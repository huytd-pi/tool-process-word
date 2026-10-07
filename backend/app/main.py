import os
import re
import shutil
import urllib.parse
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .schemas import (
    ConvertRequest,
    NormalizeRequest,
    NormalizeResponse,
    HealthResponse,
    DocumentSettings,
    LatexConvertRequest,
    LatexConvertResponse
)
from .html_parser import html_parser
from .math_sanitizer import math_sanitizer
from .deepseek_service import deepseek_service
from .docx_converter import docx_converter
from .utils import sanitize_filename

app = FastAPI(
    title="Word Math Converter API",
    description="Chuyển đổi bài viết từ ChatGPT, Gemini, NotebookLM sang file Word .docx với công thức OMML",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Warnings-Count", "X-Suggested-Filename"]
)

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    settings.reload_env()
    pandoc_bin = settings.get_pandoc_bin()
    pandoc_exists = bool(shutil.which(pandoc_bin) or os.path.exists(pandoc_bin))
    return HealthResponse(
        status="ok",
        pandoc_available=pandoc_exists,
        pandoc_path=pandoc_bin,
        deepseek_configured=deepseek_service.is_configured(),
        deepseek_model=deepseek_service.model
    )

@app.post("/api/parse-html")
def parse_html_endpoint(payload: dict):
    html_content = payload.get("html", "")
    md_text, warnings = html_parser.parse_html_to_markdown(html_content)
    sanitized_md, math_warnings = math_sanitizer.sanitize(md_text)
    return {
        "markdown": sanitized_md,
        "warnings": warnings + math_warnings
    }

@app.post("/api/sanitize")
def sanitize_endpoint(payload: dict):
    raw_text = payload.get("text", "")
    sanitized_md, math_warnings = math_sanitizer.sanitize(raw_text)
    blocks = deepseek_service.parse_markdown_to_blocks(sanitized_md)
    return {
        "markdown": sanitized_md,
        "blocks": blocks,
        "warnings": math_warnings
    }

@app.post("/api/normalize", response_model=NormalizeResponse)
async def normalize_endpoint(req: NormalizeRequest):
    warnings = []
    text_to_process = req.raw_text

    # If raw_html is supplied and contains KaTeX or tables, parse it first
    if req.raw_html and ("katex" in req.raw_html.lower() or "table" in req.raw_html.lower() or "math" in req.raw_html.lower()):
        parsed_md, html_warns = html_parser.parse_html_to_markdown(req.raw_html)
        warnings.extend(html_warns)
        if parsed_md.strip():
            text_to_process = parsed_md

    # Sanitize math
    sanitized_text, math_warns = math_sanitizer.sanitize(text_to_process)
    warnings.extend(math_warns)

    # Call DeepSeek if configured via request payload or environment
    effective_key = (req.api_key or "").strip() or deepseek_service.api_key
    effective_model = (req.model or "").strip() or deepseek_service.model or "deepseek-chat"

    model_used = None
    if effective_key:
        deepseek_md, ds_warns, model_used = await deepseek_service.normalize_text(
            sanitized_text, api_key=effective_key, model=effective_model
        )
        warnings.extend(ds_warns)
        # Final sanitize check on DeepSeek output
        final_md, post_math_warns = math_sanitizer.sanitize(deepseek_md)
        warnings.extend(post_math_warns)
    else:
        final_md = sanitized_text
        warnings.append({
            "type": "api_key_not_configured",
            "message": "Chưa nhập DEEPSEEK_API_KEY. Ứng dụng đã sử dụng bộ chuẩn hóa cục bộ chuẩn xác.",
            "position": None,
            "expression": None
        })

    # Extract structured blocks for preview
    blocks = deepseek_service.parse_markdown_to_blocks(final_md)

    return NormalizeResponse(
        normalized_markdown=final_md,
        blocks=blocks,
        warnings=warnings,
        model_used=model_used,
        success=True
    )

@app.post("/api/convert")
async def convert_endpoint(req: ConvertRequest):
    md_text = req.markdown.strip()
    if not md_text:
        raise HTTPException(status_code=400, detail="Nội dung markdown không được để trống")

    try:
        docx_bytes, warnings, safe_filename = await docx_converter.convert_markdown_to_docx(
            md_text,
            req.settings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi Word: {str(e)}")

    encoded_filename = urllib.parse.quote(safe_filename)
    ascii_filename = re.sub(r'[^\x20-\x7E]+', '_', safe_filename).replace('"', '')
    if not ascii_filename.endswith(".docx"):
        ascii_filename += ".docx"
    headers = {
        "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        "X-Warnings-Count": str(len(warnings)),
        "X-Suggested-Filename": encoded_filename
    }

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )

@app.post("/api/convert-latex", response_model=LatexConvertResponse)
async def convert_latex_endpoint(req: LatexConvertRequest):
    md_text = req.markdown.strip()
    if not md_text:
        return LatexConvertResponse(latex="", filename="document.tex", warnings=[])

    try:
        latex_str, warnings, safe_filename = await docx_converter.convert_markdown_to_latex(
            md_text,
            standalone=req.standalone,
            custom_filename=req.custom_filename or ""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chuyển đổi LaTeX: {str(e)}")

    return LatexConvertResponse(
        latex=latex_str,
        filename=safe_filename,
        warnings=warnings
    )

@app.post("/api/export-latex")
async def export_latex_endpoint(req: LatexConvertRequest):
    md_text = req.markdown.strip()
    if not md_text:
        raise HTTPException(status_code=400, detail="Nội dung markdown không được để trống")

    try:
        latex_str, warnings, safe_filename = await docx_converter.convert_markdown_to_latex(
            md_text,
            standalone=req.standalone,
            custom_filename=req.custom_filename or ""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất file LaTeX: {str(e)}")

    encoded_filename = urllib.parse.quote(safe_filename)
    ascii_filename = re.sub(r'[^\x20-\x7E]+', '_', safe_filename).replace('"', '')
    if not ascii_filename.endswith(".tex"):
        ascii_filename += ".tex"

    headers = {
        "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        "X-Warnings-Count": str(len(warnings)),
        "X-Suggested-Filename": encoded_filename
    }

    return Response(
        content=latex_str.encode("utf-8"),
        media_type="application/x-tex; charset=utf-8",
        headers=headers
    )

@app.post("/api/upload")
async def upload_file_endpoint(file: UploadFile = File(...)):
    filename = file.filename or ""
    content_bytes = await file.read()
    
    try:
        content_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_text = content_bytes.decode("utf-8-sig", errors="replace")

    warnings = []
    if filename.lower().endswith(".html") or filename.lower().endswith(".htm"):
        markdown_text, html_warns = html_parser.parse_html_to_markdown(content_text)
        warnings.extend(html_warns)
    else:
        markdown_text = content_text

    sanitized_md, math_warns = math_sanitizer.sanitize(markdown_text)
    warnings.extend(math_warns)

    return {
        "filename": filename,
        "markdown": sanitized_md,
        "warnings": warnings
    }

# Mount static frontend build if it exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

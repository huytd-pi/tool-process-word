import os
import shutil
import tempfile
import subprocess
from typing import Tuple, List
from .config import settings
from .schemas import DocumentSettings, WarningItem
from .math_sanitizer import math_sanitizer
from .utils import sanitize_filename, extract_title_from_markdown, process_images_in_markdown
from .docx_enhancer import docx_enhancer

class DocxConverter:
    """
    Orchestrates the conversion pipeline:
    Markdown/LaTeX -> Sanitization -> Image Extraction -> Pandoc OMML -> Python-docx Enhancement -> DOCX Bytes.
    """

    async def convert_markdown_to_docx(
        self,
        markdown_text: str,
        doc_settings: DocumentSettings
    ) -> Tuple[bytes, List[WarningItem], str]:
        warnings: List[WarningItem] = []
        
        # 1. Sanitize math and collect formula warnings
        clean_md, math_warnings = math_sanitizer.sanitize(markdown_text)
        warnings.extend(math_warnings)

        # 2. Determine title and filename
        title = doc_settings.document_title or extract_title_from_markdown(clean_md)
        filename = doc_settings.custom_filename or title
        safe_filename = sanitize_filename(filename)

        # 3. Create isolated temporary directory
        temp_dir = tempfile.mkdtemp(prefix="doc_conv_")
        try:
            # 4. Process images (base64 data URLs & remote URLs)
            final_md, img_warnings = await process_images_in_markdown(clean_md, temp_dir)
            warnings.extend(img_warnings)

            # 5. Write markdown input file
            input_md_path = os.path.join(temp_dir, "input.md")
            with open(input_md_path, "w", encoding="utf-8") as f:
                f.write(final_md)

            # 6. Run Pandoc
            pandoc_bin = settings.get_pandoc_bin()
            output_docx_path = os.path.join(temp_dir, "output.docx")

            cmd = [
                pandoc_bin,
                input_md_path,
                "-o", output_docx_path,
                "-f", "markdown+tex_math_dollars+tex_math_single_backslash+tex_math_double_backslash+raw_tex+table_captions+smart",
                "-t", "docx",
                "--highlight-style=tango"
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if process.returncode != 0:
                err_stderr = process.stderr.strip()
                raise RuntimeError(f"Lỗi Pandoc ({process.returncode}): {err_stderr}")

            if not os.path.exists(output_docx_path):
                raise FileNotFoundError("Pandoc không tạo được file output.docx")

            # 7. Post-process and enhance DOCX with python-docx
            docx_enhancer.enhance(output_docx_path, doc_settings)

            # 8. Read final file bytes
            with open(output_docx_path, "rb") as f:
                docx_bytes = f.read()

            return docx_bytes, warnings, safe_filename

        finally:
            # Clean up temporary directory and files
            shutil.rmtree(temp_dir, ignore_errors=True)

docx_converter = DocxConverter()

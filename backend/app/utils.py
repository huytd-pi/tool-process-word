import os
import re
import base64
import uuid
from typing import Tuple, List
import httpx
from .schemas import WarningItem

def sanitize_filename(name: str) -> str:
    """Removes illegal filesystem characters and cleans up filename for download."""
    if not name:
        return "document_export.docx"
    # Remove invalid characters for Windows and Unix
    clean = re.sub(r'[\\/*?:"<>|\r\n\t]', "", name)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        clean = "document_export"
    if not clean.lower().endswith(".docx"):
        clean += ".docx"
    # Cap length to 80 characters (excluding .docx)
    base, ext = os.path.splitext(clean)
    if len(base) > 80:
        base = base[:80].strip()
    return base + ext

def extract_title_from_markdown(md_text: str) -> str:
    """Extracts first H1 or title from markdown, defaults to 'Tài liệu Word'."""
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            # Clean up markdown formatting in title if any
            title = re.sub(r"[*_`]", "", title)
            if title:
                return title
    # Fallback to first non-empty line under 60 chars
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("|", "```", "$", "!", "-", "*", "1.")):
            clean = re.sub(r"[*_`]", "", stripped)
            if 3 <= len(clean) <= 60:
                return clean
    return "Tai_Lieu_Khoa_Hoc"

async def process_images_in_markdown(md_text: str, temp_dir: str) -> Tuple[str, List[WarningItem]]:
    """
    Downloads remote images and decodes base64 data URLs in markdown,
    saving them as local image files in temp_dir for Pandoc to embed.
    """
    warnings: List[WarningItem] = []
    
    # 1. Handle base64 Data URLs: ![alt](data:image/png;base64,...)
    def replace_data_url(match):
        alt = match.group(1)
        mime = match.group(2)
        b64data = match.group(3)
        ext = "png"
        if "jpeg" in mime or "jpg" in mime:
            ext = "jpg"
        elif "gif" in mime:
            ext = "gif"
        elif "webp" in mime:
            ext = "webp"

        filename = f"img_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = os.path.join(temp_dir, filename)

        try:
            img_bytes = base64.b64decode(b64data)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            # Use forward slashes for Pandoc compatibility on Windows
            return f"![{alt}]({filepath.replace(os.sep, '/')})"
        except Exception as e:
            warnings.append(WarningItem(
                type="image_decode_error",
                message=f"Không thể giải mã ảnh base64: {str(e)}"
            ))
            return f"*[Hình ảnh base64 không hợp lệ]*"

    # Regex for markdown data url: ![alt](data:image/{mime};base64,{data})
    processed = re.sub(
        r"!\[(.*?)\]\(data:image/([a-zA-Z0-9\+\-]+);base64,([a-zA-Z0-9\+/=]+)\)",
        replace_data_url,
        md_text
    )

    # 2. Handle remote image URLs: ![alt](http://... or https://...)
    remote_matches = list(re.finditer(r"!\[(.*?)\]\((https?://[^\s\)]+)\)", processed))
    if remote_matches:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for match in remote_matches:
                alt = match.group(1)
                url = match.group(2)
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "")
                        ext = "png"
                        if "jpeg" in content_type or "jpg" in content_type:
                            ext = "jpg"
                        elif "gif" in content_type:
                            ext = "gif"
                        elif "webp" in content_type:
                            ext = "webp"
                        
                        filename = f"remote_{uuid.uuid4().hex[:8]}.{ext}"
                        filepath = os.path.join(temp_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(resp.content)
                        local_path = filepath.replace(os.sep, "/")
                        processed = processed.replace(match.group(0), f"![{alt}]({local_path})")
                    else:
                        warnings.append(WarningItem(
                            type="image_download_failed",
                            message=f"Không thể tải ảnh từ liên kết (HTTP {resp.status_code}): {url[:60]}"
                        ))
                        processed = processed.replace(match.group(0), f"*[Không thể tải ảnh: {url[:50]}...]*")
                except Exception as e:
                    warnings.append(WarningItem(
                        type="image_download_exception",
                        message=f"Lỗi khi tải ảnh từ {url[:40]}: {str(e)}"
                    ))
                    processed = processed.replace(match.group(0), f"*[Lỗi tải ảnh: {url[:50]}...]*")

    return processed, warnings

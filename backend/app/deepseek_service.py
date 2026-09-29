import os
import re
import json
from typing import Tuple, List, Optional
import httpx
from .config import settings
from .schemas import BlockItem, StructuredDocument, WarningItem

SYSTEM_PROMPT = """Bạn là một chuyên gia chuẩn hóa cấu trúc văn bản học thuật và khoa học.
Nhiệm vụ của bạn là nhận nội dung sao chép từ các AI (ChatGPT, Gemini, NotebookLM) có thể bị mất cấu trúc hoặc xáo trộn định dạng, và chuẩn hóa nó về Markdown chuẩn với công thức toán học LaTeX ($...$ và $$...$$).

CÁC NGUYÊN TẮC BẮT BUỘC TUÂN THỦ:
1. BẢO TOÀN NGUYÊN VĂN (ABSOLUTE VERBATIM): Giữ nguyên 100% từ ngữ, câu chữ, biến số, số liệu, tên gọi, công thức và bảng biểu. TUYỆT ĐỐI KHÔNG tóm tắt, KHÔNG diễn giải lại, KHÔNG viết lại câu văn, KHÔNG bổ sung kiến thức ngoài, KHÔNG thêm lời chào hay kết bài.
2. BẢO TOÀN CÔNG THỨC TOÁN & KHOA HỌC:
   - Giữ nguyên toàn bộ giá trị số, số mũ, chỉ số trên/dưới, dấu âm/dương, biến số, ký tự Hy Lạp.
   - Chuẩn hóa công thức trong dòng về dạng: $biểu thức$
   - Chuẩn hóa công thức độc lập (khối) về dạng:
     $$
     biểu thức
     $$
   - Đối với hệ phương trình, ma trận hoặc phương trình nhiều dòng, dùng các môi trường chuẩn: aligned, matrix, bmatrix, pmatrix, cases.
3. KHỐI MÃ (CODE):
   - Đặt trong khối mã ```tên_ngôn_ngữ ... ```.
   - TUYỆT ĐỐI KHÔNG chuyển khối mã lập trình thành công thức toán.
4. BẢNG BIỂU (TABLE):
   - Chuẩn hóa bảng về Markdown chuẩn (| Cột 1 | Cột 2 | ... | kèm dòng ngăn cách | --- | --- |).
5. ĐỀ MỤC & DANH SÁCH:
   - Dùng #, ##, ### cho các cấp đề mục tương ứng.
   - Dùng - cho danh sách không thứ tự, 1., 2. cho danh sách có thứ tự.
6. ĐẦU RA:
   - Trả về DUY NHẤT nội dung Markdown đã chuẩn hóa, không có bất kỳ lời dẫn hay ghi chú trò chuyện nào.
"""

class DeepSeekService:
    @property
    def api_key(self) -> str:
        return settings.DEEPSEEK_API_KEY

    @property
    def base_url(self) -> str:
        return settings.DEEPSEEK_BASE_URL.rstrip("/")

    @property
    def model(self) -> str:
        return settings.DEEPSEEK_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def normalize_text(
        self,
        text: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Tuple[str, List[WarningItem], Optional[str]]:
        warnings: List[WarningItem] = []
        effective_key = (api_key or self.api_key or "").strip()
        effective_model = (model or self.model or "deepseek-chat").strip()

        if not effective_key:
            warnings.append(WarningItem(
                type="api_key_missing",
                message="Chưa cung cấp DeepSeek API Key. Ứng dụng đã sử dụng bộ chuẩn hóa cục bộ chuẩn xác."
            ))
            return text, warnings, None

        if not text or not text.strip():
            return "", warnings, effective_model

        # Chunk if text is too long (over ~8000 characters)
        chunks = self._chunk_text(text, max_chunk_chars=8000)
        normalized_chunks = []

        async with httpx.AsyncClient(timeout=90.0) as client:
            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                try:
                    chunk_result = await self._call_deepseek_api(
                        client, chunk, api_key=effective_key, model=effective_model
                    )
                    normalized_chunks.append(chunk_result)
                except httpx.HTTPStatusError as e:
                    err_msg = f"DeepSeek API trả về lỗi HTTP {e.response.status_code}: {e.response.text[:200]}"
                    warnings.append(WarningItem(type="api_error", message=err_msg))
                    # Fallback to original chunk
                    normalized_chunks.append(chunk)
                except httpx.TimeoutException:
                    err_msg = f"Quá thời gian chờ phản hồi DeepSeek API (phần {idx+1}/{len(chunks)}). Đang giữ nguyên phần này."
                    warnings.append(WarningItem(type="api_timeout", message=err_msg))
                    normalized_chunks.append(chunk)
                except Exception as e:
                    err_msg = f"Lỗi kết nối DeepSeek: {str(e)}"
                    warnings.append(WarningItem(type="api_exception", message=err_msg))
                    normalized_chunks.append(chunk)

        merged = "\n\n".join(normalized_chunks)
        return merged, warnings, effective_model

    async def _call_deepseek_api(
        self,
        client: httpx.AsyncClient,
        content: str,
        api_key: str,
        model: str
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Chuẩn hóa cấu trúc văn bản sau:\n\n{content}"}
            ],
            "temperature": 0.1,  # Low temperature for strict verbatim adherence
            "stream": False
        }

        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError("DeepSeek phản hồi rỗng không có nội dung choices")

        result = choices[0].get("message", {}).get("content", "")
        # Strip potential markdown fences wrapping the whole output if present
        result = re.sub(r"^```markdown\s*", "", result.strip(), flags=re.I)
        result = re.sub(r"\s*```$", "", result)
        return result.strip()

    def _chunk_text(self, text: str, max_chunk_chars: int = 8000) -> List[str]:
        """
        Splits text along logical section boundaries (# or ## or double newlines)
        without cutting across math blocks ($$..$$), tables (|..|), or code blocks (```..```).
        """
        if len(text) <= max_chunk_chars:
            return [text]

        lines = text.split("\n")
        chunks: List[str] = []
        current_chunk_lines: List[str] = []
        current_chars = 0
        in_code_block = False
        in_display_math = False

        for line in lines:
            line_stripped = line.strip()

            # Track code block fence
            if line_stripped.startswith("```"):
                in_code_block = not in_code_block

            # Track display math fence
            if line_stripped.startswith("$$"):
                in_display_math = not in_display_math

            # Check if this is a safe split point
            is_heading = line_stripped.startswith("#") and not in_code_block and not in_display_math
            is_empty_line = line_stripped == "" and not in_code_block and not in_display_math

            can_split = not in_code_block and not in_display_math

            if can_split and current_chars >= max_chunk_chars and (is_heading or is_empty_line):
                chunks.append("\n".join(current_chunk_lines))
                current_chunk_lines = [line]
                current_chars = len(line) + 1
            else:
                current_chunk_lines.append(line)
                current_chars += len(line) + 1

        if current_chunk_lines:
            chunks.append("\n".join(current_chunk_lines))

        return chunks

    def parse_markdown_to_blocks(self, md_text: str) -> List[BlockItem]:
        """Parses normalized Markdown into structured BlockItem objects."""
        blocks: List[BlockItem] = []
        lines = md_text.split("\n")
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # Heading
            if stripped.startswith("#"):
                match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
                if match:
                    level = len(match.group(1))
                    content = match.group(2)
                    blocks.append(BlockItem(type="heading", level=level, content=content))
                    i += 1
                    continue

            # Fenced Code Block
            if stripped.startswith("```"):
                lang = stripped[3:].strip()
                code_lines = []
                i += 1
                while i < n and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1 # skip closing ```
                blocks.append(BlockItem(type="code", language=lang, content="\n".join(code_lines)))
                continue

            # Display Math Block $$ ... $$
            if stripped.startswith("$$"):
                math_lines = []
                # Check if single line $$...$$
                if stripped.endswith("$$") and len(stripped) > 2:
                    content = stripped[2:-2].strip()
                    blocks.append(BlockItem(type="math", content=content, display=True))
                    i += 1
                    continue
                i += 1
                while i < n and not lines[i].strip().startswith("$$"):
                    math_lines.append(lines[i])
                    i += 1
                i += 1 # skip closing $$
                blocks.append(BlockItem(type="math", content="\n".join(math_lines).strip(), display=True))
                continue

            # Table
            if stripped.startswith("|") and stripped.endswith("|"):
                table_lines = [stripped]
                i += 1
                while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                headers, rows = self._parse_md_table(table_lines)
                blocks.append(BlockItem(type="table", headers=headers, rows=rows))
                continue

            # List
            if re.match(r"^(\*|-|\+|\d+\.)\s+", stripped):
                is_ordered = bool(re.match(r"^\d+\.\s+", stripped))
                list_items = []
                while i < n and re.match(r"^(\*|-|\+|\d+\.)\s+", lines[i].strip()):
                    item_text = re.sub(r"^(\*|-|\+|\d+\.)\s+", "", lines[i].strip())
                    list_items.append(item_text)
                    i += 1
                blocks.append(BlockItem(type="list", ordered=is_ordered, items=list_items))
                continue

            # Blockquote
            if stripped.startswith(">"):
                quote_lines = []
                while i < n and lines[i].strip().startswith(">"):
                    quote_lines.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                blocks.append(BlockItem(type="quote", content="\n".join(quote_lines)))
                continue

            # Image ![alt](src)
            img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", stripped)
            if img_match:
                blocks.append(BlockItem(type="image", alt=img_match.group(1), src=img_match.group(2)))
                i += 1
                continue

            # Paragraph (accumulate until empty line or next block)
            p_lines = [stripped]
            i += 1
            while i < n:
                next_l = lines[i].strip()
                if not next_l or next_l.startswith("#") or next_l.startswith("```") or next_l.startswith("$$") or next_l.startswith("|") or re.match(r"^(\*|-|\+|\d+\.)\s+", next_l) or next_l.startswith(">"):
                    break
                p_lines.append(next_l)
                i += 1
            blocks.append(BlockItem(type="paragraph", content=" ".join(p_lines)))

        return blocks

    def _parse_md_table(self, lines: List[str]) -> Tuple[List[str], List[List[str]]]:
        if not lines:
            return [], []
        
        def split_row(line: str) -> List[str]:
            cells = line.strip("|").split("|")
            return [c.strip() for c in cells]

        headers = split_row(lines[0])
        rows = []
        start_idx = 1
        # Skip separator line like | --- | --- |
        if len(lines) > 1 and re.match(r"^\|(\s*:?-+:?\s*\|)+$", lines[1].strip()):
            start_idx = 2

        for l in lines[start_idx:]:
            rows.append(split_row(l))
        return headers, rows

deepseek_service = DeepSeekService()

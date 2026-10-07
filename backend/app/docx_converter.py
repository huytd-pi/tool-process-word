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

    async def convert_markdown_to_latex(
        self,
        markdown_text: str,
        standalone: bool = True,
        custom_filename: str = ""
    ) -> Tuple[str, List[WarningItem], str]:
        warnings: List[WarningItem] = []
        clean_md, math_warnings = math_sanitizer.sanitize(markdown_text)
        warnings.extend(math_warnings)

        title = extract_title_from_markdown(clean_md)
        filename = custom_filename or title
        safe_filename = sanitize_filename(filename)
        if not safe_filename.endswith(".tex"):
            safe_filename += ".tex"

        temp_dir = tempfile.mkdtemp(prefix="latex_conv_")
        try:
            final_md, img_warnings = await process_images_in_markdown(clean_md, temp_dir)
            warnings.extend(img_warnings)

            input_md_path = os.path.join(temp_dir, "input.md")
            with open(input_md_path, "w", encoding="utf-8") as f:
                f.write(final_md)

            pandoc_bin = settings.get_pandoc_bin()
            cmd = [
                pandoc_bin,
                input_md_path,
                "-f", "markdown+tex_math_dollars+tex_math_single_backslash+tex_math_double_backslash+raw_tex+table_captions+smart",
                "-t", "latex",
            ]
            if standalone:
                cmd.append("--standalone")

            latex_content = ""
            try:
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30
                )
                if process.returncode == 0:
                    latex_content = process.stdout
                else:
                    err_msg = process.stderr.strip()[:200]
                    warnings.append(WarningItem(
                        type="pandoc_latex_warning",
                        message=f"Pandoc cảnh báo khi xuất LaTeX: {err_msg}",
                        position=None,
                        expression=None
                    ))
                    # If stdout has content despite warnings, use it
                    if process.stdout.strip():
                        latex_content = process.stdout
            except Exception as pe:
                warnings.append(WarningItem(
                    type="pandoc_not_available",
                    message=f"Không thể chạy Pandoc ({str(pe)}), sử dụng bộ xuất LaTeX cục bộ.",
                    position=None,
                    expression=None
                ))

            if not latex_content.strip():
                latex_content = self._fallback_markdown_to_latex(final_md, title=title, standalone=standalone)

            return latex_content, warnings, safe_filename
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _fallback_markdown_to_latex(self, md_text: str, title: str = "", standalone: bool = True) -> str:
        """
        Lightweight fallback converting Markdown + LaTeX equations to a LaTeX document
        when Pandoc is not reachable.
        """
        import re

        body_lines = []
        in_code_block = False
        code_lang = ""

        for line in md_text.splitlines():
            # Code block check
            if line.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_lang = line[3:].strip()
                    body_lines.append(r"\begin{verbatim}")
                else:
                    in_code_block = False
                    body_lines.append(r"\end{verbatim}")
                continue

            if in_code_block:
                body_lines.append(line)
                continue

            # Headings
            if re.match(r"^#\s+(.+)$", line):
                h = re.sub(r"^#\s+", "", line)
                body_lines.append(f"\\section{{{h}}}")
            elif re.match(r"^##\s+(.+)$", line):
                h = re.sub(r"^##\s+", "", line)
                body_lines.append(f"\\subsection{{{h}}}")
            elif re.match(r"^###\s+(.+)$", line):
                h = re.sub(r"^###\s+", "", line)
                body_lines.append(f"\\subsubsection{{{h}}}")
            elif re.match(r"^####\s+(.+)$", line):
                h = re.sub(r"^####\s+", "", line)
                body_lines.append(f"\\paragraph{{{h}}}")
            elif re.match(r"^>\s+(.+)$", line):
                q = re.sub(r"^>\s+", "", line)
                body_lines.append(f"\\begin{{quote}}\n{q}\n\\end{{quote}}")
            elif re.match(r"^\s*-\s+(.+)$", line):
                item = re.sub(r"^\s*-\s+", "", line)
                body_lines.append(f"\\item {item}")
            else:
                # Display math $$ ... $$
                if line.strip().startswith("$$") and line.strip().endswith("$$"):
                    eq = line.strip()[2:-2].strip()
                    body_lines.append(f"\\[\n{eq}\n\\]")
                else:
                    # Replace bold and italic
                    l = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", line)
                    l = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", l)
                    body_lines.append(l)

        body = "\n".join(body_lines)

        if not standalone:
            return body

        tex_title = title or "Document"
        return f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[vietnamese]{{babel}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=2.54cm}}

\\title{{{tex_title}}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

{body}

\\end{{document}}
"""

docx_converter = DocxConverter()

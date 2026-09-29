import re
from typing import Tuple, List
from bs4 import BeautifulSoup, Tag, NavigableString
from .schemas import WarningItem

class HTMLContentParser:
    """
    Parses rich HTML copied from ChatGPT, Gemini, NotebookLM, or general web pages
    into clean Markdown with LaTeX math ($...$ and $$...$$).
    Handles KaTeX, MathJax, MathML, tables, code blocks, lists, and images.
    """

    def parse_html_to_markdown(self, html_str: str) -> Tuple[str, List[WarningItem]]:
        warnings: List[WarningItem] = []
        if not html_str or not html_str.strip():
            return "", warnings

        # Clean CF_HTML headers and fragment markers
        html_str = re.sub(
            r"Version:\d+(?:\.\d+)?\s*StartHTML:\d+\s*EndHTML:\d+\s*StartFragment:\d+\s*EndFragment:\d+\s*",
            "",
            html_str,
            flags=re.IGNORECASE
        )
        html_str = re.sub(r"(?:<!--\s*)?StartFragment(?:\s*-->)?", "", html_str, flags=re.IGNORECASE)
        html_str = re.sub(r"(?:<!--\s*)?EndFragment(?:\s*-->)?", "", html_str, flags=re.IGNORECASE)

        soup = BeautifulSoup(html_str, "html.parser")

        # 1. Clean up known UI noise (e.g. ChatGPT copy buttons, svgs, header actions)
        for noise in soup.find_all(["button", "svg"]):
            noise.decompose()
        for noise in soup.find_all(class_=re.compile(r"(copy-button|clipboard|btn-copy|sr-only)", re.I)):
            noise.decompose()

        # 2. Process KaTeX elements
        # ChatGPT / NotebookLM KaTeX:
        # Display math usually has parent with class 'katex-display' or is a <div>
        # Look for katex-display containers first
        # 2. Process Display Math elements (KaTeX display, MathJax display, Gemini math-block)
        for kd in soup.find_all(class_=re.compile(r"(katex-display|math-display|display-math|math-block)", re.I)):
            tex_annot = kd.find("annotation", encoding=re.compile(r"tex", re.I))
            if tex_annot and tex_annot.string:
                clean_tex = tex_annot.string.strip()
                kd.replace_with(f"\n\n$$\n{clean_tex}\n$$\n\n")
            elif kd.get("data-latex") or kd.get("data-tex"):
                clean_tex = (kd.get("data-latex") or kd.get("data-tex", "")).strip()
                kd.replace_with(f"\n\n$$\n{clean_tex}\n$$\n\n")
            else:
                math_tag = kd.find("math")
                if math_tag and math_tag.get("alttext"):
                    kd.replace_with(f"\n\n$$\n{math_tag['alttext'].strip()}\n$$\n\n")

        # 3. Process Inline Math elements (KaTeX inline, Gemini math-inline, general math spans)
        for k in soup.find_all(class_=re.compile(r"(\bkatex\b|math-inline|inline-math)", re.I)):
            if not k.parent:
                continue
            tex_annot = k.find("annotation", encoding=re.compile(r"tex", re.I))
            if tex_annot and tex_annot.string:
                clean_tex = re.sub(r"\s+", " ", tex_annot.string.strip())
                k.replace_with(f"${clean_tex}$")
            elif k.get("data-latex") or k.get("data-tex"):
                clean_tex = re.sub(r"\s+", " ", (k.get("data-latex") or k.get("data-tex", "")).strip())
                k.replace_with(f"${clean_tex}$")
            else:
                math_tag = k.find("math")
                if math_tag and math_tag.get("alttext"):
                    clean_tex = re.sub(r"\s+", " ", math_tag["alttext"].strip())
                    k.replace_with(f"${clean_tex}$")

        # 4. Process MathJax elements
        for mjx in soup.find_all(class_=re.compile(r"MathJax", re.I)):
            tex_script = mjx.find("script", type=re.compile(r"math/tex", re.I))
            if tex_script and tex_script.string:
                tex = tex_script.string.strip()
                if "mode=display" in tex_script.get("type", ""):
                    mjx.replace_with(f"\n\n$$\n{tex}\n$$\n\n")
                else:
                    clean_tex = re.sub(r"\s+", " ", tex)
                    mjx.replace_with(f"${clean_tex}$")
            elif mjx.get("data-mathml"):
                clean_tex = re.sub(r"\s+", " ", mjx.get_text().strip())
                mjx.replace_with(f"${clean_tex}$")

        # 5. Standalone MathML <math>
        for m in soup.find_all("math"):
            if not m.parent:
                continue
            is_display = m.get("display") == "block" or m.get("mode") == "display"
            alt = m.get("alttext") or m.get("alt")
            if alt:
                tex = alt.strip()
                if is_display:
                    m.replace_with(f"\n\n$$\n{tex}\n$$\n\n")
                else:
                    clean_tex = re.sub(r"\s+", " ", tex)
                    m.replace_with(f"${clean_tex}$")

        # 4. Process Code Blocks (<pre><code>)
        for pre in soup.find_all("pre"):
            code_tag = pre.find("code")
            code_text = code_tag.get_text() if code_tag else pre.get_text()
            lang = ""
            if code_tag and code_tag.get("class"):
                for cls in code_tag.get("class"):
                    if cls.startswith("language-") or cls.startswith("lang-"):
                        lang = cls.split("-", 1)[1]
                        break
            # Ensure code text ends with newline
            code_text = code_text.rstrip("\n")
            pre.replace_with(f"\n\n```{lang}\n{code_text}\n```\n\n")

        # 5. Process Tables
        for table in soup.find_all("table"):
            table_md = self._table_to_markdown(table)
            table.replace_with(f"\n\n{table_md}\n\n")

        # 6. Process Headings
        for i in range(1, 7):
            for h in soup.find_all(f"h{i}"):
                text = self._inline_to_markdown(h).strip()
                prefix = "#" * i
                h.replace_with(f"\n\n{prefix} {text}\n\n")

        # 7. Process Blockquotes
        for bq in soup.find_all("blockquote"):
            bq_text = self._inline_to_markdown(bq).strip()
            lines = [f"> {line}" for line in bq_text.splitlines() if line.strip()]
            bq.replace_with(f"\n\n{chr(10).join(lines)}\n\n")

        # 8. Process Lists
        for ul in soup.find_all(["ul", "ol"]):
            # Only top-level lists here; nested ones handled inside
            if not ul.find_parent(["ul", "ol"]):
                list_md = self._list_to_markdown(ul, depth=0)
                ul.replace_with(f"\n\n{list_md}\n\n")

        # 9. Process Images
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "image")
            img.replace_with(f"![{alt}]({src})")

        # 10. Process Remaining Paragraphs & Divs
        for p in soup.find_all(["p", "div"]):
            p_text = self._inline_to_markdown(p).strip()
            if p_text:
                p.replace_with(f"\n\n{p_text}\n\n")

        # Convert remaining inline elements
        markdown = self._inline_to_markdown(soup)

        # Cleanup excess whitespace
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        
        # Apply math sanitization on parsed markdown
        from .math_sanitizer import math_sanitizer
        sanitized_md, math_warns = math_sanitizer.sanitize(markdown.strip())
        warnings.extend(math_warns)
        return sanitized_md, warnings

    def _inline_to_markdown(self, element: Tag) -> str:
        """Recursively formats inline formatting like bold, italic, links, etc."""
        if isinstance(element, NavigableString):
            return str(element)

        result = []
        for child in element.children:
            if isinstance(child, NavigableString):
                result.append(str(child))
            elif isinstance(child, Tag):
                tag_name = child.name.lower()
                child_content = self._inline_to_markdown(child)

                if tag_name in ["strong", "b"]:
                    result.append(f"**{child_content}**")
                elif tag_name in ["em", "i"]:
                    result.append(f"*{child_content}*")
                elif tag_name in ["del", "s", "strike"]:
                    result.append(f"~~{child_content}~~")
                elif tag_name == "code":
                    result.append(f"`{child_content}`")
                elif tag_name == "sup":
                    result.append(f"^{child_content}^")
                elif tag_name == "sub":
                    result.append(f"~{child_content}~")
                elif tag_name == "a":
                    href = child.get("href", "#")
                    result.append(f"[{child_content}]({href})")
                elif tag_name == "br":
                    result.append("\n")
                elif tag_name == "hr":
                    result.append("\n---\n")
                else:
                    result.append(child_content)
        return "".join(result)

    def _table_to_markdown(self, table: Tag) -> str:
        """Converts HTML table element to Markdown table string."""
        rows_data: List[List[str]] = []
        for tr in table.find_all("tr"):
            row: List[str] = []
            for cell in tr.find_all(["th", "td"]):
                cell_text = self._inline_to_markdown(cell).strip()
                cell_text = cell_text.replace("\n", " ").replace("|", "\\|")
                row.append(cell_text)
            if row:
                rows_data.append(row)

        if not rows_data:
            return ""

        # Normalize column count across all rows
        max_cols = max(len(r) for r in rows_data)
        for r in rows_data:
            while len(r) < max_cols:
                r.append("")

        header = rows_data[0]
        md_lines = []
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")

        for row in rows_data[1:]:
            md_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(md_lines)

    def _list_to_markdown(self, list_tag: Tag, depth: int = 0) -> str:
        """Recursively converts nested HTML lists to Markdown list with proper indentation."""
        lines = []
        is_ordered = list_tag.name.lower() == "ol"
        idx = 1
        indent = "  " * depth

        for child in list_tag.find_all("li", recursive=False):
            # Extract child content without child sub-lists
            sub_lists = child.find_all(["ul", "ol"], recursive=False)
            
            # Temporary detach sub-lists to get li text cleanly
            sub_list_tags = []
            for sl in sub_lists:
                sub_list_tags.append(sl.extract())

            li_text = self._inline_to_markdown(child).strip()
            marker = f"{idx}." if is_ordered else "-"
            lines.append(f"{indent}{marker} {li_text}")
            idx += 1

            # Process nested lists
            for sl in sub_list_tags:
                lines.append(self._list_to_markdown(sl, depth=depth + 1))

        return "\n".join(lines)

html_parser = HTMLContentParser()

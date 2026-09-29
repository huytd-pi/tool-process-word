import re
from typing import Tuple, List, Dict
from .schemas import WarningItem

class MathSanitizer:
    """
    Normalizes and validates mathematical formulas in Markdown/LaTeX.
    - Converts \\( ... \\) and \\\\( ... \\\\) to $ ... $
    - Converts \\[ ... \\] and \\\\[ ... \\\\] to $$ ... $$
    - Converts inline $$ ... $$ within text sentences to $ ... $
    - Normalizes inline math interior whitespace ($ x $ -> $x$, multiline -> singleline)
    - Ensures boundary word spacing without altering punctuation ($x$, ($x$), chữ $x$ này)
    - Shields code blocks from math delimiter replacement
    - Normalizes align/align* to aligned for OMML compatibility
    - Validates LaTeX syntax (braces, environments)
    - Emits warnings for malformed formulas while preserving original text
    """

    def sanitize(self, text: str) -> Tuple[str, List[WarningItem]]:
        warnings: List[WarningItem] = []
        if not text:
            return "", warnings

        # 0. Clean Windows Clipboard CF_HTML fragment markers and metadata
        text = re.sub(
            r"Version:\d+(?:\.\d+)?\s*StartHTML:\d+\s*EndHTML:\d+\s*StartFragment:\d+\s*EndFragment:\d+\s*",
            "",
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(r"(?:<!--\s*)?StartFragment(?:\s*-->)?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"(?:<!--\s*)?EndFragment(?:\s*-->)?", "", text, flags=re.IGNORECASE)

        # 1. Shield code blocks and inline code
        code_shield_map: Dict[str, str] = {}
        shield_counter = 0

        def shield_block_code(match):
            nonlocal shield_counter
            key = f"__CODE_BLOCK_SHIELD_{shield_counter}__"
            shield_counter += 1
            code_shield_map[key] = match.group(0)
            return key

        def shield_inline_code(match):
            nonlocal shield_counter
            key = f"__INLINE_CODE_SHIELD_{shield_counter}__"
            shield_counter += 1
            code_shield_map[key] = match.group(0)
            return key

        processed = re.sub(r"```[\s\S]*?```", shield_block_code, text)
        processed = re.sub(r"`[^`\n]+`", shield_inline_code, processed)

        # 2. Normalize LaTeX display math: \[ ... \] and \\[ ... \\]
        processed = re.sub(
            r"(?:\\\\|\\)\[([\s\S]*?)(?:\\\\|\\)\]",
            lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n",
            processed
        )

        # 3. Normalize LaTeX inline math: \( ... \) and \\( ... \\)
        def fix_latex_inline(m):
            inner = m.group(1).strip()
            inner = re.sub(r"\s+", " ", inner)
            return f"${inner}$"

        processed = re.sub(r"(?:\\\\|\\)\(([\s\S]*?)(?:\\\\|\\)\)", fix_latex_inline, processed)

        # 4. Handle inline $$ ... $$ embedded in text sentences
        # If $$expr$$ is on the same line with other text, convert it to inline $expr$
        def fix_inline_double_dollar(m):
            inner = m.group(1).strip()
            clean_inner = re.sub(r"\s+", " ", inner)
            return f"${clean_inner}$"

        # Match single-line $$...$$ that has non-newline text around it on the same line
        processed = re.sub(r"(?<=[^\n\$])\$\$([^\$\n]+?)\$\$(?=[^\n\$])", fix_inline_double_dollar, processed)

        # 5. Shield genuine display math $$ ... $$ before processing inline math
        display_shield_map: Dict[str, str] = {}
        display_counter = 0

        def shield_display_math(match):
            nonlocal display_counter
            key = f"__DISPLAY_MATH_SHIELD_{display_counter}__"
            display_counter += 1
            content = match.group(1).strip()
            # Standardize align* / align inside display math to aligned
            fixed = re.sub(r"\\begin\{(?:align\*?|eqnarray\*?)\}", r"\\begin{aligned}", content)
            fixed = re.sub(r"\\end\{(?:align\*?|eqnarray\*?)\}", r"\\end{aligned}", fixed)
            display_shield_map[key] = f"\n\n$$\n{fixed}\n$$\n\n"
            return key

        processed = re.sub(r"\$\$([\s\S]*?)\$\$", shield_display_math, processed)

        # 6. Check for standalone \begin{equation} or \begin{align} without $$
        def wrap_standalone_env(match):
            env_name = match.group(1)
            content = match.group(2).strip()
            if env_name in ["align", "align*", "eqnarray", "eqnarray*"]:
                return f"\n\n$$\n\\begin{{aligned}}\n{content}\n\\end{{aligned}}\n$$\n\n"
            return f"\n\n$$\n\\begin{{{env_name}}}\n{content}\n\\end{{{env_name}}}\n$$\n\n"

        processed = re.sub(
            r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|aligned)\}([\s\S]*?)\\end\{\1\}",
            wrap_standalone_env,
            processed
        )

        # 7. Clean up inline math $ ... $
        # - Strips internal leading/trailing whitespace ($ x $ -> $x$)
        # - Collapses internal line breaks into single space ($f(x) =\n 1$ -> $f(x) = 1$)
        # - Adds word boundary spacing (chữ$x$này -> chữ $x$ này)
        # - Preserves punctuation untouched ($x$, ($x$), [$x$])
        # - Avoids matching currency ($100, $5.50, $10k, $50 USD)
        word_chars_re = re.compile(r"^[a-zA-Z0-9\u00C0-\u024F\u1EA0-\u1EF9]$")

        def clean_inline_dollar(m):
            inner = m.group(1).strip()
            # Ignore currency patterns like $100 or $5.50
            if re.match(r"^\d+([.,]\d+)?(\s*(USD|VND|k|m|b|đ|triệu|nghìn))?$", inner, re.I):
                return m.group(0)

            clean_inner = re.sub(r"\s+", " ", inner)

            # Check boundary characters in the surrounding string
            start_idx = m.start()
            end_idx = m.end()
            before_char = processed[start_idx - 1] if start_idx > 0 else ""
            after_char = processed[end_idx] if end_idx < len(processed) else ""

            lead_space = " " if word_chars_re.match(before_char) else ""
            trail_space = " " if word_chars_re.match(after_char) else ""

            return f"{lead_space}${clean_inner}${trail_space}"

        processed = re.sub(
            r"(?<!\$)\$(?!\$)\s*([^\$\n]+?(?:\n[^\$\n]+?)?)\s*(?<!\$)\$(?!\$)",
            clean_inline_dollar,
            processed
        )

        # 8. Restore shielded display math blocks
        for key, display_content in display_shield_map.items():
            processed = processed.replace(key, display_content)

        # 9. Restore shielded code blocks
        for key, code_content in code_shield_map.items():
            processed = processed.replace(key, code_content)

        # 10. Clean up excessive empty lines
        processed = re.sub(r"\n{3,}", "\n\n", processed)

        # 11. Validate math equations and collect warnings
        for match in re.finditer(r"\$\$([\s\S]*?)\$\$", processed):
            expr = match.group(1).strip()
            err = self._validate_latex(expr)
            if err:
                char_idx = match.start()
                line_no = processed[:char_idx].count("\n") + 1
                warnings.append(
                    WarningItem(
                        type="display_math_warning",
                        message=f"Công thức hiển thị (dòng ~{line_no}) có thể có lỗi: {err}",
                        position=line_no,
                        expression=expr[:120]
                    )
                )

        for match in re.finditer(r"(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)", processed):
            expr = match.group(1).strip()
            if re.match(r"^\d+([.,]\d+)?(\s*(USD|VND|k|m|b|đ|triệu|nghìn))?$", expr, re.I):
                continue
            err = self._validate_latex(expr)
            if err:
                char_idx = match.start()
                line_no = processed[:char_idx].count("\n") + 1
                warnings.append(
                    WarningItem(
                        type="inline_math_warning",
                        message=f"Công thức trong dòng (dòng ~{line_no}) có thể có lỗi: {err}",
                        position=line_no,
                        expression=expr[:80]
                    )
                )

        return processed.strip(), warnings

    def _validate_latex(self, expr: str) -> str:
        """
        Quick structural validation of LaTeX expression.
        Returns error message string if an obvious error is found, else empty string.
        """
        if not expr:
            return "Công thức rỗng"

        # Check balanced curly braces { }
        brace_count = 0
        escaped = False
        for char in expr:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count < 0:
                    return "Thừa dấu đóng ngoặc nhọn '}'"
        if brace_count > 0:
            return "Thiếu dấu đóng ngoặc nhọn '}'"

        # Check balanced \begin{...} and \end{...}
        begins = re.findall(r"\\begin\{([^}]+)\}", expr)
        ends = re.findall(r"\\end\{([^}]+)\}", expr)
        if begins != ends:
            return f"Môi trường LaTeX không cân bằng: \\begin{{{','.join(begins)}}} vs \\end{{{','.join(ends)}}}"

        return ""

math_sanitizer = MathSanitizer()

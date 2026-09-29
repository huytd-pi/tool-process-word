import os
import re
from typing import Optional
import docx
from docx.shared import Inches, Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from .schemas import DocumentSettings

class DocxEnhancer:
    """
    Enhances Pandoc-generated Word documents with:
    - Proper A4 / Letter paper size & customizable margins
    - Typography (font family, font size, line spacing)
    - Heading numbering (1., 1.1., 1.1.1.) & keep_with_next
    - Professional table styling (borders, header shading, repeat header, cantSplit)
    - Code block styling (Consolas font, subtle background shading, left accent line)
    - Preserves all native Word OMML math equations intact
    """

    def enhance(self, docx_path: str, settings: DocumentSettings) -> str:
        doc = docx.Document(docx_path)

        # 1. Page Setup: Size and Margins
        self._setup_page(doc, settings)

        # 2. Typography: Normal, Headings, Quotes
        self._setup_styles(doc, settings)

        # 3. Headings: Numbering and Keep-with-next
        self._process_headings(doc, settings)

        # 4. Tables: Professional styling and borders
        self._process_tables(doc, settings)

        # 5. Code blocks & Quotes styling
        self._process_special_blocks(doc, settings)

        # Save enhanced docx
        doc.save(docx_path)
        return docx_path

    def _setup_page(self, doc: docx.Document, settings: DocumentSettings):
        for section in doc.sections:
            # Paper size
            if settings.paper_size == "A4":
                section.page_width = Mm(210)
                section.page_height = Mm(297)
            else:
                section.page_width = Inches(8.5)
                section.page_height = Inches(11.0)

            # Margins
            if settings.margins == "narrow":
                section.top_margin = Mm(12.7)
                section.bottom_margin = Mm(12.7)
                section.left_margin = Mm(12.7)
                section.right_margin = Mm(12.7)
            elif settings.margins == "moderate":
                section.top_margin = Mm(25.4)
                section.bottom_margin = Mm(25.4)
                section.left_margin = Mm(19.1)
                section.right_margin = Mm(19.1)
            elif settings.margins == "wide":
                section.top_margin = Mm(25.4)
                section.bottom_margin = Mm(25.4)
                section.left_margin = Mm(31.8)
                section.right_margin = Mm(31.8)
            else:  # normal
                section.top_margin = Mm(25.4)
                section.bottom_margin = Mm(25.4)
                section.left_margin = Mm(25.4)
                section.right_margin = Mm(25.4)

    def _setup_styles(self, doc: docx.Document, settings: DocumentSettings):
        font_name = settings.font_family
        base_size = settings.font_size
        spacing = settings.line_spacing

        # Helper to set font and XML rFonts
        def apply_font_to_style(style, size_pt, bold=False, italic=False, color=None):
            font = style.font
            font.name = font_name
            font.size = Pt(size_pt)
            font.bold = bold
            font.italic = italic
            if color:
                font.color.rgb = color
            
            # Ensure Word uses the specified font for all scripts (Unicode / East Asia / Complex Script)
            rPr = style._element.get_or_add_rPr()
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.append(rFonts)
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:cs'), font_name)

        # Normal style
        if "Normal" in doc.styles:
            normal_style = doc.styles["Normal"]
            apply_font_to_style(normal_style, base_size)
            normal_style.paragraph_format.line_spacing = spacing
            normal_style.paragraph_format.space_after = Pt(6)

        # Title
        if "Title" in doc.styles:
            title_style = doc.styles["Title"]
            apply_font_to_style(title_style, base_size + 10, bold=True, color=RGBColor(15, 23, 42))
            title_style.paragraph_format.space_after = Pt(12)
            title_style.paragraph_format.keep_with_next = True

        # Heading 1
        if "Heading 1" in doc.styles:
            h1_style = doc.styles["Heading 1"]
            apply_font_to_style(h1_style, base_size + 4, bold=True, color=RGBColor(30, 41, 59))
            h1_style.paragraph_format.space_before = Pt(12)
            h1_style.paragraph_format.space_after = Pt(6)
            h1_style.paragraph_format.keep_with_next = True

        # Heading 2
        if "Heading 2" in doc.styles:
            h2_style = doc.styles["Heading 2"]
            apply_font_to_style(h2_style, base_size + 2, bold=True, color=RGBColor(51, 65, 85))
            h2_style.paragraph_format.space_before = Pt(10)
            h2_style.paragraph_format.space_after = Pt(4)
            h2_style.paragraph_format.keep_with_next = True

        # Heading 3
        if "Heading 3" in doc.styles:
            h3_style = doc.styles["Heading 3"]
            apply_font_to_style(h3_style, base_size, bold=True, color=RGBColor(71, 85, 105))
            h3_style.paragraph_format.space_before = Pt(8)
            h3_style.paragraph_format.space_after = Pt(3)
            h3_style.paragraph_format.keep_with_next = True

        # Blockquote
        if "Blockquote" in doc.styles:
            bq_style = doc.styles["Blockquote"]
            apply_font_to_style(bq_style, base_size - 0.5, italic=True, color=RGBColor(71, 85, 105))
            bq_style.paragraph_format.left_indent = Inches(0.4)
            bq_style.paragraph_format.space_after = Pt(6)

    def _process_headings(self, doc: docx.Document, settings: DocumentSettings):
        h1_count = 0
        h2_count = 0
        h3_count = 0

        for p in doc.paragraphs:
            style_name = p.style.name if p.style else ""
            if style_name.startswith("Heading"):
                # Always prevent orphaned headings
                p.paragraph_format.keep_with_next = True

                if settings.number_headings:
                    if style_name == "Heading 1":
                        h1_count += 1
                        h2_count = 0
                        h3_count = 0
                        prefix = f"{h1_count}. "
                        self._prepend_text_to_paragraph(p, prefix)
                    elif style_name == "Heading 2":
                        h2_count += 1
                        h3_count = 0
                        prefix = f"{h1_count}.{h2_count}. "
                        self._prepend_text_to_paragraph(p, prefix)
                    elif style_name == "Heading 3":
                        h3_count += 1
                        prefix = f"{h1_count}.{h2_count}.{h3_count}. "
                        self._prepend_text_to_paragraph(p, prefix)

    def _prepend_text_to_paragraph(self, p, prefix: str):
        if not p.runs:
            p.text = prefix
            return
        # If prefix already exists, don't duplicate
        first_text = p.runs[0].text
        if re.match(r"^\d+(\.\d+)*\.\s+", first_text):
            return
        p.runs[0].text = prefix + first_text

    def _process_tables(self, doc: docx.Document, settings: DocumentSettings):
        border_xml = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            '  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            '  <w:left w:val="none"/>'
            '  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
            '  <w:right w:val="none"/>'
            '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            '  <w:insideV w:val="none"/>'
            '</w:tblBorders>'
        )

        for table in doc.tables:
            tblPr = table._tbl.tblPr
            
            # 1. Apply clean borders
            existing_borders = tblPr.find(qn('w:tblBorders'))
            if existing_borders is not None:
                tblPr.remove(existing_borders)
            tblPr.append(border_xml)

            # 2. Center alignment for table
            tblJc = tblPr.find(qn('w:jc'))
            if tblJc is None:
                tblJc = OxmlElement('w:jc')
                tblPr.append(tblJc)
            tblJc.set(qn('w:val'), 'center')

            # 3. Repeat Header Row & Header Shading
            if len(table.rows) > 0:
                header_row = table.rows[0]
                trPr = header_row._tr.get_or_add_trPr()
                # Repeat header row on new page
                if trPr.find(qn('w:tblHeader')) is None:
                    trPr.append(OxmlElement('w:tblHeader'))
                
                # Header row styling
                shd_xml = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
                for cell in header_row.cells:
                    tcPr = cell._tc.get_or_add_tcPr()
                    tcPr.append(shd_xml)
                    for p in cell.paragraphs:
                        p.paragraph_format.space_before = Pt(4)
                        p.paragraph_format.space_after = Pt(4)
                        for run in p.runs:
                            run.font.bold = True
                            run.font.size = Pt(settings.font_size - 1)
                            run.font.name = settings.font_family

            # 4. cantSplit on all rows and padding for readability
            for row in table.rows:
                trPr = row._tr.get_or_add_trPr()
                if trPr.find(qn('w:cantSplit')) is None:
                    trPr.append(OxmlElement('w:cantSplit'))

                # Set cell margins (padding)
                for cell in row.cells:
                    for p in cell.paragraphs:
                        # ensure compact spacing in table
                        p.paragraph_format.line_spacing = 1.15
                        if row != table.rows[0]:
                            p.paragraph_format.space_before = Pt(3)
                            p.paragraph_format.space_after = Pt(3)
                            for run in p.runs:
                                run.font.size = Pt(settings.font_size - 1)
                                run.font.name = settings.font_family

    def _process_special_blocks(self, doc: docx.Document, settings: DocumentSettings):
        """Enhances source code blocks and blockquotes with borders and backgrounds."""
        code_bg_xml = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
        code_border_xml = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            '  <w:left w:val="single" w:sz="18" w:space="8" w:color="0284C7"/>'
            '</w:pBdr>'
        )

        for p in doc.paragraphs:
            style_name = p.style.name if p.style else ""
            if style_name in ["Source Code", "SourceCode", "Code"]:
                pPr = p._p.get_or_add_pPr()
                pPr.append(code_bg_xml)
                pPr.append(code_border_xml)
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = "Consolas"
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(15, 23, 42)

docx_enhancer = DocxEnhancer()

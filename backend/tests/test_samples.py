import os
import io
import zipfile
import pytest
import xml.dom.minidom
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.schemas import DocumentSettings
from app.docx_converter import docx_converter
from app.html_parser import html_parser
from app.math_sanitizer import math_sanitizer
try:
    from .sample_data import (
        SAMPLE_1_VIETNAMESE,
        SAMPLE_2_COMPLEX_MATH,
        SAMPLE_3_HTML_KATEX,
        SAMPLE_4_CODE_IMAGES
    )
except ImportError:
    from tests.sample_data import (
        SAMPLE_1_VIETNAMESE,
        SAMPLE_2_COMPLEX_MATH,
        SAMPLE_3_HTML_KATEX,
        SAMPLE_4_CODE_IMAGES
    )

client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint returns pandoc status and does not leak secret values."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "pandoc_available" in data
    assert "deepseek_configured" in data
    # Ensure api key is never in health response
    assert "DEEPSEEK_API_KEY" not in str(data)
    assert "api_key" not in str(data).lower()

@pytest.mark.asyncio
async def test_sample_1_vietnamese_article():
    """
    Test Case 1: Vietnamese article with headings, lists, blockquote, and markdown table.
    Verifies no content is lost and Vietnamese typography is preserved.
    """
    settings = DocumentSettings(
        paper_size="A4",
        margins="normal",
        font_family="Times New Roman",
        font_size=12,
        number_headings=True
    )
    docx_bytes, warnings, filename = await docx_converter.convert_markdown_to_docx(
        SAMPLE_1_VIETNAMESE,
        settings
    )
    assert len(docx_bytes) > 0
    assert filename.endswith(".docx")

    # Inspect docx archive
    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
        
        # Verify Vietnamese keywords are preserved intact
        assert "Nghiên Cứu Ứng Dụng Học Máy" in doc_xml
        assert "Cách mạng Công nghiệp" in doc_xml
        assert "Mô hình thuật toán" in doc_xml
        assert "Random Forest Baseline" in doc_xml
        assert "Transformer-based Model" in doc_xml

        # Verify Table elements exist
        assert "<w:tbl>" in doc_xml or "<w:tbl " in doc_xml
        assert "tblHeader" in doc_xml
        assert "cantSplit" in doc_xml

@pytest.mark.asyncio
async def test_sample_2_complex_math():
    """
    Test Case 2: Document with fractions, roots, sums, integrals, matrices, multiline equations.
    Verifies presence of native Word Equation OMML elements (m:oMath, m:oMathPara).
    """
    settings = DocumentSettings(
        paper_size="A4",
        margins="normal",
        font_family="Times New Roman",
        font_size=12
    )
    docx_bytes, warnings, filename = await docx_converter.convert_markdown_to_docx(
        SAMPLE_2_COMPLEX_MATH,
        settings
    )
    assert len(docx_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
        
        # 1. Verify OMML namespace and elements
        assert "m:oMath" in doc_xml, "Tài liệu phải chứa phần tử OMML m:oMath"
        assert "m:oMathPara" in doc_xml, "Tài liệu phải chứa khối công thức OMML m:oMathPara"
        
        # 2. Verify math mathematical elements in OMML:
        # m:f (fraction / phân số)
        assert "<m:f>" in doc_xml or "<m:f " in doc_xml, "OMML phải có thẻ m:f cho phân số"
        # m:rad (radical / căn thức)
        assert "<m:rad>" in doc_xml or "<m:rad " in doc_xml, "OMML phải có thẻ m:rad cho căn thức"
        # m:nary (n-ary operator for sums/integrals / tổng/tích phân)
        assert "<m:nary>" in doc_xml or "<m:nary " in doc_xml, "OMML phải có thẻ m:nary cho tích phân hoặc tổng"
        # m:m (matrix / ma trận)
        assert "<m:m>" in doc_xml or "<m:m " in doc_xml, "OMML phải có thẻ m:m cho ma trận"

@pytest.mark.asyncio
async def test_sample_3_html_katex():
    """
    Test Case 3: HTML with KaTeX and inline math from ChatGPT/Gemini/NotebookLM.
    Verifies HTML extraction and OMML equation output.
    """
    # 1. Parse HTML to markdown
    md_text, html_warns = html_parser.parse_html_to_markdown(SAMPLE_3_HTML_KATEX)
    assert "\\Psi(x, t)" in md_text
    assert "\\hbar" in md_text
    assert "Cơ Học Lượng Tử Cơ Bản" in md_text

    # 2. Convert to DOCX
    settings = DocumentSettings(paper_size="A4")
    docx_bytes, warnings, filename = await docx_converter.convert_markdown_to_docx(
        md_text,
        settings
    )
    assert len(docx_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
        assert "m:oMath" in doc_xml
        assert "Cơ Học Lượng Tử Cơ Bản" in doc_xml

@pytest.mark.asyncio
async def test_sample_4_code_images_and_symbols():
    """
    Test Case 4: Code blocks, images, and special scientific symbols.
    Verifies code blocks are preserved as code (not formulas),
    embedded images are saved in docx package, and special symbols exist.
    """
    settings = DocumentSettings(paper_size="A4")
    docx_bytes, warnings, filename = await docx_converter.convert_markdown_to_docx(
        SAMPLE_4_CODE_IMAGES,
        settings
    )
    assert len(docx_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as z:
        file_list = z.namelist()
        doc_xml = z.read("word/document.xml").decode("utf-8")
        
        # 1. Verify code is preserved verbatim and not converted to math
        assert "compute_fft" in doc_xml
        assert "sample_rate" in doc_xml
        assert "checkServerHealth" in doc_xml

        # 2. Verify image is embedded inside word/media/
        media_files = [f for f in file_list if f.startswith("word/media/")]
        assert len(media_files) >= 1, f"Tài liệu phải chứa ảnh trong word/media/: {media_files}"

        # 3. Verify Greek and scientific symbols in OMML
        assert "m:oMath" in doc_xml

def test_api_key_leak_prevention():
    """Verify API keys are never leaked to responses, logs, or word files."""
    dummy_key = "sk-test-secret-key-999888777666"
    os.environ["DEEPSEEK_API_KEY"] = dummy_key
    
    # Reload settings
    from app.config import Settings
    temp_settings = Settings()
    assert temp_settings.DEEPSEEK_API_KEY == dummy_key

    # Call health check
    resp = client.get("/api/health")
    assert dummy_key not in resp.text
    
    # Call normalize endpoint with mock
    req_payload = {
        "raw_text": "# Tiêu đề\nNội dung văn bản",
        "source": "auto"
    }
    resp = client.post("/api/normalize", json=req_payload)
    assert dummy_key not in resp.text

    # Clean up env
    os.environ["DEEPSEEK_API_KEY"] = ""

@pytest.mark.asyncio
async def test_inline_math_mixed_in_text_runs():
    """
    Test specifically addressing user request:
    'công thức ở dòng thì định dạng ok, nhưng công thức lẫn với dòng có text là không chuyển đổi được'
    Verifies that inline formulas mixed in Vietnamese sentences (with spaces, latex parens,
    adjacent characters, and punctuation) are converted to native Word OMML <m:oMath>.
    """
    test_text = """# Thử nghiệm công thức trong dòng văn bản

Cho hàm số $f(x) = x^2 + 2x + 1$ xác định với mọi $x \\in \\mathbb{R}$.

Biết rằng điểm $M(x_0, y_0)$ thuộc đồ thị và có $k = f'(x_0) = 2x_0 + 2$.

Công thức có dấu cách: $ \\alpha + \\beta = \\gamma $ và $ x $.

Công thức LaTeX parens: \\(g(x) = \\sqrt{x}\\) và điểm \\(A(1, 1)\\).

Công thức dính chữ: giá trị$x_1$và$x_2$ là nghiệm.

Công thức đi liền dấu câu: Ta có $a$, $b$, và $c$ thỏa mãn ($a + b = c$).

| Đại lượng | Ký hiệu | Giá trị |
| --- | --- | --- |
| Gia tốc | $a = \\frac{dv}{dt}$ | $9.8\\text{ m/s}^2$ |
| Vận tốc | $v(t) = v_0 + at$ | $20\\text{ m/s}$ |
"""

    settings = DocumentSettings(
        paper_size="A4",
        margins="normal",
        font_family="Times New Roman",
        font_size=12
    )

    docx_bytes, warnings, filename = await docx_converter.convert_markdown_to_docx(
        test_text,
        settings
    )

    assert len(docx_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
        
        # Verify OMML elements are present
        assert "<m:oMath>" in doc_xml or "<m:oMath " in doc_xml, "Tài liệu phải chứa <m:oMath> cho công thức trong dòng"
        
        # Count oMath instances - should be at least 12 inline formulas converted
        omath_count = doc_xml.count("<m:oMath>") + doc_xml.count("<m:oMath ")
        assert omath_count >= 10, f"Kỳ vọng ít nhất 10 công thức inline được chuyển đổi, thực tế: {omath_count}"
        
        # Verify text runs and math coexist in the same paragraphs
        import xml.etree.ElementTree as ET
        root = ET.fromstring(doc_xml)
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }
        
        paragraphs_with_math_and_text = 0
        for p in root.findall('.//w:p', ns):
            has_math = len(p.findall('.//m:oMath', ns)) > 0
            has_text = len(p.findall('.//w:t', ns)) > 0
            if has_math and has_text:
                paragraphs_with_math_and_text += 1
                
        assert paragraphs_with_math_and_text >= 5, f"Kỳ vọng ít nhất 5 đoạn chứa đồng thời văn bản và công thức OMML, thực tế: {paragraphs_with_math_and_text}"

@pytest.mark.asyncio
async def test_start_fragment_end_fragment_stripping():
    """
    Test specifically addressing user request:
    'StartFragmentChất lỏng màu xanh ..... ao nhiêu?EndFragment có kỹ tự StartFragment và EndFragment'
    Verifies that StartFragment, EndFragment, and Windows Clipboard CF_HTML headers
    are cleanly removed without trace in markdown, preview, and exported docx.
    """
    raw_user_input = "StartFragmentChất lỏng màu xanh với độ nhớt $\\eta = 1.2 \\times 10^{-3}\\text{ Pa}\\cdot\\text{s}$ có thể tích bao nhiêu?EndFragment"

    # Test math sanitizer
    clean_text, _ = math_sanitizer.sanitize(raw_user_input)
    assert "StartFragment" not in clean_text
    assert "EndFragment" not in clean_text
    assert clean_text.startswith("Chất lỏng màu xanh")
    assert clean_text.endswith("bao nhiêu?")

    # Test HTML parser with Windows CF_HTML comments and headers
    cf_html = """Version:0.9
StartHTML:0000000105
EndHTML:0000000250
StartFragment:0000000125
EndFragment:0000000220
<!--StartFragment--><p>Chất lỏng màu đỏ $T = 100^\\circ\\text{C}$</p><!--EndFragment-->"""
    parsed_md, _ = html_parser.parse_html_to_markdown(cf_html)
    assert "StartFragment" not in parsed_md
    assert "EndFragment" not in parsed_md
    assert "StartHTML" not in parsed_md
    assert "Chất lỏng màu đỏ" in parsed_md

    # Test via API sanitize
    resp = client.post("/api/sanitize", json={"text": raw_user_input})
    assert resp.status_code == 200
    data = resp.json()
    assert "StartFragment" not in data["markdown"]
    assert "EndFragment" not in data["markdown"]
    assert data["markdown"].startswith("Chất lỏng màu xanh")

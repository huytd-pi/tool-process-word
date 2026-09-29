# Sample test data for the 4 required test cases

SAMPLE_1_VIETNAMESE = """# Nghiên Cứu Ứng Dụng Học Máy Trong Phân Tích Dữ Liệu Lớn

Tác giả: Nhóm Nghiên Cứu Trí Tuệ Nhân Tạo  
Ngày công bố: 29/09/2026

## 1. Giới thiệu tổng quan
Học máy (Machine Learning) và trí tuệ nhân tạo đang đóng vai trò then chốt trong cuộc Cách mạng Công nghiệp lần thứ tư. Việc chuẩn hóa và xử lý dữ liệu đòi hỏi các quy trình chặt chẽ và thuật toán tối ưu.

> "Dữ liệu là nguồn tài nguyên mới của kỷ nguyên số, nhưng chỉ khi được phân tích đúng cách thì nó mới tạo ra giá trị đột phá."

### 1.1. Các mục tiêu nghiên cứu
Dự án tập trung vào ba trọng tâm chính:
- Khảo sát các kiến trúc mạng nơ-ron sâu tiên tiến.
- Tối ưu hóa thời gian xử lý và tiêu thụ bộ nhớ.
- Đảm bảo tính minh bạch và khả năng giải thích của mô hình.

### 1.2. Quy trình thực nghiệm
1. Thu thập dữ liệu từ các nguồn mở uy tín.
2. Tiền xử lý, làm sạch và loại bỏ nhiễu.
3. Huấn luyện mô hình với kỹ thuật Cross-Validation 5-fold.
4. Đánh giá độ chính xác trên tập kiểm thử độc lập.

## 2. Kết quả thực nghiệm và so sánh
Dưới đây là bảng tổng hợp kết quả thử nghiệm trên tập dữ liệu chuẩn:

| Mô hình thuật toán | Độ chính xác (Accuracy) | F1-Score (%) | Thời gian huấn luyện (giây) | Ghi chú |
| --- | --- | --- | --- | --- |
| Random Forest Baseline | 87.4% | 86.2% | 12.5 | Nhanh, dễ diễn giải |
| Gradient Boosting (XGBoost) | 92.1% | 91.8% | 34.2 | Hiệu năng cao |
| Deep Neural Network (DNN) | 94.6% | 94.3% | 128.0 | Đạt kết quả tốt nhất |
| Transformer-based Model | 95.8% | 95.5% | 310.5 | Cần GPU chuyên dụng |

Kết luận: Mô hình Transformer cho độ chính xác cao nhất nhưng đánh đổi về tài nguyên tính toán.
"""

SAMPLE_2_COMPLEX_MATH = """# Khảo Sát Các Phương Trình Toán Học Và Vật Lý Lý Thuyết

## 1. Phân số, căn bậc hai và giới hạn
Phân phối chuẩn Gauss với kỳ vọng $\\mu$ và phương sai $\\sigma^2$ có hàm mật độ xác suất:
$$
f(x) = \\frac{1}{\\sigma \\sqrt{2\\pi}} e^{-\\frac{(x - \\mu)^2}{2\\sigma^2}}
$$

Bất đẳng thức Cauchy-Schwarz dạng căn thức:
$$
\\sqrt{\\frac{a^2 + b^2}{2}} \\ge \\frac{a + b}{2} \\ge \\sqrt{ab}
$$

Giới hạn lượng giác cơ bản khi $x \\to 0$:
$$
\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1
$$

## 2. Tổng vô hạn và tích phân suy rộng
Tổng chuỗi Basel nổi tiếng của Euler:
$$
\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
$$

Tích phân Gauss trên toàn trục số:
$$
\\int_{-\\infty}^{+\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

Tích phân Gamma tổng quát:
$$
\\Gamma(z) = \\int_{0}^{\\infty} x^{z-1} e^{-x} dx, \\quad \\text{với } \\text{Re}(z) > 0
$$

## 3. Ma trận và đại số tuyến tính
Ma trận xoay 3D và vector trạng thái:
$$
\\mathbf{R}_z(\\theta) = \\begin{bmatrix}
\\cos\\theta & -\\sin\\theta & 0 \\\\
\\sin\\theta & \\cos\\theta & 0 \\\\
0 & 0 & 1
\\end{bmatrix}, \\quad
\\vec{v} = \\begin{pmatrix} x \\\\ y \\\\ z \\end{pmatrix}
$$

Định thức của ma trận vuông cấp 2:
$$
\\det(A) = \\begin{vmatrix} a & b \\\\ c & d \\end{vmatrix} = ad - bc
$$

## 4. Hệ phương trình Maxwell và hàm phân nhánh
Bốn phương trình vi phân Maxwell mô tả điện từ trường:
$$
\\begin{aligned}
\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\varepsilon_0} \\\\
\\nabla \\cdot \\mathbf{B} &= 0 \\\\
\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\
\\nabla \\times \\mathbf{B} &= \\mu_0 \\left( \\mathbf{J} + \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t} \\right)
\\end{aligned}
$$

Hàm kích hoạt ReLu cải biên (Leaky ReLU):
$$
f(x) = \\begin{cases}
x & \\text{khi } x \\ge 0 \\\\
\\alpha x & \\text{khi } x < 0 \\text{ với } \\alpha = 0.01
\\end{cases}
$$
"""

SAMPLE_3_HTML_KATEX = """<div class="chatgpt-response">
<h1>Cơ Học Lượng Tử Cơ Bản</h1>
<p>Trong cơ học lượng tử, trạng thái của một hạt vi mô được mô tả bởi hàm sóng <span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi mathvariant="normal">Ψ</mi><mo stretchy="false">(</mo><mi>x</mi><mo separator="true">,</mo><mi>t</mi><mo stretchy="false">)</mo></mrow><annotation encoding="application/x-tex">\\Psi(x, t)</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="mord">Ψ</span><span class="mopen">(</span><span class="mord mathnormal">x</span><span class="mpunct">,</span><span class="mspace" style="margin-right:0.1667em;"></span><span class="mord mathnormal">t</span><span class="mclose">)</span></span></span></span>.</p>

<h2>Phương Trình Schrödinger Độc Lập Thời Gian</h2>
<p>Phương trình trạng thái dừng trong giếng thế 1 chiều:</p>

<div class="katex-display"><span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mo>−</mo><mfrac><msup><mi mathvariant="normal">ℏ</mi><mn>2</mn></msup><mrow><mn>2</mn><mi>m</mi></mrow></mfrac><mfrac><mrow><msup><mi>d</mi><mn>2</mn></msup><mi>ψ</mi></mrow><mrow><mi>d</mi><msup><mi>x</mi><mn>2</mn></msup></mrow></mfrac><mo>+</mo><mi>V</mi><mo stretchy="false">(</mo><mi>x</mi><mo stretchy="false">)</mo><mi>ψ</mi><mo>=</mo><mi>E</mi><mi>ψ</mi></mrow><annotation encoding="application/x-tex">-\\frac{\\hbar^2}{2m} \\frac{d^2\\psi}{dx^2} + V(x)\\psi = E\\psi</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="mord">...</span></span></span></span></div>

<p>Các đại lượng liên quan:</p>
<ul>
  <li>Hằng số Planck rút gọn: <span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi mathvariant="normal">ℏ</mi><mo>=</mo><mfrac><mi>h</mi><mrow><mn>2</mn><mi>π</mi></mrow></mfrac></mrow><annotation encoding="application/x-tex">\\hbar = \\frac{h}{2\\pi}</annotation></semantics></math></span></span></li>
  <li>Khối lượng hạt: <i>m</i></li>
  <li>Thế năng: <i>V(x)</i></li>
</ul>

<table>
  <thead>
    <tr>
      <th>Mức năng lượng n</th>
      <th>Công thức năng lượng</th>
      <th>Trạng thái</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>n = 1</td>
      <td>E_1 = \\frac{\\pi^2 \\hbar^2}{2m L^2}</td>
      <td>Cơ bản (Ground state)</td>
    </tr>
    <tr>
      <td>n = 2</td>
      <td>E_2 = 4 E_1</td>
      <td>Kích thích cấp 1</td>
    </tr>
  </tbody>
</table>
</div>"""

# Tiny 1x1 transparent PNG encoded in base64 for testing image embedding
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

SAMPLE_4_CODE_IMAGES = f"""# Lập Trình Khoa Học Và Xử Lý Tín Hiệu

## 1. Khối mã nguồn thuật toán
Đoạn mã Python thực hiện biến đổi Fourier nhanh (FFT) trên tín hiệu âm thanh:

```python
import numpy as np

def compute_fft(signal: np.ndarray, sample_rate: int):
    \"\"\"Tính toán phổ tần số của tín hiệu đầu vào.\"\"\"
    n = len(signal)
    frequencies = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitudes = np.abs(np.fft.rfft(signal)) / n
    return frequencies, magnitudes

# Khởi tạo tín hiệu mẫu: f = 50 Hz
t = np.linspace(0, 1.0, 1000)
test_signal = np.sin(2 * np.pi * 50 * t)
freqs, mags = compute_fft(test_signal, 1000)
print(f"Tần số đỉnh: {{freqs[np.argmax(mags)]}} Hz")
```

Khối mã JavaScript kiểm tra kết nối API:

```javascript
async function checkServerHealth(endpointUrl) {{
  const response = await fetch(endpointUrl, {{ method: 'GET' }});
  if (!response.ok) {{
    throw new Error(`HTTP Error: ${{response.status}}`);
  }}
  return await response.json();
}}
```

## 2. Hình ảnh minh họa và ký tự đặc biệt
Hình ảnh sơ đồ hệ thống được nhúng trực tiếp:

![Sơ đồ tín hiệu mẫu](data:image/png;base64,{TINY_PNG_B64})

### 2.1. Bảng ký hiệu khoa học đặc biệt
| Nhóm ký hiệu | Danh sách ký hiệu | Ứng dụng |
| --- | --- | --- |
| Chữ Hy Lạp | $\\alpha, \\beta, \\gamma, \\delta, \\epsilon, \\zeta, \\eta, \\theta, \\lambda, \\mu, \\xi, \\pi, \\rho, \\sigma, \\tau, \\phi, \\chi, \\psi, \\omega$ | Góc, tần số, bước sóng, độ nhớt |
| Toán tử tập hợp | $\\forall, \\exists, \\in, \\notin, \\subset, \\subseteq, \\cup, \\cap, \\emptyset, \\mathbb{{R}}, \\mathbb{{C}}, \\mathbb{{Z}}$ | Logic vị từ và giải tích |
| Quan hệ logic & mũi tên | $\\rightarrow, \\Rightarrow, \\iff, \\approx, \\neq, \\le, \\ge, \\pm, \\mp$ | Phương trình và suy luận |
| Đơn vị vật lý | $\\text{{m/s}}^2, \\text{{kg}}\\cdot\\text{{m}}^2/\\text{{s}}^2, \\Omega, \\mu\\text{{F}}, \\text{{GHz}}$ | Đo lường thực nghiệm |
"""

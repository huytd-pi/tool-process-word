# Lập Trình Khoa Học Và Xử Lý Tín Hiệu

## 1. Khối mã nguồn thuật toán
Đoạn mã Python thực hiện biến đổi Fourier nhanh (FFT) trên tín hiệu âm thanh:

```python
import numpy as np

def compute_fft(signal: np.ndarray, sample_rate: int):
    """Tính toán phổ tần số của tín hiệu đầu vào."""
    n = len(signal)
    frequencies = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitudes = np.abs(np.fft.rfft(signal)) / n
    return frequencies, magnitudes

# Khởi tạo tín hiệu mẫu: f = 50 Hz
t = np.linspace(0, 1.0, 1000)
test_signal = np.sin(2 * np.pi * 50 * t)
freqs, mags = compute_fft(test_signal, 1000)
print(f"Tần số đỉnh: {freqs[np.argmax(mags)]} Hz")
```

Khối mã JavaScript kiểm tra kết nối API:

```javascript
async function checkServerHealth(endpointUrl) {
  const response = await fetch(endpointUrl, { method: 'GET' });
  if (!response.ok) {
    throw new Error(`HTTP Error: ${response.status}`);
  }
  return await response.json();
}
```

## 2. Hình ảnh minh họa và ký tự đặc biệt
Hình ảnh sơ đồ hệ thống được nhúng trực tiếp dạng base64:

![Sơ đồ tín hiệu mẫu](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)

### 2.1. Bảng ký hiệu khoa học đặc biệt
| Nhóm ký hiệu | Danh sách ký hiệu | Ứng dụng |
| --- | --- | --- |
| Chữ Hy Lạp | $\alpha, \beta, \gamma, \delta, \epsilon, \zeta, \eta, \theta, \lambda, \mu, \xi, \pi, \rho, \sigma, \tau, \phi, \chi, \psi, \omega$ | Góc, tần số, bước sóng, độ nhớt |
| Toán tử tập hợp | $\forall, \exists, \in, \notin, \subset, \subseteq, \cup, \cap, \emptyset, \mathbb{R}, \mathbb{C}, \mathbb{Z}$ | Logic vị từ và giải tích |
| Quan hệ logic & mũi tên | $\rightarrow, \Rightarrow, \iff, \approx, \neq, \le, \ge, \pm, \mp$ | Phương trình và suy luận |
| Đơn vị vật lý | $\text{m/s}^2, \text{kg}\cdot\text{m}^2/\text{s}^2, \Omega, \mu\text{F}, \text{GHz}$ | Đo lường thực nghiệm |

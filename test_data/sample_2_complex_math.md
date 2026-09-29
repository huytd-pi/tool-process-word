# Khảo Sát Các Phương Trình Toán Học Và Vật Lý Lý Thuyết

## 1. Phân số, căn bậc hai và giới hạn
Phân phối chuẩn Gauss với kỳ vọng $\mu$ và phương sai $\sigma^2$ có hàm mật độ xác suất:
$$
f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{(x - \mu)^2}{2\sigma^2}}
$$

Bất đẳng thức Cauchy-Schwarz dạng căn thức:
$$
\sqrt{\frac{a^2 + b^2}{2}} \ge \frac{a + b}{2} \ge \sqrt{ab}
$$

Giới hạn lượng giác cơ bản khi $x \to 0$:
$$
\lim_{x \to 0} \frac{\sin(x)}{x} = 1
$$

## 2. Tổng vô hạn và tích phân suy rộng
Tổng chuỗi Basel nổi tiếng của Euler:
$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
$$

Tích phân Gauss trên toàn trục số:
$$
\int_{-\infty}^{+\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Tích phân Gamma tổng quát:
$$
\Gamma(z) = \int_{0}^{\infty} x^{z-1} e^{-x} dx, \quad \text{với } \text{Re}(z) > 0
$$

## 3. Ma trận và đại số tuyến tính
Ma trận xoay 3D và vector trạng thái:
$$
\mathbf{R}_z(\theta) = \begin{bmatrix}
\cos\theta & -\sin\theta & 0 \\
\sin\theta & \cos\theta & 0 \\
0 & 0 & 1
\end{bmatrix}, \quad
\vec{v} = \begin{pmatrix} x \\ y \\ z \end{pmatrix}
$$

Định thức của ma trận vuông cấp 2:
$$
\det(A) = \begin{vmatrix} a & b \\ c & d \end{vmatrix} = ad - bc
$$

## 4. Hệ phương trình Maxwell và hàm phân nhánh
Bốn phương trình vi phân Maxwell mô tả điện từ trường:
$$
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \left( \mathbf{J} + \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t} \right)
\end{aligned}
$$

Hàm kích hoạt ReLu cải biên (Leaky ReLU):
$$
f(x) = \begin{cases}
x & \text{khi } x \ge 0 \\
\alpha x & \text{khi } x < 0 \text{ với } \alpha = 0.01
\end{cases}
$$

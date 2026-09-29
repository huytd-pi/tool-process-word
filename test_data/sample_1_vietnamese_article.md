# Nghiên Cứu Ứng Dụng Học Máy Trong Phân Tích Dữ Liệu Lớn

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

# Nhật ký kỹ thuật

## 2026-10-29 — Cơ sở mã nguồn cho nhóm

- Tổ chức core OpenCV, desktop UI, firmware, test và ví dụ theo module.
- Giữ nguyên nội dung năm bài thực hành và mã firmware mẫu.
- Chuẩn hóa điểm chạy module và launcher độc lập thư mục làm việc.
- Bổ sung tài liệu sử dụng, quy trình đóng góp và kiểm tra tự động.
- 22 test Python, 23 test mô phỏng Windows và build firmware đạt ở môi trường phát triển.

## 2026-10-29 — Kiểm tra bìa B08

Camera DirectShow nhận ảnh 1280×720. Trong 12 khung, 5 khung đọc được PBL5-B08; 7 khung chọn vùng chạm biên nên không chạy QR. Chưa đạt ổn định READY.

Ảnh chẩn đoán cho thấy bộ chọn góc chuyển giữa mép giấy, mép hình in và đường ron nền. Cần sửa lựa chọn tứ giác trước khi thu dữ liệu hàng loạt. Ảnh và metadata thử nghiệm lưu cục bộ, không nằm trong repository.

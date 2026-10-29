# Tiến độ phát triển

Cập nhật: 2026-10-29.

Repository: [pbl5-library-book-inspection](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection). Kiểm tra tự động: [GitHub Actions](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/workflows/checks.yml).

| Hạng mục | Trạng thái | Kết quả |
|---|---|---|
| Cấu trúc repository và hướng dẫn nhóm | Hoàn thành | Tách firmware, vision, software, ví dụ và test |
| Camera và thu ảnh | Đang phát triển | DirectShow nhận khung 1280×720; có bundle ảnh và metadata |
| Hình học bìa A6 | Đang phát triển | Căn phối cảnh được; chọn góc chưa ổn định trên nền có đường ron |
| QR | Đang phát triển | Hỗ trợ PBL5/LIB1; đã đọc PBL5-B08 trên bìa thật |
| Firmware ESP32 | Khởi tạo | Code mẫu Arduino build được; chưa tích hợp cơ cấu |
| Mô hình phát hiện lỗi | Chưa triển khai | Hai lớp mục tiêu: cover_tear, surface_stain |
| Database, policy và tích hợp | Chưa triển khai | Theo kế hoạch kỹ thuật |

## Kiểm chứng

- 22 test Python đạt: hình học/QR, camera mô phỏng, lưu dữ liệu và đường dẫn chạy.
- 23 test mô phỏng của tiện ích camera Windows đạt.
- Firmware mẫu build thành công với PlatformIO; chưa thử upload hoặc vận hành cơ cấu.
- CLI/GUI thu ảnh tổng hợp và khôi phục manifest hoạt động.

Trong đợt kiểm tra 12 khung bìa B08, 5 khung đọc được QR; 7 khung dừng tại bước kiểm tra hình học. Chưa có khung đạt READY liên tiếp. Đây là kết quả thử một bố trí, không phải phép đo độ chính xác tổng quát của QR.

## Ưu tiên

1. Ổn định bộ chọn mép ngoài bìa, loại ứng viên dính đường ron hoặc biên khung.
2. Tách cập nhật preview khỏi xử lý QR.
3. Kiểm tra pilot trên nhiều bìa và điều kiện chiếu sáng trước khi thu dataset.

[Kiến trúc](docs/ARCHITECTURE.md) · [Kế hoạch](docs/PLAN.md) · [Kiểm chứng](docs/COVER_CAPTURE_VALIDATION.md)

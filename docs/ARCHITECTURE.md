# Kiến trúc hệ thống

## Luồng mục tiêu

`Camera → OpenCV/QR → kiểm tra dữ liệu sách → AI → quyết định phân loại → lưu kết quả → ESP32 → xác nhận đầu ra`

Ứng dụng hiện triển khai camera, xử lý bìa, QR và thu ảnh. Các bước database, AI và điều khiển tích hợp thuộc giai đoạn tiếp theo.

## Thành phần

| Module | Chức năng |
|---|---|
| vision/opencv | Thu frame, chất lượng ảnh, bốn góc/crop, QR và bundle dữ liệu |
| vision/yolo | Huấn luyện, đánh giá và suy luận lỗi rách/bẩn |
| software | Giao diện, điều phối, database, policy và adapter thiết bị |
| firmware/esp32 | State machine, sensor, interlock, cơ cấu và xác nhận đầu ra |

Desktop collector nằm tại `software/desktop/cover_capture_app.py`; sử dụng API từ `vision/opencv`. Điểm chạy là `python -m vision.opencv`. Cấu hình OpenCV thuộc module; chưa có định nghĩa dùng chung cần tách ra shared.

## Nguyên tắc tích hợp

- Mỗi thời điểm xử lý một sách/job; ảnh và kết quả liên kết bằng ID.
- Phân biệt kết quả mô phỏng và xác nhận từ thiết bị thật.
- Gửi lệnh hoặc nhận ACK không chứng minh sách đã tới khay.
- AI và giao diện không gọi GPIO trực tiếp.
- Định dạng QR tách khỏi tra cứu danh tính sách.
- Lưu ảnh gốc riêng, không ghi đè bằng crop hoặc ảnh chú thích.

Chi tiết tại [DECISIONS.md](DECISIONS.md).

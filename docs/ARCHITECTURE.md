# Kiến trúc hệ thống

## Luồng mục tiêu

`Camera → OpenCV/QR → kiểm tra dữ liệu sách → AI → quyết định phân loại → lưu kết quả → ESP32 → xác nhận đầu ra`

Trạm OK/NG dùng luồng IR trên ESP32 → ảnh mới và ổn định trên PC → phân loại → quyết định có mã lượt → ESP32 đưa sách ra hoặc gạt → ghi trạng thái vào SQLite. Web HMI đọc nguồn hình và nhật ký chung. Collector QR là ứng dụng riêng cho việc thu ảnh. [Vận hành trạm](INSPECTION_STATION.md).

## Thành phần

| Module | Chức năng |
|---|---|
| vision/opencv | Thu frame, chất lượng ảnh, bốn góc/crop, QR và bundle dữ liệu |
| vision/yolo | Kiểm tra ảnh và chạy model phân loại OK/NG của trạm |
| software | Giao diện, điều phối, database, policy và adapter thiết bị |
| firmware/esp32 | Conveyor receiver with button, IR, PWM, pusher sequence and heartbeat enforcement. Builds for paired ESP-NOW or direct USB. |
| firmware/espnow-bridge | PC-side bridge between USB Serial at 115200 baud and the paired conveyor receiver. |

Desktop collector nằm tại `software/desktop/cover_capture_app.py`; sử dụng API từ `vision/opencv`. Điểm chạy là `python -m vision.opencv`. Cấu hình OpenCV thuộc module; chưa có định nghĩa dùng chung cần tách ra shared.

## Nguyên tắc tích hợp

- Mỗi thời điểm xử lý một sách/job; ảnh và kết quả liên kết bằng ID.
- Phân biệt kết quả mô phỏng và xác nhận từ thiết bị thật.
- Gửi lệnh hoặc nhận ACK không chứng minh sách đã tới khay.
- AI và giao diện không gọi GPIO trực tiếp.
- Định dạng QR tách khỏi tra cứu danh tính sách.
- Lưu ảnh gốc riêng, không ghi đè bằng crop hoặc ảnh chú thích.

Chi tiết tại [DECISIONS.md](DECISIONS.md).

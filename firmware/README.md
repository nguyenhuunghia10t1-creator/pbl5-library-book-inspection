# Firmware ESP32

Project PlatformIO tại [esp32/](esp32/). Mã ứng dụng: [main.cpp](esp32/src/main.cpp); cấu hình: [platformio.ini](esp32/platformio.ini).

## Build

Mở project bằng PlatformIO IDE trong VS Code hoặc sử dụng CLI:

```powershell
pio run --project-dir firmware/esp32
```

Môi trường hiện tại: board esp32dev, framework Arduino. Firmware đang là chương trình mẫu; chưa tích hợp cảm biến, động cơ, servo hoặc giao thức điều phối.

## Tích hợp

Xác minh board, pin map, nguồn/tải và sensor feedback trước khi triển khai cơ cấu. Firmware quản lý trạng thái thiết bị/interlock; phần mềm máy tính gửi yêu cầu qua giao thức được thống nhất. Lệnh hoặc ACK không thay thế xác nhận sách đã tới khay.

Output `.pio/` và metadata IDE không được commit. [Kiến trúc](../docs/ARCHITECTURE.md) · [Quyết định thiết kế](../docs/DECISIONS.md).

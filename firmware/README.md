# Firmware ESP32

Project PlatformIO tại [esp32/](esp32/). Mã ứng dụng: [main.cpp](esp32/src/main.cpp); cấu hình: [platformio.ini](esp32/platformio.ini).

## Build the paired system

Use the existing private pair header for both builds. Follow the role-specific upload commands after verifying each board's MAC address. [Bridge and receiver setup](espnow-bridge/README.md).

```powershell
pio run --project-dir firmware/espnow-bridge -e esp32dev
pio run --project-dir firmware/esp32 -e espnow_receiver
```

## Build the single-board wired fallback

Mở project bằng PlatformIO IDE trong VS Code hoặc sử dụng CLI:

```powershell
pio run --project-dir firmware/esp32 -e esp32dev
```

Firmware vận hành trên esp32dev với Arduino. GPIO18 điều khiển BTS7960, GPIO19 đọc IR, GPIO22 phát lệnh góc MG996R, GPIO23 nhận nút bật/tắt. ESP32 quản lý một lượt sách và tự dừng khi mất heartbeat qua USB. [Nạp board, kiểm tra COM và thử cơ cấu](../docs/INSPECTION_STATION.md).

## Tích hợp

Xác minh board, pin map, nguồn/tải và sensor feedback trước khi triển khai cơ cấu. Firmware quản lý trạng thái thiết bị/interlock; phần mềm máy tính gửi yêu cầu qua giao thức được thống nhất. Lệnh hoặc ACK không thay thế xác nhận sách đã tới khay.

Output `.pio/` và metadata IDE không được commit. [Kiến trúc](../docs/ARCHITECTURE.md) · [Quyết định thiết kế](../docs/DECISIONS.md).

# Thử băng tải, cảm biến IR và servo bằng ESP32

Bản lưu ngày **2026-11-20 18:17:21 +07:00**, múi giờ Việt Nam UTC+07.

Nhánh `firmware/esp32-standalone-20261120-181721`.

Firmware [bts7960_button_ramp.cpp](bts7960_button_ramp.cpp) dùng để thử riêng cụm phần cứng phân loại sách. ESP32 điều khiển BTS7960, đọc nút nhấn và cảm biến IR, rồi gạt servo theo tín hiệu cảm biến. Khi hệ thống bật, cảm biến có thể kích hoạt lượt gạt mới sau khi chu trình servo kết thúc và IR đã trống liên tục 2 giây. Chương trình chạy độc lập, quyết định xử lý trực tiếp trên ESP32. USB Serial 115200 baud dùng để xem log.

Mã nguồn được giữ đúng bản đã nạp ngày 2026-11-19. Chế độ đang chọn là `CONVEYOR_IR_TEST = true`.

## Hoạt động

1. Khởi động với băng tải tắt, PWM bằng 0 và lệnh servo về 0°.
2. Nhấn nút GPIO23 để bật. Khi servo hết thời gian chờ về và IR trống liên tục 2 giây, PWM tăng từ 0 lên 100% trong 2 giây.
3. IR xuống LOW thì PWM về 0. Khi đủ điều kiện kích hoạt, servo nhận lệnh 180°, chờ 700 ms, sau đó nhận lệnh 0° và chờ 700 ms.
4. Một lượt gạt mới được cho phép khi IR đã HIGH liên tục 2 giây và chu trình servo kết thúc. Nếu nút vẫn ở trạng thái bật, băng tải tăng tốc trở lại trong 2 giây. Khoảng IR trống có thể trùng với thời gian chờ servo.
5. Nhấn nút lần nữa để tắt. PWM về 0, chu trình gạt đang chạy bị hủy và servo nhận lệnh về 0°. Trạng thái tắt giữ nguyên đến lần nhấn bật tiếp theo.

IR giữ LOW khiến băng tải tiếp tục dừng và lượt gạt chưa được kích hoạt lại. Nút cần được thả trước khi nhận một lần nhấn mới. PWM chạy ở 20 kHz, độ phân giải 10 bit. Servo nhận xung 50 Hz, dải 500–2400 µs cho các góc lệnh 0–180°.

## Đấu nối của bản thử

| Chức năng | Kết nối |
|---|---|
| BTS7960 RPWM | GPIO18 |
| BTS7960 LPWM | GND |
| BTS7960 VCC, R_EN, L_EN | 3V3 theo cấu hình module trong bài thử |
| BTS7960 B+, B− | Nguồn ngoài 12 V cho động cơ |
| BTS7960 M+, M− | Hai dây động cơ băng tải |
| Cảm biến IR OUT | GPIO19, LOW khi có vật |
| Cảm biến IR VCC, GND | 3V3 và GND |
| Servo Signal | GPIO22 |
| Servo VCC | Nguồn ngoài 5 V của cụm thử |
| Nút thường mở | GPIO23 xuống GND, điện trở kéo lên ngoài 10 kΩ từ GPIO23 tới 3V3 |
| GND | Nối chung ESP32, cảm biến, driver và nguồn servo |

Mã nguồn dùng tên MG995 trong chú thích và phát góc lệnh bằng PWM. Cần kiểm tra hành trình, nguồn cấp và khả năng tương thích với servo đang lắp. GPIO23 dùng chế độ `INPUT` và phụ thuộc điện trở kéo lên ngoài. Mức tín hiệu GPIO của bài thử là 3,3 V.

## Build và nạp

Cài PlatformIO, mở terminal tại thư mục gốc repository rồi chạy

```powershell
pio run --project-dir firmware/manual-tests --environment esp32dev
```

Ngắt nguồn tải motor và servo khi nạp. Xem cổng của ESP32 rồi thay `COMx` bằng cổng thực tế

```powershell
pio device list
pio run --project-dir firmware/manual-tests --environment esp32dev --target upload --upload-port COMx
pio device monitor --port COMx --baud 115200
```

Cấu hình [platformio.ini](platformio.ini) dùng `esp32dev`, Arduino và Espressif32 8.0.0. Sau reset, log có dòng `[READY] BUTTON_IR_SERVO. PWM=0.`. Khi IR trống đủ thời gian và nút đang tắt, log có `[IR] Clear confirmed; button is OFF, motor stays stopped.`.

Để thử băng trống, ngắt điện rồi lắp dây, cấp nguồn lại, để vùng IR trống và nhấn nút bật/tắt. Giữ tay ngoài vùng chuyển động và đặt nút dừng trong tầm với. Sau đó thử đưa từng vật vào vùng cảm biến để quan sát một chu trình dừng, gạt, thu và chạy lại.

## Bằng chứng kiểm tra

| Kiểm tra | Trạng thái | Ghi nhận |
|---|---|---|
| Build bản trong nhánh ngày 2026-11-20 | PASS | PlatformIO esp32dev, Espressif32 8.0.0 và Arduino-ESP32 3.3.12 |
| Nạp bản nguồn ngày 2026-11-19 | PASS | esptool xác minh dữ liệu flash trên ESP32-D0WD-V3 |
| Khởi động bản nguồn ngày 2026-11-19 | PASS | Log READY, PWM 0, IR trống khi board tách khỏi mạch ngoài |
| Nút, IR và chuyển động cơ khí trên cụm đã lắp sau lần nạp đó | NOT_RUN | Chờ kiểm tra thực tế |

Thời gian chờ servo dựa trên bộ định thời. Góc servo thực, kẹt cơ khí và vị trí sách cần được quan sát tại thiết bị.

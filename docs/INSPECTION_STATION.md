# Vận hành trạm kiểm tra sách

The installed system uses a USB-to-ESP-NOW bridge on the PC and a separately powered receiver on the conveyor. Open **ManualMechanics.cmd** to commission the real conveyor with operator OK/NG decisions. Use **SimulateBooks.cmd** for file-image inference without devices. [One-page operator quick start](STATION_QUICKSTART.html).

## Chạy trực tiếp OK/NG

Mở [DirectSorting.cmd](../scripts/windows/DirectSorting.cmd). Khi COM5 và webcam có tín hiệu, để IR trống rồi nhấn Start vật lý. Đưa từng cuốn từ đầu băng. Khi IR phát hiện sách, ESP32 dừng băng; PC chờ 0,35 giây theo cấu hình hiện tại và phân loại toàn khung hình mới bằng best.pt. Nhãn OK cho băng đi tiếp. Với NG, ESP32 đẩy, thu servo và chờ IR trống trước khi chạy lại. Chế độ này dùng nhãn cao nhất kể cả khi độ tin cậy thấp. Mất hình, lỗi model, mất liên lạc hoặc kẹt sách sẽ giữ dừng.

## Chạy trên Windows

Để thử riêng camera và mô hình, cắm webcam USB vào PC rồi chạy [TestCameraAI.cmd](../scripts/windows/TestCameraAI.cmd). Đưa trọn bìa một cuốn sách vào khung và bấm **Chụp và nhận diện**. Trang hiển thị ảnh, nhãn gốc và độ tin cậy. Bản thử dùng `weights/best.pt` với ảnh 448 px. Nhãn “ảnh bình thường” hiện OK và “ảnh lỗi” hiện NG. Nút **Lưu ảnh đã chụp** tải JPEG. All four station launchers share port 8765. Exit the current service before switching modes.

Mở [SimulateBooks.cmd](../scripts/windows/SimulateBooks.cmd) để thử toàn bộ luồng trên PC. Trên giao diện, chọn **Nhấn nút → Chọn OK → Đưa sách vào IR**. Khi thấy **Đưa sách OK ra**, chọn **Lấy sách khỏi IR**. Để thử NG, chọn NG, đưa cuốn tiếp theo vào và lấy sách khỏi IR trong khi tay gạt đang thu. Để nguyên sách trong IR sẽ tạo lỗi gạt hụt. Các nút ngắt liên kết USB, camera và AI phục vụ thử lỗi. Mô phỏng dùng cơ sở dữ liệu riêng.

Mở [InspectBooks.cmd](../scripts/windows/InspectBooks.cmd) để vận hành thật. Một cửa sổ lệnh chạy dịch vụ, trình duyệt mở ở `http://127.0.0.1:8765`. Dừng bằng nút vật lý rồi dùng Ctrl+C trong cửa sổ lệnh để thoát. Đóng tab trình duyệt chỉ đóng trang giám sát.

Trên máy mới, từ thư mục gốc cài môi trường Python 3.11 rồi đặt model vào `weights/best.pt`.

```powershell
py -3.11 -m venv .venv-inspection
& ./.venv-inspection/Scripts/python.exe -m pip install -r requirements-inspection.txt
```

Có thể chỉ định tệp weights khác qua biến môi trường `PBL5_MODEL` hoặc đổi đường dẫn trong [station.json](../configs/station.json). Dùng model phân loại Ultralytics có ánh xạ đầy đủ hai kết quả OK/NG. Khi đổi model, chỉnh tên lớp và cỡ ảnh theo model, khởi động lại ứng dụng và hiệu chỉnh ngưỡng cho checksum mới. ESP32 nhận cùng giao thức.

## Camera và ngưỡng AI lần đầu

1. Cắm **A4tech HD 720P PC Camera** vào máy tính. Trạm chọn đúng tên trong `configs/station.json` qua MSMF. Di chuyển một cuốn sách trong khung để kiểm tra hình trực tiếp. Đóng ứng dụng khác nếu đang chiếm webcam.
2. Gắn camera USB nhìn từ trên, đặt IR sao cho **điểm dừng sau khi băng trôi** nằm trong vùng chụp trọn bìa và ngang với thanh đẩy. Dùng ánh sáng đều và nền tương phản. Kiểm tra cả cuốn nhỏ nhất, lớn nhất và lỗi sát mép. Cố định camera, hướng đặt sách và ánh sáng sau hiệu chỉnh.
3. Khi trạm tắt, để băng trống rồi chọn **Kết nối và hiệu chỉnh → Lưu ảnh băng tải trống**. Có thể lấy mẫu khi ESP32 chưa kết nối. Đặt một cuốn ở vị trí sẽ dừng, nhập mã cuốn thật, chọn nhãn do người kiểm tra xác định và lấy mẫu. Dùng nhiều thiết kế bìa cho cả OK và NG. Mỗi cuốn chỉ thuộc một tập, kể cả khi chụp lại.
4. Thu riêng tập **Hiệu chỉnh** và **Kiểm tra độc lập**. Nút **Đánh giá và lưu ngưỡng** chọn ngưỡng riêng cho OK và NG trên tập hiệu chỉnh. Mức sàn ban đầu là 0,85, có thể cấu hình. Tập độc lập phải có cả hai lớp, phải có kết quả đúng được chấp nhận ở cả hai lớp và không có sách NG lọt thành OK. HMI báo số ảnh OK, NG, HOLD và số nhầm mỗi chiều. Pilot ít sách chỉ xác minh luồng. Trước khi nghiệm thu cần tập đa dạng và 30 lượt tại trạm.
5. Khi vận hành, PC chỉ suy luận sau khi ESP32 dừng và có nhiều khung hình mới cho thấy một bìa nằm ổn định. OpenCV kiểm tra biên, kích thước, độ nét, độ sáng và khác biệt so với nền. Ảnh bìa được đặt lên khung vuông giữ tỷ lệ trước khi phân loại ở 448 px. Không yêu cầu QR. Ảnh lỗi, camera mất hoặc lặp nguyên hình, AI quá hạn hoặc confidence thấp đều giữ dừng. Khi băng tải dừng, rút và cắm lại webcam để kiểm tra trạng thái mất hình và khôi phục xem trước.

## Connect the installed ESP-NOW system

1. Connect the PC-side bridge over USB and power the conveyor receiver from its established supply. Close any serial monitor.
2. Open [ManualMechanics.cmd](../scripts/windows/ManualMechanics.cmd). Check for a connected COM port and live conveyor status. If Windows exposes multiple COM ports, select the bridge's actual port from the HMI.
3. Keep the load power off while verifying the sensor and connection. Existing paired firmware can be reused. If a board needs replacement or reflashing, follow the role-specific builds and keep the same private pair header for both. [Bridge and receiver setup](../firmware/espnow-bridge/README.md).

## Nạp ESP32 và kiểm tra USB Serial cho cấu hình một board

This section applies to direct USB with a single conveyor controller. The upload below and `FlashInspection.cmd` install the wired build.

1. Dùng cáp USB có đường dữ liệu. Khi nạp lần đầu, ngắt nguồn tải motor và servo. GPIO18 điều khiển RPWM trên BTS7960, GPIO19 đọc IR active LOW ở mức 3,3 V, GPIO22 xuất PWM servo, GPIO23 nhận nút thường mở xuống GND. Dùng nguồn tải phù hợp và GND chung. [Sơ đồ thử phần cứng](../firmware/manual-tests/bts7960_button_ramp.cpp)
2. Đóng Serial Monitor và dịch vụ trạm đang giữ COM. Từ thư mục gốc, liệt kê cổng và tìm **Silicon Labs CP210x USB to UART Bridge**. Có thể đối chiếu cổng biến mất rồi xuất hiện khi rút và cắm lại board.
3. Nạp qua cổng vừa tìm. Ví dụ dưới dùng COM5. Thay COM5 nếu Windows cấp số khác.

```powershell
& .\.venv-inspection\Scripts\python.exe -m serial.tools.list_ports -v
$pio = Join-Path $env:USERPROFILE '.platformio\penv\Scripts\platformio.exe'
& $pio run --project-dir firmware/esp32 -e esp32dev -t upload --upload-port COM5
```

4. Sau khi PlatformIO báo `SUCCESS`, giữ cáp USB cắm rồi mở [InspectBooks.cmd](../scripts/windows/InspectBooks.cmd). Nếu chỉ có một CP210x, trạm tự chọn cổng. Nếu có nhiều board hoặc dùng cầu USB–UART khác, nhập COM thực tế ở **Kết nối và hiệu chỉnh**, bấm **Kết nối**. HMI hiện **ESP32 qua USB · COM…** sau khi nhận trạng thái hợp lệ. Có thể kiểm tra kết nối khi board chưa đấu cảm biến hay tải. Nếu HMI báo timeout, kiểm tra đúng firmware, cáp và cổng đã chọn.
5. Firmware đọc góc thu/đẩy và thời gian đã lưu trong NVS của firmware trước. Nếu chưa có giá trị hợp lệ, mặc định là 0°/180° và 700/700 ms. Thử hành trình với servo tách khỏi cơ cấu trước. GPIO22 chỉ phát lệnh góc. Vị trí thực tế của thanh gạt cần quan sát hoặc xác nhận bằng công tắc hành trình.
6. Sau khi hiệu chỉnh camera và ngưỡng AI, chờ HMI sẵn sàng, IR trống rồi bấm nút vật lý để bật. Một lượt FAIL chạy hết đẩy, thu và chờ thêm 2 giây. Sau PASS, băng tải đưa sách ra khỏi IR. Chừa khoảng trống giữa các cuốn. Sau lỗi hoặc mất liên lạc, kiểm tra và dọn trạm rồi bấm nút vật lý để bật lại.

## Giao thức USB Serial và ESP-NOW

The PC speaks the same serial protocol to the bridge or the wired controller. In the two-board setup the bridge relays it over ESP-NOW, and the conveyor receiver owns the job state and acknowledgements.

Cổng dùng 115200 baud, 8N1. Mỗi bản tin ASCII kết thúc bằng LF. Mã lượt gồm 32 ký tự hex của phiên khởi động, dấu gạch ngang và số thứ tự sách. Ví dụ một lượt đọc thành công

```text
ESP32 → PC   CAPTURE,0123456789abcdef0123456789abcdef-1
PC → ESP32   RESULT,0123456789abcdef0123456789abcdef-1,PASS
ESP32 → PC   ACK,0123456789abcdef0123456789abcdef-1,PASS
```

- ESP32 dừng PWM khi IR gặp sách rồi gửi CAPTURE. Python lấy ảnh mới sau khi dừng. OK gửi PASS, NG gửi FAIL. Ảnh không đạt hoặc AI không đủ tin cậy sẽ yêu cầu dừng bằng `HOLD,<id>` hoặc hạ cờ sẵn sàng.
- PC bắt tay bằng `PING,<seq>,-,0`, rồi gửi `PING,<seq>,<boot>,<ready>` khoảng 250 ms/lần. ESP32 trả trạng thái JSON cùng `seq` 8 ký tự hex. ESP32 có thể nhắc lại CAPTURE khi chờ AI. Python chỉ tạo một lượt nhận diện cho mỗi ID và ghi quyết định sau ACK đúng mã và giá trị.
- Khi board còn được cấp nguồn, mất heartbeat 1 giây sẽ ngắt PWM. Chờ AI quá 10 giây, sai ID hoặc bản tin lỗi đều giữ dừng. Nếu rút USB cũng cắt nguồn ESP32 trong khi nguồn động cơ vẫn bật, cần thử riêng trạng thái ngõ vào BTS7960 khi board mất nguồn.

## Hồ sơ và kiểm thử

Dữ liệu nằm trong `data/local/station/`. SQLite tách `hardware.sqlite3` và `simulation.sqlite3`. Mỗi lượt lưu ảnh đầu vào JPEG, ảnh đưa vào AI, nhãn, confidence, checksum model, nguyên nhân giữ dừng và trạng thái. Mã lượt gồm phiên khởi động ESP32 và số thứ tự sách. **Tổng = OK + NG** theo quyết định AI. Lượt chưa phân loại và lỗi cơ khí có dòng lịch sử riêng. Bắt đầu ca mới đặt lại số hiển thị. Hết chu trình điều khiển vẫn để trống `actual_route` cho đến khi có bằng chứng về khay thực.

| Thử nghiệm | Quan sát cần ghi |
|---|---|
| Motor riêng, servo tách khỏi tải | Khởi động PWM=0, nhấn bật tăng dần, nhấn tắt dừng, đo quãng trôi trước khi chốt vị trí IR. |
| IR và sách OK | Tăng băng để đưa sách ra ngay cả khi còn che IR. Một cuốn tạo đúng một lượt. Che liên tục quá 5 giây khi đang đưa ra phải báo kẹt. |
| Servo riêng rồi có tải | NG tạo đúng một lệnh đẩy–thu. Đo góc/thời gian thực, kiểm tra chờ đủ 2 giây và gạt hụt. |
| Lỗi liên lạc | Đóng PC, rút USB, ngắt camera, tạo ảnh mờ, rút điện board ở giữa lượt. Đo thời gian và quãng đường tới dừng. Kiểm tra không tự bật khi hồi phục. |
| Dừng giữa lượt | Bấm OFF khi chờ AI, đang đẩy, đang thu và đang đưa sách OK ra. Không có thêm lượt gạt khi kết quả cũ tới. |
| Chạy pilot | Đối chiếu log, ảnh, kết quả thật và khay quan sát được cho từng cuốn. Ghi riêng số gạt trùng, gạt nhầm, lọt NG, giữ dừng và thời gian mỗi lượt. |

Chạy kiểm thử PC bằng `.venv-inspection/Scripts/python.exe -m unittest discover -s tests -v`. Test trình duyệt qua FastAPI TestClient cần thêm gói `httpx`. Test C++ trong `firmware/esp32/test/host/station_test.cpp` dùng cùng mã chuyển trạng thái với firmware và chạy được bằng trình biên dịch C++11 trên PC. Các test này dùng mô phỏng.

## HMI vận hành trên Windows

Mở DirectSorting để dùng top-1 hoặc ManualMechanics để quyết định bằng tay trong 8 giây. Nhấn một dòng lịch sử để ghim ảnh đầu vào của lượt đó. Mở ca mới khi trạm nghỉ để bắt đầu bộ đếm mới. Lệnh servo và trạng thái hoàn tất chu kỳ là dữ liệu của controller. Quan sát sách ở khay để xác nhận tuyến thực tế.

Cổng bridge đã lắp là COM5. Trường `bridge_diagnostic_port` trong `configs/station.json` chọn cổng được hỏi BRIDGE? khi mở kết nối. Khi chuyển bridge sang cổng khác, cập nhật trường này. Khi cắm trực tiếp receiver qua USB, đặt trường này thành chuỗi rỗng trước khi chạy. Các cổng còn lại chỉ dùng bắt tay PING. HMI hiển thị thời gian từ lần bridge trả lời và trạng thái receiver riêng.

Direct lưu thời gian chờ chụp vào direct-vision-settings.json. Chế độ hiệu chuẩn tiếp tục dùng vision-settings.json. Lượt cũ giữ nguyên dữ liệu gốc; các trường chưa từng đo hiển thị trống.

# Tiến độ phát triển

## 2026-11-25 — Bàn giao mã nguồn cho nhóm

Nhánh `feature/pbl5-station` chứa giao diện vận hành, mô phỏng, firmware USB/ESP-NOW và notebook Colab. README có lệnh cài đặt và hash của mô hình vận hành để đối chiếu khi chia sẻ nội bộ. Bước tiếp theo là chạy mô phỏng trên máy thành viên.


## 2026-11-25 — Notebook Colab phân loại sách OK/NG

Đã tạo [notebook YOLO11n-cls](vision/yolo/train_book_defect_v23_colab.ipynb) cho ZIP book-defect-v23 v1. Đọc đủ 195 ảnh. Chạy thử 1 epoch trên CPU, nạp lại checkpoint, suy luận đủ 19 ảnh test và kiểm tra gói xuất **PASS**. Split Roboflow có 4 ảnh OK ở test và chưa xác minh độc lập theo cuốn. Huấn luyện đủ trên Colab và kiểm tra camera với model mới **NOT_RUN**. Việc tiếp theo là chạy notebook trên Colab với ZIP gốc.

## 2026-11-25 — Mở giao diện vận hành

Đã khởi động chế độ AI trực tiếp và mở giao diện ở cổng 8765. HTTP trả đúng trang và API báo Direct hoạt động. Chưa nhận camera A4tech hoặc cổng COM5. Bước tiếp theo khi chạy sách là kết nối hai thiết bị và xác nhận trạng thái trên giao diện.

## 2026-11-23 — Thiết kế và Việt hóa HMI (DONE)

Đã mở giao diện mới trên dịch vụ Direct ở cổng 8765. Khung camera có sơ đồ trạm khi mất hình. Giao diện, cài đặt, thông báo vận hành, trang thử camera và hướng dẫn dùng tiếng Việt. Chrome kiểm tra ba kích thước desktop không cuộn trang ngoài, hai kích thước nhỏ không tràn ngang, drawer cài đặt và chuyển tab hoạt động. 81 bài Python và 9 bài HMI đạt. Xem [nhật ký](docs/SESSION_LOG.md). Bước tiếp theo của trạm là kiểm tra lượt sách thật khi có camera và bộ điều khiển.


## 2026-11-23 — HMI vận hành theo ca (IN_PROGRESS)

Giao diện tiếng Việt cho AI trực tiếp, AI hiệu chuẩn, Manual và Simulation; trang thử camera riêng. SQLite ghi chính sách, thời gian suy luận và lý do dừng. 81 test Python, 7 test JS PASS. Chrome headless ở ba viewport desktop vừa đủ khung. Dịch vụ thực đã mở lại ở chế độ Direct. Nghiệm thu chuyển động NOT_RUN do thiếu COM5 và webcam A4tech. Việc tiếp theo là quan sát một lượt OK và một lượt NG tại khay sau khi kết nối thiết bị. [Nhật ký](docs/SESSION_LOG.md).


## 2026-11-23 — Chạy trên băng tải theo nhãn OK/NG (IN_PROGRESS)

Mở DirectSorting.cmd. ESP32 đã nhận kết quả từ PC cho cả hai nhãn. Trong 6 lượt đầu có ba lượt OK hoàn tất (1, 2, 5). Lượt 3 nhận NG và dừng NG_NOT_CLEAR. Lượt 4 và 6 dừng BOOK_MOVED. Ở lượt 7, receiver báo PUSH 180°, RETRACT 0°, SETTLE và NG_NOT_CLEAR. Chưa xác nhận sách NG đến khay. Tiếp theo là đối chiếu chuyển động của tay gạt và tín hiệu IR trong lượt NG. [Nhật ký](docs/SESSION_LOG.md).

## 2026-11-23 — Thử trạm đang bật với cuốn Bài tập Cơ học (IN_PROGRESS)

Tám phản hồi COM5 và tám ảnh webcam khác nhau. Đã lưu lại nền băng xanh sau khi người vận hành dọn sách. Với một ảnh webcam của cuốn Bài tập Cơ học, best.pt dự đoán ảnh lỗi 0,67363. Ảnh chuẩn rách IMG_7 trả OK 0,999027. Hai lượt mô phỏng COMPLETE. Lượt tự động trên băng thật chưa diễn ra: NO_COVER ở bước tách bìa, chưa có bộ ngưỡng được xác nhận; OFF, PWM 0. Nếu tiếp tục thử tự động, việc tiếp theo là kiểm tra bộ tách bìa với đúng ảnh và nền mới.

## 2026-11-23 — Camera USB A4tech và xem trước MJPEG (DONE)

OpenCV nhận A4tech HD 720P PC Camera qua MSMF. Giao diện chạy thật dùng camera USB và luồng MJPEG độc lập với trạng thái ESP32. Kiểm tra trên Chrome headless: 81 hình khác nhau trong 3,002 s ở 640×480. 78 kiểm thử Python và 6 kiểm thử HMI đạt. Bước tiếp theo: cố định webcam và lưu ảnh băng tải trống cho camera mới.

## 2026-11-23 — DroidCam trực tiếp và best.pt (IN_PROGRESS)

Sau khi người dùng kết nối điện thoại, đọc được 8/8 JPEG khác nhau ở 640×480 từ HMI hardware. Chạy best.pt trên một ảnh xem trước trả OK 0,99973, chưa có nhãn thật của cảnh. COM5 đang kết nối, board báo FAULT/BOOK_MOVED, PWM 0. Health yêu cầu hiệu chỉnh ngưỡng, ảnh chuẩn rách vẫn bị nhận OK. Tiếp theo là đặt camera cố định trên băng trống và lưu ảnh nền.

## 2026-11-23 — Test tổng thể bằng best.pt và DroidCam (BLOCKED)

Giao diện đã chuyển sang hardware và nhận ESP32 qua COM5. Inference bằng weights/best.pt chạy thành công, nhưng ảnh rách IMG_7 bị phân loại OK (0,999027). DroidCam Client đã mở, hai địa chỉ Wi-Fi lưu trước không trả lời tại cổng 4747 và HMI báo FRAME_FROZEN. Chưa chạy lượt sách tự động. Tiếp theo là xác nhận IP và cổng hiện trên điện thoại để kết nối đúng nguồn.

## 2026-11-23 — Test ESP-NOW với cả hai board trên bàn (PASS)

PC nhận bridge COM5 và receiver COM9. Gửi PING qua COM5, nhận đủ 12/12 phản hồi đúng mã, trung vị khứ hồi 31 ms. HMI chạy tay đã kết nối COM5 và đọc được OFF, PWM 0. Tiếp theo là kiểm tra lại kết nối khi lắp receiver vào đế băng tải.

## 2026-11-23 — Mở giao diện chạy tay

Giao diện trả HTTP 200, chế độ `hardware-manual` **PASS**. Kết nối trực tiếp từ HMI **FAIL** tại lần đọc: COM5 không trả lời, chưa có trạng thái board. Nguyên nhân chưa xác định. Tiếp theo là kiểm tra lại kết nối của bridge trên COM5.

## 2026-11-23 — Kết nối hai ESP32 sau khi cấp nguồn (PASS)

Bridge COM5 đuôi 2A:E4 nhận 4/4 phản hồi ESP-NOW từ bộ điều khiển băng tải. Trạng thái OFF, IR trống và PWM 0. Tiếp theo là đặt sách che cảm biến khi băng tải dừng để kiểm tra IR.

## 2026-11-23 — Khôi phục receiver băng tải AC:5C (DONE)

Sau khi đổi board, COM5 có MAC đuôi `AC:5C`, khớp cấu hình với bridge `2A:E4`. Build, nạp, xác minh flash và đọc Serial **PASS**. Receiver báo `RADIO_READY`, kênh 1, `PHASE=OFF`, `PWM=0`, `OUTPUTS=READY`. Liên lạc hai board sau lần nạp này **NOT_RUN**. Tiếp theo là kiểm tra phản hồi qua bridge với tải tắt.

## 2026-11-23 — Nhận dạng board trước khi nạp receiver (BLOCKED)

Đọc MAC trên COM5 được `<other-board-mac>`. Cấu hình ESP-NOW hiện ghép bridge với receiver đã xác nhận. Kiểm tra MAC **PASS**, nạp **NOT_RUN**. Tiếp theo là xác nhận có thay receiver bằng board vừa kiểm tra hay không.


## 2026-11-23 — Test riêng servo MG996R (IN_PROGRESS)

Board băng tải đuôi AC:5C trên COM5 hiện chạy [bài quét servo GPIO22](firmware/manual-tests/servo-sweep/src/main.cpp). Build, nạp và đọc Serial **PASS**. Một chu kỳ lệnh 0° → 180° → 0° mất 5,008 s. Hành trình cơ khí **NOT_RUN**. Việc tiếp theo là quan sát một chu kỳ khi tháo tay gạt. Khi dùng lại trạm, board này cần firmware `espnow_receiver`.

## 2026-11-21 — Field checklist and workspace cleanup

The [22 November field checklist](docs/FIELD_CHECKLIST.md) covers the paired conveyor, camera/model checks, demo setup and repository audit. Removed 584,527,068 logical bytes of verified duplicates and generated artifacts. Local verification passed 78 Python tests, six HMI tests and the repository check. Running the installed classifier on the retained torn reference returned OK at 0.999027. Automatic sorting still requires a passing profile. Next: observe whether an NG book clears IR and reaches the reject tray in Manual Mechanics.

## 2026-11-21 — Installed wireless conveyor completed manual OK and NG cycles

Flashed the paired receiver and verified six wireless replies from the installed controller through COM5. Manual Mechanics recorded an operator timeout on job 1, completed OK on job 2, and completed NG on job 3. The NG trace showed PUSH at 180 degrees, RETRACT at 0, SETTLE and then RUN. Job 4 stopped with NG_NOT_CLEAR; at readback IR was clear and PWM was 0. The camera independently reported a frozen frame across 56 sequence samples. Physical book destinations and actual servo travel remain unconfirmed. Next: check whether the pusher moved the NG book completely beyond the sensor on job 4.

## 2026-11-21 — PC-side ESP-NOW bridge flashed

The new ESP32 on COM5 (MAC ending 2A:E4) runs the [USB bridge](firmware/espnow-bridge/README.md). Verified flash hash, USB identity, radio initialization on channel 1 and one readiness-disabled PING accepted by the local transmit queue. The conveyor board (AC:5C) still has its standalone firmware. Next: provision and flash the conveyor receiver with the existing local pair header, then verify a peer response with the loads off.

## 2026-11-21 — Original standalone firmware restored on COM5

Flashed the detached ESP32 with the standalone button, IR and pusher firmware from commit `43b2c58`. Flash verification and boot readback passed. The board reported PWM 0 and motor off after the clear interval. Next: install with power disconnected and observe one complete physical cycle using the pushbutton and a single book.

## 2026-11-21 — External-power retest

With external power reported on, COM5 opened but five readiness-disabled status requests returned zero bytes. The previous detached test received five replies. Next: isolate the base by testing it with peripheral cables disconnected, external power off and USB as the only ESP32 supply.

## 2026-11-21 — USB recovered after removing the ESP32 from the base

The same firmware on COM5 responded to five consecutive requests with the ESP32 removed from the base. All five reported OFF and PWM 0. The installed test had returned no application replies. The exact connection causing the difference has not been identified. Next: inspect the unpowered base wiring around RX0/GPIO3 and the socket alignment.

## 2026-11-21 — Installed board serial diagnosis

With load power off, two resets produced readable ESP32 flash boot logs on COM5. Six readiness-disabled application probes returned zero bytes. A ROM read-only probe detected download mode but received no sync reply. The installed PC-to-ESP32 serial path needs inspection. Returned to flash boot and closed COM5. Next: inspect the base connection at RX0/GPIO3 with USB and external power disconnected.

## 2026-11-21 — Installed board USB check

The operator installed the board and confirmed the external ESP32 VIN feed was disconnected. The initial 115200-baud handshake timed out with the loads off. With all supplies on, the COM5 bridge opened, but eight disabled-readiness queries returned zero bytes. Station state and IR remain unknown. DroidCam delivered 36 sampled frame sequences with a frozen image. Next: with load power off and USB connected, capture the installed board's reset log.

## 2026-11-21 — Preparing the installed conveyor test

Windows detected the CP210x on COM5. During an eight-second PC check, DroidCam supplied 42 sampled frames with no confirmed changing image. The automatic threshold profile was absent. The operator confirmed the external 5 V feed had been disconnected from ESP32 VIN and the board was still on USB alone. Next: after power-off installation, check the real IR input in Manual Mechanics.

## 2026-11-21 — USB firmware flashed to the bench ESP32

PlatformIO verified the inspection firmware on the detached ESP32-D0WD-V3 at COM5. Three 115200-baud replies after reset reported OFF, STARTUP, PWM 0 and job 0. Next physical check: reinstall the board with power off, then confirm the real IR sensor changes Clear → Blocked → Clear in Manual Mechanics before powering the motor or servo. [Operator guide](docs/STATION_QUICKSTART.html).

## 2026-11-20 — Station console fixes

Manual Mechanics shows each book's queued decision until its ESP32 acknowledgement arrives. Last stop shows the controller reason and measurements from that incident. Failed calibration shows the failed book and recovery instructions beside the validation button. Simulation reports a blocked IR sensor and displays the active uploaded image. [Verification log](docs/SESSION_LOG.md). PC verification passed with 78 Python tests, six JavaScript tests and a browser check. At the default threshold the model still misclassifies the torn reference and automatic operation stays disarmed. Next physical check: run one manual OK and NG cycle using the [operator guide](docs/STATION_QUICKSTART.html).

## 2026-11-20 — USB inspection commissioning

Manual Mechanics, AI Inspection and file-image Simulation are available from the Windows launchers. [One-page operator quick start](docs/STATION_QUICKSTART.html). PC checks passed: 71 Python tests, the native C++ station suite, USB firmware build, and one-page A4 print. The real classifier predicted OK at 99.90% on the torn IMG_7 reference; the independent reference check blocked automatic operation at the default OK floor. The next physical step is one operator-driven OK and NG cycle in Manual Mechanics, starting with the outputs unpowered for the USB/IR check.

## 2026-11-20 — Đã xuất bản firmware ESP32 độc lập

Đã đẩy nhánh [firmware/esp32-standalone-20261120-181721](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/tree/firmware/esp32-standalone-20261120-181721), tạo lúc 18:17:21 UTC+07. Commit `43b2c58` chứa mã thử nút, băng tải, IR, servo và hướng dẫn ngày giờ, pin map, build, nạp, kiểm chứng. Build **PASS** với Espressif32 8.0.0 và Arduino-ESP32 3.3.12. Đọc lại bốn tệp từ GitHub khớp commit, SHA nhánh từ xa trùng bản local. Chuyển động cơ khí ở lần nạp 2026-11-19 vẫn chờ kiểm tra. Việc tiếp theo là kiểm tra IR OUT đổi trạng thái khi đưa sách vào và lấy ra, giữ nguồn motor và servo tắt.

## 2026-11-19 — ESP32 đang chạy bản thử phần cứng độc lập

Đã tắt trạm Python và nạp lại bản `BUTTON_IR_SERVO` cho ESP32 trên COM5 sau khi người dùng tách board khỏi mạch ngoài. esptool xác minh dữ liệu flash. Log khởi động báo PWM 0, IR trống và motor tắt. GPIO23 đọc LOW khi board tách rời. Bản này dùng điện trở kéo lên ngoài 10 kΩ tới 3V3. Bước tiếp theo là lắp lại mạch khi ngắt điện rồi thử nút bật/tắt trên băng trống. Chưa kiểm chứng chuyển động ở lần nạp này.

## 2026-11-19 — Nạp lại firmware đầy đủ để thử băng tải thật

PlatformIO đã nạp và xác minh firmware trạm qua COM5. Python kết nối lại sau khi ESP32 khởi động, đọc được OFF, PWM 0, IR báo có vật và lệnh servo 0°. Trước khi nạp, board đã nhận nút nhấn và báo PC_NOT_READY. DroidCam đang lặp hình, chưa có tệp ngưỡng AI. Chưa quan sát băng chạy hoặc servo gạt. Việc tiếp theo là kết nối lại DroidCam và xác nhận ảnh trên trạm thay đổi khi di chuyển cuốn sách.

## 2026-11-19 — Đã nhận lại COM5 sau khi đấu dây

HMI nhận board thật, OFF, PWM 0. Trong 32 giây lấy 128 mẫu trạng thái, IR luôn báo có sách. Chưa xác nhận người dùng đã đưa rồi lấy sách trong khoảng đo. DroidCam báo lặp hình. Bước tiếp theo là để trống vùng cảm biến rồi thử với một cuốn sách, quan sát IR trên HMI khi nguồn tải vẫn tắt.

## 2026-11-19 — Chờ cắm lại USB sau khi đấu dây

Người dùng báo đã nối dây. Lúc 17:18, giao diện trạm đang chạy nhưng Windows chưa thấy CP210x và HMI chưa có trạng thái board. Bước tiếp theo là giữ các nguồn tải tắt, kiểm tra dây +5 V ngoài đã tách khỏi chân nguồn ESP32, rồi cắm USB và đợi HMI báo OFF, PWM 0.

## 2026-11-19 — Chuẩn bị chạy camera, IR, servo và băng tải

Người dùng xác nhận bộ cơ đã chạy ở bài thử cũ, nguồn 12 V dành cho động cơ băng tải và nguồn 5 V dành cho servo. Firmware giữ bốn GPIO cũ. HMI đang nối COM5, trạng thái OFF, PWM 0, GPIO19 báo có vật. Chưa xác định jumper còn nối hay tín hiệu do cảm biến. DroidCam báo lặp hình; cơ sở dữ liệu chưa có mẫu hiệu chỉnh hoặc kiểm tra cho model hiện tại.

**Việc tiếp theo:** khi đã ngắt nguồn, lắp lại bộ dây cũ. Lần cấp điện kiểm tra đầu tiên giữ nguồn motor tắt, xác nhận IR đổi trạng thái và khôi phục hình trực tiếp tại vị trí dừng trước khi lưu nền thật.

## 2026-11-19 — Chuẩn bị thử cảm biến IR thật

HMI đang nhận COM5, trạng thái OFF, PWM 0, IR trống. Lần đọc này chưa xác minh được thời điểm người dùng kéo GPIO19 xuống GND. Bước tiếp theo là nhận ảnh rõ chân đấu, ký hiệu nguồn hoặc mã cảm biến IR để xác định cách cấp nguồn và đưa tín hiệu vào GPIO19.

## 2026-11-19 — Đã nạp firmware USB và đọc được trạng thái từ ESP32 thật

PlatformIO nạp thành công qua COM5. Python đọc ba lần liên tiếp được `OFF`, PWM 0, lượt sách 0 ở 115200 baud. HMI trạm thật cũng báo COM5, OFF, PWM 0 và IR trống. Theo người dùng, board hiện chỉ nối với PC. Bước tiếp theo là thử ngõ vào IR trong trạng thái OFF bằng dây jumper từ GPIO19 xuống GND và quan sát trạng thái trên HMI. Chưa kiểm tra cảm biến, cơ cấu hoặc phân loại sách trên băng tải.

## 2026-11-19 — Giao tiếp ESP32–Python qua USB Serial

Trạm thật dùng USB 115200 baud. GPIO18/19/22/23 tiếp tục điều khiển BTS7960, IR, servo và nút. Windows nhận CP210x trên COM5. Đã đóng phiên thử camera chạy nền để giải phóng cổng web cho trạm thật.

PlatformIO build thành công cho esp32dev. 53 kiểm thử Python và kiểm thử C++ trên PC đạt. Cặp Python và bộ đọc firmware C++ trao đổi PASS/FAIL qua đường truyền giả lập. Mô hình `best.pt` thực nhận một ảnh giả lập và trả HOLD khi chưa hiệu chỉnh ngưỡng. Chưa nạp bản USB, chưa thử bắt tay trên board hoặc đo chuyển động thật. **Bước tiếp theo** là nạp firmware qua cổng COM đã đối chiếu, sau đó kiểm tra HMI nhận trạng thái OFF khi tải chưa cấp nguồn. [Lệnh nạp và hướng dẫn thử](docs/INSPECTION_STATION.md).

## 2026-11-19 — Khôi phục mô hình hai lớp và dọn thư mục

Trang thử DroidCam dùng lại `weights/best.pt` ở 448 px. Đã xác minh checksum và phân loại được một ảnh tệp qua API. Cả 15 kiểm thử trạm đạt. Ở lần kiểm tra sau khi khởi động lại dịch vụ, camera ảo đang lặp hình nên chưa xác nhận lượt chụp trực tiếp bằng bản vừa khôi phục.

Tổng kích thước tệp trong dự án giảm khoảng 1,35 GB, từ 4,25 GB còn 2,90 GB. Đã lưu danh sách 40 gói trong hồ sơ cục bộ trước khi xóa môi trường theo yêu cầu. Bước tiếp theo là mở lại luồng DroidCam trên điện thoại để chụp một cuốn sách.

## 2026-11-19 — DroidCam dùng mô hình ba lớp

Đã nạp `weights/best (1).pt` cho trang thử camera. Với một ảnh DroidCam trực tiếp, API trả JPEG, nhãn `ok` và độ tin cậy 71,7%. SHA-256 của mô hình xử lý ảnh khớp tệp người dùng gửi. Chưa xác nhận nhãn thực của ảnh này. Bước tiếp theo là đặt một cuốn sách đã biết tình trạng vào khung và bấm **Chụp và nhận diện**.

## 2026-11-19 — DroidCam và AI đã trả kết quả trên ảnh trực tiếp

Đã mở trang **Chụp và kiểm tra bìa sách**. Dịch vụ trả ba JPEG trực tiếp khác nhau. Khi bấm chụp qua API, mô hình trả ảnh và dự đoán OK với độ tin cậy 99,6%. Chưa có nhãn thực cho ảnh này. Bước tiếp theo là đặt một cuốn sách đã biết tình trạng vào khung rồi bấm **Chụp và nhận diện**.

## 2026-11-19 — Thử riêng DroidCam và AI trên PC

[TestCameraAI.cmd](scripts/windows/TestCameraAI.cmd) mở giao diện chụp một ảnh, xem OK/NG, độ tin cậy và tải JPEG. Dịch vụ đang chạy ở chế độ `camera-test`; ESP32 có thể giữ nguyên kết nối USB. Cả 15 kiểm thử trạm đều đạt. Với một ảnh từ thư mục `test/images`, API dùng đúng weights người dùng cung cấp, trả dự đoán và JPEG giải mã được. Chưa đánh giá độ chính xác trên sách trước camera.

**Bước hiện tại:** kết nối lại DroidCam trên điện thoại với DroidCam Client trên PC. Khi kiểm tra, camera ảo lặp một khung hình và cổng điện thoại đã lưu trong client hết thời gian chờ.

## 2026-11-19 — Kiểm tra thông báo về nút vật lý

Hai lần đọc trạng thái HMI đều thấy ESP32 báo `OFF`, PWM bằng 0 và DroidCam lặp khung hình. Nút ngoài GPIO23 chưa đấu theo người dùng. Chưa thử cơ cấu. Bước tiếp theo là đưa tay qua trước camera để xem hình trên máy tính có thay đổi.

## 2026-11-19 — Camera đã có hình mới trên HMI

Người dùng xác nhận camera hoạt động và ESP32 mới nạp qua USB, chưa đấu cơ cấu thật. HMI đang chạy ở chế độ hardware. Ba lần đọc `/api/live.jpg` đều trả HTTP 200 và cho ba ảnh có hash khác nhau. HMI hiện yêu cầu lưu ảnh nền trống. Chạy motor, đọc IR trên cơ cấu và gạt servo thực tế: NOT_RUN.

**Đúng một việc tiếp theo:** cố định điện thoại nhìn xuống vùng đặt sách, dọn trống vùng đó rồi lưu ảnh nền bằng nút **Lưu ảnh băng tải trống**.

## 2026-11-19 — Đã ghép ESP32 với HMI qua mạng 2,4 GHz

Board trên COM5 đã lưu cấu hình. Serial báo đọc được settings, nút được nhả, ESP32 nhận IP 192.168.5.91. HMI ở chế độ hardware đã dùng mã ghép để nhận telemetry thực. Thêm kéo lên nội GPIO23 để chân ổn định khi chưa đấu nút, log chẩn đoán Wi-Fi và tắt chế độ ngủ Wi-Fi. Bản cuối nạp và kiểm tra hash thành công.

Trong 31,9 giây sau lần trả lời đầu tiên, 48/63 lần lấy mẫu HMI có trạng thái board, các lần còn lại timeout. Tất cả bản tin hợp lệ báo OFF và PWM=0. DroidCam Client đã mở trên PC, HMI báo hình đang lặp. Thử chuyển động thực tế NOT_RUN. Bằng chứng ở `data/local/station/validation/pair-check.json` và `wifi-heartbeat-upload.log`.

**Đúng một việc tiếp theo:** mở DroidCam trên điện thoại cùng mạng, kết nối với DroidCam Client và xác nhận HMI hiển thị hình thay đổi khi đưa tay qua camera.

## 2026-11-18 — Phiên 4 — Kiểm tra kết nối sau cấu hình

PC đã kết nối BEAN HONG COFFEE - 2.4Ghz và HMI thật trả lời trên localhost:8765. Windows chưa phân giải được pbl5-sorter.local. Quét Wi-Fi mới vẫn thấy PBL5-Setup với BSSID của board đã nạp. Ghép LAN chưa xác nhận. Đúng một việc tiếp theo: lưu cấu hình trên điện thoại và kiểm tra thông báo phản hồi của ESP32.

## 2026-11-18 — Phiên 3 — Đã nạp firmware trạm OK/NG

Firmware vận hành `firmware/esp32` đã nạp qua CP210x COM5. PlatformIO báo SUCCESS trong 24,60 giây trên ESP32-D0WD-V3 rev3.1 và kiểm tra hash thành công ở cả bốn vùng ghi. Sau reset, Windows thấy Wi-Fi `PBL5-Setup` của board. Log tại `data/local/station/validation/upload-COM5-20261118T112826Z.log`.

Ghép trạm với mạng LAN, chạy motor và gạt MG996R còn chờ thử. **Đúng một việc tiếp theo:** trên điện thoại, kết nối Wi-Fi PBL5-Setup và mở trang cấu hình ở `http://192.168.4.1`.

## 2026-11-18 — Phiên 2 — Trạm kiểm tra sách qua Wi-Fi

Ứng dụng Windows và firmware vận hành đã triển khai theo D26. Model thật nằm cục bộ tại `weights/best.pt`. Có HMI web, mô phỏng riêng, SQLite theo ca, chụp ảnh chỉ sau khi dừng, chống lặp theo phiên board và lượt sách. [Chạy và nạp trạm](docs/INSPECTION_STATION.md).

**Kiểm chứng trên PC.** 42 test Python PASS, gồm giao thức WebSocket loopback, lỗi Wi-Fi/camera/AI, ảnh trống, confidence thấp, dừng thủ công và chống đếm trùng. Edge đã chạy hết một lượt OK mô phỏng và đặt lại bộ đếm. Test native C++ chạy trực tiếp máy trạng thái firmware PASS. PlatformIO esp32dev build PASS. Môi trường Python riêng chạy best.pt trên một ảnh từ file. Bằng chứng cục bộ ở `data/local/station/validation/`.

**Tại thiết bị.** Driver DroidCam đã trả frame 640×480. Trong lượt kiểm tra cuối, driver lặp cùng hình và phần mềm giữ trạng thái chưa sẵn sàng. Chưa xác nhận hình sách trực tiếp, chưa đo độ chính xác tại trạm. ESP32 chưa cắm, upload và chạy motor/servo MG996R thật NOT_RUN. Hồi servo theo thời gian, vị trí cơ khí và khay vẫn chờ xác minh.

**Đúng một việc tiếp theo:** mở trạm thật, kết nối điện thoại trong DroidCam Client và xác nhận bìa sách chuyển động trong khung hình tại vị trí dừng trước khi thu mẫu hiệu chỉnh.

## 2026-11-18 — Phiên 1 — Đối chiếu bản ESP32 và chân cắm

**Bài hiện tại:** test độc lập nút bấm, IR và MG995. GPIO18 điều khiển BTS7960 RPWM, GPIO19 đọc IR active LOW, GPIO22 điều khiển MG995, GPIO23 đọc nút với điện trở 10 kΩ kéo lên 3V3. Khởi động motor tắt. Nút bật tăng PWM trong 2 giây, nút tắt đưa PWM về 0. Khi đang bật, IR LOW ngắt PWM và kích lệnh gạt 180° rồi về 0°, mỗi lệnh chờ 700 ms. Chạy lại khi đã hết thời gian servo về và IR HIGH liên tục 2 giây.

**Kiểm chứng:** đọc mã, Get-FileHash đối chiếu nguồn với bản build ngày 15/11 (PASS), Select-String đối chiếu log upload COM5 và log khởi động BUTTON_IR_SERVO tại data/local/bts7960-servo-20261115/ (PASS). Firmware chính vẫn là chương trình mẫu. Build, nạp, Serial trực tiếp và thử cơ khí trong phiên này NOT_RUN. Chưa có lỗi cơ khí mới được xác minh.

**Đúng một việc tiếp theo:** kiểm tra thực tế một chu trình bấm bật → IR nhận vật → gạt và về → chạy lại khi hết vật đủ 2 giây.

## Cập nhật 2026-11-15T17:30:59+07:00 — đã nạp MG995 gạt 180° rồi về 0°

**Bài hiện tại:** người dùng báo bản IR ổn và yêu cầu thêm/nạp servo MG995. Đã bổ sung PWM GPIO22 50 Hz, 14 bit, xung 500–2400 us, kênh servo 2 và motor 0. Khi hệ thống bật, IR LOW ngắt PWM motor rồi ra lệnh servo 180°, chờ 700 ms, về vị trí gốc quy ước 0°, chờ 700 ms. Chỉ bắt đầu ramp băng tải khi servo hết thời gian về và IR HIGH liên tục 2 giây; không gạt lặp khi còn vật. Nút OFF ngắt motor, hủy gạt và ra lệnh về 0°; bật lại giữa thời gian về vẫn phải chờ. Khởi động đưa servo về 0°, motor giữ tắt. Nguồn MG995 ngoài 5–6V, GND chung, tín hiệu GPIO22.

**Kiểm chứng PASS:** build 9,70 s; upload COM5 9,68 s, ESP32-D0WD-V3 rev3.1, Arduino-ESP32 3.3.12, xác minh hash bốn vùng; RAM 22368 B/flash 303587 B. SHA256 nguồn/bản build `5138b7c64814ce90f4c69c43265e4d95d4b24143ca81a77c32a99cfcf99661c4`. Serial `[READY] BUTTON_IR_SERVO`, GPIO23 HIGH, GPIO19 HIGH, sau thời gian về và hết vật ghi motor vẫn tắt vì nút OFF. Đã đóng Serial. Log và bản trước sửa: `data/local/bts7960-servo-20261115/`. Firmware chính/cấu hình giữ nguyên hash. Tái dùng project build `data/local/bts7960-button-only-20261115/pio`.

**Còn chờ:** góc/hành trình MG995, thời gian gạt/về và chu trình cơ khí thực tế NOT_RUN; 700 ms chỉ là thời gian chờ, chưa có feedback xác nhận góc. Không kết luận servo vật lý đã quay đúng.

**Đúng một việc tiếp theo:** người dùng bấm bật, đưa vật vào cảm biến và kiểm tra dừng → gạt 180° → về 0° → hết vật đủ 2 giây thì chạy lại.

## Cập nhật 2026-11-15T17:12:10+07:00 — đã nạp test nút + IR GPIO19, chờ hết vật 2 giây

**Bài hiện tại:** người dùng báo bản test nút đã ổn và yêu cầu thêm cảm biến. Đã bật `CONVEYOR_IR_TEST` trong `firmware/manual-tests/bts7960_button_ramp.cpp`: GPIO19 LOW ngắt PWM ngay ở lần đọc; HIGH liên tục 2000 ms mới cho ramp chạy lại 2 giây nếu nút còn bật. Vật xuất hiện lại đặt lại thời gian chờ. Có vật sẵn khi bật không chạy; nút tắt luôn ngắt PWM và ngăn tự khởi động. Servo vẫn không phát xung. Cảm biến theo cấu hình VCC 3V3/GND chung/OUT GPIO19. Bản nút trước sửa: `data/local/bts7960-ir-20261115/before.cpp`.

**Kiểm chứng PASS:** build/upload COM5, ESP32-D0WD-V3 rev3.1, Arduino-ESP32 3.3.12, SUCCESS 27,66 s, RAM 22360 B/flash 303175 B, xác minh hash bốn vùng flash. SHA256 nguồn và bản build khớp `c8e0d9b5d360c0d1e0522d827e30cf7aa3c8ea7d02b0783419d4594e5a73004c`. Serial 115200: `[READY] BUTTON_IR. PWM=0. GPIO23=LOW (release before pressing). GPIO19=HIGH (clear). Clear wait=2000 ms. Servo disabled.` Đã đóng cổng. Bằng chứng: `data/local/bts7960-ir-20261115/build-upload.log`, `serial-startup.log`. Giữ nguyên hash firmware chính/cấu hình. Nạp lại dùng project build tạm cũ ở `data/local/bts7960-button-only-20261115/pio`, hiện chứa bản IR mới.

**Còn chờ:** người dùng mới xác nhận bản nút; chu trình IR/dừng cơ khí/thời gian chạy lại thực tế NOT_RUN. PWM=0 là lệnh dừng, không chứng minh hết quán tính.

**Đúng một việc tiếp theo:** nhả nút rồi bấm bật, che cảm biến để kiểm tra dừng, bỏ vật để kiểm tra chờ 2 giây rồi bắt đầu chạy lại.

## Cập nhật 2026-11-15T16:45:34+07:00 — đã nạp bản test nút, Serial xác nhận BUTTON_ONLY

**Bài hiện tại:** người dùng xác nhận đã chuyển đầu điện trở kéo lên sang 3V3; đã nạp bản test nút theo yêu cầu trước đó. Nguồn test và bản build cùng SHA256 `63d7660743be1e3f684af7bebfe11216beaa8888a388e61089656c70643f96da`.

**Kiểm chứng PASS:** COM5 CP210x; upload nhận ESP32-D0WD-V3 revision 3.1, xác minh hash bốn vùng flash, SUCCESS 9,81 s. Serial 115200 sau reset ghi `[READY] BUTTON_ONLY. PWM=0. GPIO23=HIGH (released), external 10k to 3V3. IR/servo disabled.`, tiếp theo `[BUTTON] ON: ramp to 100% in 2000 ms.` và `[DONE] PWM=1023/1023`. Không gửi lệnh chạy từ máy tính; log chứng minh firmware nhận tín hiệu nhấn, chưa xác minh thao tác vật lý hoặc động cơ thực. Đã đóng Serial. Bằng chứng: `data/local/bts7960-button-only-20261115/upload.log` và `serial-startup.log`.

**Còn chờ:** hành vi động cơ và nút dừng thực tế chưa được người dùng xác nhận; không đánh DONE phần cứng.

**Đúng một việc tiếp theo:** người dùng bấm thêm lần nữa để kiểm tra băng tải dừng và báo kết quả.

## Cập nhật 2026-11-15T16:41:01+07:00 — bản test chỉ nút/băng tải đã build, chờ sửa mức kéo lên GPIO23

**Bài hiện tại:** người dùng yêu cầu sửa và nạp test nút trước. Đã bật `BUTTON_ONLY_TEST` trong `firmware/manual-tests/bts7960_button_ramp.cpp`: GPIO23 dùng INPUT với điện trở ngoài 10k lên 3V3; nhấn bật ramp 2 giây, nhấn tắt đưa PWM về 0 ngay; chống dội 35 ms, giữ nút không lặp. Bỏ qua cảm biến và không phát xung servo. Bản trước sửa được giữ tại `data/local/bts7960-button-only-20261115/before.cpp`; firmware chính giữ nguyên.

**Kiểm chứng:** build PASS với Arduino-ESP32 3.3.12/esp32dev, RAM 22352 B, flash 302499 B. Nguồn SHA256 `63d7660743be1e3f684af7bebfe11216beaa8888a388e61089656c70643f96da`. Phát hiện COM5 CP210x. Upload/Serial/cơ khí bản mới NOT_RUN: người dùng mô tả điện trở 10k kéo GPIO23 lên 5V, chưa xác nhận chuyển sang 3V3; đã giải thích điện trở kéo lên không hạ 5V thành 3V3. Không nạp hoặc mở Serial khi việc sửa dây chưa rõ.

**Đúng một việc tiếp theo:** người dùng ngắt nguồn, chuyển đầu điện trở từ 5V sang 3V3 và cắm lại USB; sau xác nhận sẽ nạp bản đã build theo yêu cầu sẵn có, không cần xin phép nạp lại.

## Cập nhật 2026-11-15T16:32:17+07:00 — giải thích code ESP32 và chân nối

**Bài hiện tại:** đối chiếu code test băng tải theo yêu cầu người dùng; không đổi bài thực hành hoặc mã firmware.

**Đã xác minh:** đọc toàn bộ `firmware/manual-tests/bts7960_button_ramp.cpp`; SHA256 khớp bản được nhật ký ngày 13/11 ghi đã nạp (`c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc`). GPIO18 điều khiển RPWM, GPIO23 là nút bật/tắt, GPIO19 đọc cảm biến, GPIO22 điều khiển MG995. `firmware/esp32/src/main.cpp` vẫn chỉ là code mẫu. Chu trình dùng thời gian chờ, không có phản hồi xác nhận góc servo hoặc băng tải đã dừng; PWM=0 không chứng minh cơ khí dừng tức thì. Nếu cảm biến đã bị che lúc bật, phải hết che rồi phát hiện lại mới kích gạt; sau chu trình băng tải vẫn được lệnh chạy lại kể cả còn che cảm biến.

**Kiểm chứng:** đọc nguồn và đối chiếu hash PASS; build/upload/Serial/phần cứng trong phiên này NOT_RUN. Không sửa hoặc nạp code. Chưa có lỗi mới được kiểm chứng trên thiết bị.

**Đúng một việc tiếp theo:** người dùng thử chu trình nút → cảm biến → servo → băng tải và báo hành vi thực tế; giữ nghiệm thu M14–M18 đang chờ.

## Cập nhật 2026-11-13T09:44:00+07:00 — đã biên dịch và nạp bản test BTS7960 + Hồng ngoại + Servo MG995 qua COM5

**Bài hiện tại:** người dùng yêu cầu nâng cấp mã test độc lập [bts7960_button_ramp.cpp](firmware/manual-tests/bts7960_button_ramp.cpp) (thêm cảm biến hồng ngoại vật cản 3 chân ở `GPIO19` và Servo MG995 3 chân ở `GPIO22`) và nạp trực tiếp lên ESP32 qua cổng `COM5`. Không sửa `firmware/esp32/src/main.cpp` hay `firmware/esp32/platformio.ini`.

**Đã làm:** cập nhật [bts7960_button_ramp.cpp](firmware/manual-tests/bts7960_button_ramp.cpp) (SHA256 `c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc`):
- Giữ `RPWM_PIN = 18` (`20 kHz`, `10 bit`) và `BUTTON_PIN = 23` (`INPUT_PULLUP`, chống dội `35 ms`).
- Thêm `IR_SENSOR_PIN = 19` (`INPUT_PULLUP`, mặc định `IR_ACTIVE_LEVEL = LOW`, lọc chống nhiễu `30 ms`, có khóa `irArmed` chờ vật rời cảm biến trước khi nhận chu trình mới).
- Thêm `SERVO_PIN = 22` điều khiển MG995 bằng LEDC `50 Hz` / `14 bit` (`500..2400 us`, tương thích Arduino-ESP32 core 2.x trên kênh/timer độc lập và core 3.x, không cần thư viện ngoài).
- Chu trình gạt không chặn (`millis()`, không dùng `delay()`): gặp vật cản khi đang chạy -> dừng băng tải ngay (`PWM=0`) -> quay `180°` giữ `700 ms` -> thu về `0°` giữ `700 ms` -> ramp băng tải chạy lại `0 -> 1023` trong `2.000 ms`. Nếu bấm nút tắt giữa lúc servo đang gạt thì hủy chu trình, đưa servo về `0°` và dừng băng tải.

**Kiểm chứng build & upload PASS:**
- Bản sao nguồn trong project tạm `<temporary-project>/src/main.cpp` khớp SHA256 `c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc`.
- Lệnh `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project> -t upload --upload-port COM5` **SUCCESS** (41,90 giây; `esp32dev`, Platform Espressif32 `8.0.0`, Arduino-ESP32 `3.3.12`; RAM `22.360 B`, Flash `303.359 B`).
- `esptool v5.4.0` nhận `ESP32-D0WD-V3 (revision v3.1)` trên `COM5`, ghi và xác minh hash cả 4 vùng (`bootloader.bin`, `partitions.bin`, `boot_app0.bin`, `firmware.bin`), đã hard reset qua RTS.
- `data\local\python311\python.exe scripts/check_repository.py` PASS (25 nguồn Python, liên kết tài liệu, workspace); `git diff --check` PASS. SHA256 `firmware/esp32/src/main.cpp` (`3807e1458d840c390da18bd385ad8623da514bf923311cc42ba6ce7c85a6322d`) và `firmware/esp32/platformio.ini` (`0561ad57631b44c7346b16126738eef9cbc13b464869553865e34a450f6f2bc7`) giữ nguyên.
- **Còn chờ:** thử nghiệm thực tế với nút bấm `GPIO23`, cảm biến hồng ngoại `GPIO19`, Servo MG995 `GPIO22` và động cơ băng tải `GPIO18` hiện vẫn `NOT_RUN`; chưa nghiệm thu mốc phần cứng M14–M18.

**Đúng một việc tiếp theo:** người dùng kiểm tra dây đấu (`GPIO19` cảm biến hồng ngoại nguồn `3V3`, `GPIO22` tín hiệu Servo MG995 với nguồn ngoài `5V–6V` chung `GND`), bấm nút `GPIO23` cho băng tải chạy rồi đưa vật cản qua cảm biến để xác nhận băng tải dừng ngay, Servo gạt `180°` -> về `0°`, sau đó băng tải tự chạy tiếp.

## Cập nhật 2026-11-12T14:50:02+07:00 — đã nạp test BTS7960 qua COM5 theo yêu cầu mới

**Bài hiện tại:** người dùng đổi yêu cầu thành “nạp cho tôi luôn”, cho phép nạp bản test độc lập đã tạo. Không sửa tệp nguồn hoặc cấu hình chương trình chính.

**Kiểm chứng PASS:** phát hiện COM5 (CP210x); uploader nhận `ESP32-D0WD-V3`, revision3.1. Bản sao nguồn trong project tạm khớp SHA256 tệp test `ceadabb5b13f78b07ec41f4eb82b01995d2c6a63d52df3d98f5fa7d09c463172`. Lệnh `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project> -t upload --upload-port COM5` SUCCESS, esptool xác minh hash bootloader/partitions/boot_app0/application, reset sau nạp.

**Serial PASS:** đọc COM5 ở115200 baud sau reset thấy `[READY] PWM=0. Press/release GPIO23 button to toggle 2 s ramp.`; bằng chứng serial-startup.log (hồ sơ cục bộ) nằm trong dữ liệu cục bộ. Đã đóng serial để trả cổng. Hash `firmware/esp32/src/main.cpp` và `platformio.ini` vẫn khớp bản gốc. `git diff --check` PASS.

**Còn chờ:** thao tác nút thực, đo PWM và quan sát động cơ `NOT_RUN`; log khởi động chưa chứng minh cơ khí hoạt động đúng. Không có lỗi upload còn mở; chưa nghiệm thu mốc phần cứng M14–M18.

**Đúng một việc tiếp theo:** người dùng nhấn lần1 để kiểm tra tăng tốc, lần2 để giảm về0; trong cùng lượt thử, nhấn giữa ramp và giữ nút để kiểm tra phản ứng thực tế.


## Cập nhật 2026-11-12T14:44:58+07:00 — test ESP32/BTS7960 độc lập, chờ nạp thủ công

**Bài hiện tại:** theo yêu cầu riêng, tạo đúng một tệp nguồn [bts7960_button_ramp.cpp](firmware/manual-tests/bts7960_button_ramp.cpp) nằm ngoài `firmware/esp32/src`. Không sửa mã/cấu hình firmware chính, không tự nạp board; giữ nguyên các bài và hồ sơ AI bên dưới. Test này chưa nghiệm thu M14–M18.

**Đã làm:** GPIO18 xuất PWM LEDC 20 kHz/10 bit; GPIO23 `INPUT_PULLUP`, nút thường mở xuống GND. Ban đầu duty=0; mỗi lần nhấn hợp lệ đảo đích 0/100%, ramp từ duty hiện tại tới đích mới trong 2.000 ms, kể cả giữa ramp. Chống dội 35 ms bằng `millis()`, không gọi `delay()`, giữ nút chỉ tạo một lệnh; nút bị giữ lúc khởi động phải nhả rồi nhấn lại. Có nhánh API Arduino-ESP32 2.x/3.x và hướng dẫn tạo project PlatformIO riêng trong đầu tệp.

**Kiểm chứng:** build PASS với `esp32dev`, Arduino-ESP32 3.3.12, Platform Espressif32 8.0.0 bằng `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project>`. Project tạm chỉ nhận bản sao nguồn; firmware `.elf`/`.bin` nằm dưới `.pio/build/esp32dev` của thư mục đó. RAM 22.344 B, flash 301.991 B. `git diff --check` PASS. SHA256 `firmware/esp32/src/main.cpp` vẫn `3807e1458d840c390da18bd385ad8623da514bf923311cc42ba6ce7c85a6322d`; `platformio.ini` vẫn `0561ad57631b44c7346b16126738eef9cbc13b464869553865e34a450f6f2bc7`.

**Còn chờ:** upload/Serial/PWM đo thực tế/động cơ thật `NOT_RUN`; core 2.x chưa build trong phiên này. Build và rà logic không chứng minh động cơ quay/dừng hoặc thời gian cơ khí. Không có lỗi build còn mở. Shell sandbox không khởi chạy được; các lệnh kiểm tra/build dùng thực thi ngoài sandbox đã được tự động chấp thuận, không truy cập board.

**Đúng một việc tiếp theo:** người dùng tạo project PlatformIO riêng trong VS Code, chép tệp test thành `src/main.cpp`, nạp thủ công rồi thử nhấn/giữ/nhấn giữa ramp; xem Serial 115200 baud để đối chiếu lệnh và quan sát động cơ.

## Cập nhật 2026-11-11T22:58:19+07:00 — hoàn thành lượt rà đầu 20 ảnh, đề xuất riêng

Đã thực hiện kế hoạch người dùng duyệt: khóa đúng **12 val + 8 train**, xem ảnh gốc và ảnh vẽ hộp, lưu checksum/quan sát và đề xuất từng hộp. [Quy tắc năm lớp](docs/DAMAGED_BOOKS_ANNOTATION_RULES.md) giữ mọi lỗi nhìn rõ; cho phép hai hiện tượng thật có hộp giao nhau; chưa rõ thì chờ xác nhận. [Hồ sơ 20 ảnh](docs/reviews/damaged_books_review20.json) và [script tái lập](scripts/build_damaged_books_review20.py) không xuất nhãn YOLO mới.

**Kết quả:** 32 thao tác sửa đề xuất (thêm4, bỏ nhãn sai17, chỉnh hộp7, đổi lớp3, gộp1), giữ71 hộp, 86 hộp chờ xác nhận. Theo trạng thái toàn ảnh: **3 ảnh change_proposed, 17 ảnh needs_review**, không tự duyệt ảnh nào. Trong đó9 ảnh có câu hỏi ảnh hưởng phân biệt Ripped/khay A với lỗi khác: #7,8,9,13,15,16,17,19,20. Các ảnh rỗng #12/#20 chưa được coi là mẫu âm đạt; #2 có đề xuất thêm Barcode.

**Đầu ra:** `data/local/damaged_books_v1/run2-review20/review.html`, `review-summary.csv`, `proposals.json`; mở trang bằng lệnh trong quy tắc. Trang có ảnh gốc/nhãn hiện tại/đề xuất, lọc câu hỏi A/B và bấm phóng to; nét đứt giữ hộp nguồn chưa rõ. Có chỉnh hẹp báo cáo Antigravity về hộp lồng nhau, trường JSON là danh sách, pilot15 epoch đổi lịch, và mẫu âm #20; giữ nguyên script/phần khác của tác giả.

**Kiểm chứng PASS:** 7 test bảo vệ dữ liệu; generator `--check` tái lập; repo checker25 nguồn; bộ lọc/phóng to chạy trong Edge headless/CDP (20 thẻ/60 ảnh), ảnh chụp đầu trang/#14/#20 đã xem; node kiểm DOM độc lập;617 checksum nguồn, CSV duyệt cũ và ZIP artifacts không đổi. Browser UI thông thường lỗi khởi tạo runtime; bằng chứng giao diện dùng Edge headless. Sửa lỗi encoding tiếng Việt phát hiện ở lần render đầu, kiểm lại PASS.

**Phạm vi:** chưa đọc ảnh/nhãn test, chưa tạo dataset v2, rà rộng307 ảnh, train hay tích hợp model; không stage/commit/push. Git giữ các thay đổi có sẵn và bổ sung công cụ/quy tắc/proposal/test cùng hồ sơ phiên này; dữ liệu nguồn untracked tại root không bị thêm vào Git.

**Đúng một việc tiếp theo:** mở trang đối chiếu, chọn “Câu hỏi ảnh hưởng khay A/B” và xử lý9 ảnh ưu tiên; ca không nhìn rõ cần ảnh cận/góc khác hoặc giữ chờ xác nhận, không ép thành lỗi hay mẫu âm.

## Cập nhật 2026-11-11 — đồng bộ báo cáo phân tích lần 1 và chuẩn bị bảng rà chung 20 ảnh

Đã sửa lại các sai lệch số liệu/nhận định trong [COLAB_RUN1_ANALYSIS.md](docs/COLAB_RUN1_ANALYSIS.md), cập nhật [analyze_colab_run.py](scripts/analyze_colab_run.py) và kế hoạch thực hiện theo phản hồi đối chiếu. Giữ nguyên toàn bộ tệp của Codex Astra 6 ([DAMAGED_BOOKS_RUN1_ANALYSIS.md](docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md), [DAMAGED_BOOKS_RUN1_TABLES.md](docs/DAMAGED_BOOKS_RUN1_TABLES.md), [analyze_damaged_books_run.py](scripts/analyze_damaged_books_run.py)) và các mục lịch sử bên dưới.

1. **Danh sách 20 ảnh rà chung (`12 val + 8 train`) đã đối chiếu trực tiếp từ `split_manifest.json`, tệp nhãn `.txt` và mở xem từng ảnh `.jpg`:**
   - Script [analyze_colab_run.py](scripts/analyze_colab_run.py) tự động đối chiếu từng ảnh trong danh sách 20 ảnh với `split_manifest.json` và tệp nhãn `.txt` (`audit_20_manifest_verified = true`), xác nhận chính xác `relative_path`, `group_id`, tổng số hộp và phân bố 5 lớp (ví dụ `val/images/train__IMG_1174_jpg.rf.150e452512bc5b0270247d17e32764e1.jpg` thuộc `visual_group_087` có `3` hộp: `2 Notch, 1 Wornout`; `val/images/train__IMG_1359_jpg.rf.21b7d1f92a68815a84681fa4f0b82e2b.jpg` thuộc `visual_group_076` có `0` hộp / nhãn rỗng).
   - Đã mở trực tiếp cả 20 ảnh gốc `.jpg` (và 7 ảnh gốc thuộc 5 cặp `dHash <= 10`) để ghi nhận xét thực tế trong Mục 6 của [COLAB_RUN1_ANALYSIS.md](docs/COLAB_RUN1_ANALYSIS.md). Việc rà 20 ảnh này nhằm chốt bộ quy tắc nhãn 1 trang, chưa chứng minh toàn bộ 307 ảnh `train`/`val` còn lại đã sạch.
2. **Chuẩn hóa số liệu dataset và metric:**
   - Số hộp theo lớp khớp tuyệt đối giữa hai script: `Notch` có `250` hộp `train` (`97` ảnh, `45` nhóm) và `53` hộp `val` (`22` ảnh, `10` nhóm); 3 nhóm sách lớn nhất ở `val` (`visual_group_023`, `visual_group_060`, `visually_confirmed_same_book_001`) gồm `17/54` ảnh (`31,48%`) và `186/327` hộp (`56,88%`); giao nhau `group_id` giữa `train` và `val` bằng `0` (`group_overlap_count = 0`); hộp dẹt `aspect > 10:1` gồm `37` hộp `train` (`25 Wornout, 10 Notch, 2 Ripped`) và `12` hộp `val` (`11 Wornout, 1 Ripped`).
   - Tại ngưỡng vận hành tổng hợp (`conf ≈ 0,350`), 3 lớp có `Recall = 0,000%` (và `Precision = 100,000%` do quy ước nội suy `left=1.0`) là `Notch`, `Spot`, `Wornout`; lớp `Ripped` có `Recall = 2,564%` (`1/39`) và `Precision = 72,558%`. Tách bạch rõ `AP@50`/`AP@50:95` (tích phân toàn đường cong PR) với `P`/`R` tại một ngưỡng confidence.
3. **Làm rõ bằng chứng vs giả thuyết và thiết kế thí nghiệm tách biến:**
   - Ghi nhận `erasing=0.4` và `auto_augment=randaugment` không đi vào `v8_transforms` của bài toán detection trong Ultralytics `8.4.208`; tách bạch bằng chứng `NaN`/spike trong `results.csv` với giả thuyết `lr0=0.01`/`amp=True` trên `AdamW`; tuân thủ hợp đồng `D20–D24` (ROI sách gốc + lề 5%, 5 lớp, `Ripped` luôn ưu tiên Khay A).
   - Thiết kế thí nghiệm vòng 2 tách rõ các lượt **đơn biến (1 biến mỗi lần)** (`Pilot 2A-1` chỉ hạ `lr0: 0.01 -> 0.001`; `Pilot 2A-2` chỉ đổi `warmup_bias_lr`; `Pilot 2A-3` chỉ đổi `amp`; `Run 2C` chỉ đổi dataset `v1 -> v2`; `Run 2E` chỉ đổi model `yolo11n -> yolo11s`) khỏi các lượt **nhóm cấu hình (grouped bundle)** (`Run 2D` augmentation; `Run 2F` `imgsz=960` kèm `batch`), và quy định chấm lại mọi model đối chứng trên cùng bộ `val v2` nếu nhãn `val` thay đổi.

**Đúng một việc tiếp theo:** hai bên rà chung bảng 20 ảnh tại Mục 6 của [COLAB_RUN1_ANALYSIS.md](docs/COLAB_RUN1_ANALYSIS.md) để chốt quy tắc nhãn 1 trang trước khi tạo `split-reviewed-v2` hoặc chạy `Pilot 2A-1`. Chưa train lại, chưa sửa nhãn nguồn, chưa gộp lớp, chưa đụng tập `test`.

## Cập nhật 2026-11-11 — đối chiếu độc lập artifacts lần 1, bổ sung sau phân tích song song

Đã hoàn thành phân tích độc lập trong [DAMAGED_BOOKS_RUN1_ANALYSIS.md](docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md), [bảng số liệu tính trực tiếp](docs/DAMAGED_BOOKS_RUN1_TABLES.md) và [script tái lập](scripts/analyze_damaged_books_run.py). Giữ nguyên báo cáo, script, scripts/README và mục lịch sử của Antigravity bên dưới theo xác nhận của người dùng. Đây là phân tích và đề xuất, chưa thực hiện train lần 2.

**Bằng chứng:** giải nén riêng 54 tệp vào `data/local/damaged_books_v1/codex-analysis-20261111/artifacts`, Git bỏ qua; hash ZIP và 614 tệp ảnh/nhãn train-val khớp trước/sau. Train253/val54 ảnh; không thấy sai ID, hình học hộp, dòng trùng hoặc giao nhóm/byte/pixel train-val; pHash trên13.662 cặp không có ứng viên ở Hamming≤8, chưa bảo đảm không trùng sách khác góc. Đã mở ba cặp ảnh labels/pred, đồ thị và sáu ảnh gốc; xác nhận ví dụ thiếu Barcode ở IMG_1174 và IMG_1359.

**Kết luận cần phân biệt:** macro AP50 riêng bốn lỗi chỉ3,209%; ba lớp Recall0%, Ripped2,564%; Spot/Wornout có cạnh ngắn trung vị val18px. Val loss NaN ở9 epoch và spike587,034 là bằng chứng; LR/AMP là giả thuyết cần đối chứng, chưa chứng minh quan hệ nhân quả. Đã đọc pipeline detection Ultralytics8.4.208: `erasing`/`auto_augment` là khóa classification, không áp dụng qua pipeline detection chuẩn. P=1/R=0 liên quan quy ước nội suy; không phải mô hình nhận đúng100%. Chi tiết và giới hạn của confusion matrix/ngưỡng nằm trong báo cáo.

**Kiểm chứng:** script chạy lại trên dữ liệu thật PASS; kiểm cú pháp/liên kết repo và `git diff --check` PASS. Đã có bằng chứng hoàn thành100 epoch từ artifacts; chưa đạt chất lượng AI, chưa calibrate ngưỡng hay đo camera/CPU. Không train lại, không đọc ảnh/nhãn test, không sửa nhãn, không commit/push/merge.

**Đối chiếu bản Antigravity người dùng gửi:** số ảnh/instance và tỷ lệboxnhỏ khớp; xác nhận3nhómval chiếm186/327box (56,88%). Cần sửa các lập luận vềerasing, quan hệLR→NaN, mAPtại0.35 và giả địnhA6/hai lớp cũ. ScriptdHash của Antigravity chạy lại ra5ứng viên, khác3cặp ghi trong báo cáo; đã mở ảnh để đối chiếu, không thấy cùng ảnh nhưng chưa chứng minh độc lập mọi cuốn khác góc. Chi tiết mức độ, dẫn chứng và hướng sửa ở mục đối chiếu trong báo cáo độc lập; giữ nguyên tệp của Antigravity.

**Đúng một việc tiếp theo ưu tiên theo bản đối chiếu này:** hai người rà chung20 ảnh train/val theo danh sách và quy tắc trong báo cáo để chốt vấn đề nhãn trước pilot train lần2. Đề xuất train kiểm chứng ở mục lịch sử dưới đây chưa được thực hiện; chưa gộp lớp hoặc đổi hợp đồng năm lớp.

## Cập nhật 2026-11-11 — phân tích kết quả huấn luyện Colab YOLO11n lần 1 (`20261111T132200647414Z`)

Đã giải nén gói kết quả Colab `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip` (`261.671.829` B, SHA256 `b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866`) vào `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts` (đã xác nhận `git check-ignore` qua `.gitignore:21:/data/*`, giữ nguyên ZIP gốc). Đã viết công cụ phân tích tái lập [analyze_colab_run.py](scripts/analyze_colab_run.py) và báo cáo chi tiết [COLAB_RUN1_ANALYSIS.md](docs/COLAB_RUN1_ANALYSIS.md).

Kết quả kiểm chứng và nguyên nhân chính khiến mô hình phát hiện lỗi kém (`mAP@50 = 16,17%`, `mAP@50:95 = 9,76%`, `Recall = 15,71%`, `Precision = 88,37%`):

1. **Lỗi cấu hình `optimizer='AdamW'` đi kèm `lr0=0.01`:** Truyền `optimizer='AdamW'` tường minh mà không hạ `lr0` khiến Ultralytics `8.4.208` dùng `lr0=0.01` của `SGD` (cao gấp ~9 lần mức `0,001111` của `optimizer='auto'`), làm `val/box_loss`, `val/cls_loss`, `val/dfl_loss` bị `NaN` ở các epoch `1..8`, `10` và vọt lên `val/cls_loss = 587,034` ở epoch `9`. Mô hình đã plateau từ epoch `82–97` (`best.pt` ở epoch `97`).
2. **Ngưỡng chấm điểm chung (`conf = 0.350`) và `Precision = 100%` ảo:** Đỉnh F1 của `Barcode` kéo ngưỡng chung lên `0.350`, trong khi mọi dự đoán của `Notch` (`< 0.055`), `Spot` (`< 0.215`), `Wornout` (`< 0.320`) thấp hơn ngưỡng này nên có `0` dự đoán (`Recall = 0%`, `Precision = 100%` ảo do `0/0`).
3. **Vật thể nhỏ + Augmentation xóa/thu nhỏ mạnh:** Trên tập `val`, `73,85%` hộp `Spot` (trung vị `24×20 px`), `49,06%` hộp `Notch` và `46,21%` hộp `Wornout` nhỏ hơn `32×32 px`, lại chịu `erasing=0.4`, `auto_augment=randaugment`, `mosaic=1.0` (`scale=0.5`).
4. **Nhãn nhiễu, mơ hồ giữa các lớp lỗi và thiếu nhãn ISBN:** Confusion Matrix cho thấy `30,8%` `Ripped` bị dự đoán thành `Wornout` và `10,3%` thành `Notch`; `75,5%` `Notch` và `72,3%` `Spot` bị bỏ sót thành `background`. Đối chiếu trực tiếp `val_batch0..2` phát hiện cùng một cuốn sách gán nhãn bất nhất giữa các góc chụp (`Ripped` vs `Wornout`, hộp góc vs dải dài `aspect_ratio` tới `40,5:1`), 4 ảnh `val` thiếu nhãn mã vạch ISBN làm mô hình bị phạt oan FP, và 3 nhóm sách chiếm tới `56,88%` (`186/327`) tổng số hộp của `val`.

**Đúng một việc tiếp theo:** chạy thử nghiệm kiểm chứng nhanh trên Colab (`30–50` epochs) với `lr0=0.001`, `cos_lr=True`, `erasing=0.0`, `auto_augment=None`, `scale=0.25` (và thử phương án tách `Barcode` / gộp lớp lỗi theo [COLAB_RUN1_ANALYSIS.md](docs/COLAB_RUN1_ANALYSIS.md)) trước khi quyết định rà sửa nhãn hoặc train đầy đủ lần 2. Chưa train lại và chưa đụng tập `test`.
## Cập nhật 2026-11-11 — đồng bộ GitHub cho team train song song

Đã push hồ sơ rà nhãn/nhóm còn thiếu của Gemini lên feat/damaged-books-dataset (cbe14bb), hợp nhất lịch sử vào feat/damaged-books-colab và push công cụ team (b310c53). Không merge PR vào main. Giữ bản nháp ứng dụng chưa nghiệm thu ngoài gói train và giữ dữ liệu nguồn tại máy.

Notebook tải split-reviewed-v1.zip từ GitHub Releases, kiểm SHA256 và hỗ trợ n640/s640/n960 với cùng seed42. Mỗi lượt ghi TEAM_MEMBER, EXPERIMENT, GPU, model/dataset hash, cấu hình thực tế và experiment-summary.csv. Tất cả so sánh trên validation; test chỉ đánh giá cuối. Phiên n960 chỉ thay kích thước đầu vào của ảnh nguồn640px.

Dataset361 ảnh và manifest/attribution/SHA256SUMS đã phát hành: https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/releases/tag/damaged-books-reviewed-v1 . Tải công khai ZIP12693288 byte và đối chiếu SHA256 PASS; notebook remote khớp blob commit và JSON local PASS. 111 test PASS (38.097s);check_repository/check_codex_state/diff PASS. GPU train NOT_RUN; chưa có model thắng hoặc nghiệm thu camera.

**Một việc tiếp theo:** team mở notebook trên nhánh feat/damaged-books-colab, chọn TEAM_MEMBER và chia n640/s640/n960, chạy bằng GPU riêng rồi gửi ZIP và experiment-summary.csv để so sánh. H08/A02 còn chờ phiên GPU thật. Xem docs/TEAM_TRAINING.md và docs/COLAB_TRAINING.md trên nhánh Colab.
## Cập nhật 2026-11-11 — notebook Colab YOLO11n

Đã tạo notebook độc lập `notebooks/damaged_books_colab.ipynb` và hướng dẫn `docs/COLAB_TRAINING.md` trên nhánh `feat/damaged-books-colab`, worktree `data/local/worktrees/damaged-books-colab`. Nhánh mới dựa trên commit e75eed1; giữ nguyên bốn hồ sơ chưa commit của Gemini trên worktree dataset.

Đối chiếu trực tiếp split-reviewed-v1.zip: SHA256 0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1;253/54/54 ảnh,83/18/20 nhóm,đủ5 lớp;checksum từng tệp và không giao nhau ID/nhóm/nội dung ảnh PASS. Việc này xác minh cấu trúc split, không rà độc lập lại nhận định nhãn/nhóm của Gemini.

Notebook train từ yolo11n.pt,640px,100 epoch,patience20,batch16,seed42; ghim Ultralytics8.4.208 (đã xác minh PyPI). Lưu checkpoint Drive, best.pt, cấu hình thực tế, phiên bản thư viện, báo cáo validation/confusion và ZIP. YAML chạy chỉ chứa train/val; threshold chưa chọn, test chưa đánh giá. Không triển khai ứng dụng AI.

Kiểm chứng: mã các ô compile PASS; kiểm tra gói thật PASS;6 test cổng dữ liệu PASS. Lần test đầu có lỗi fixture dùng chung list lớp, đã sửa fixture và chạy lại PASS. Chưa chạy GPU Colab, chưa có model đã train, chưa có chất lượng AI hoặc độ trễ camera.

**Một việc tiếp theo:** người dùng mở notebook trên Colab, bật GPU, tải split-reviewed-v1.zip và chạy từng ô. A02/H08 còn chờ phiên GPU thật, không đánh DONE từ notebook.
## Cập nhật 2026-11-11 — kiểm tra độc lập nhóm và tạo split `split-reviewed-v1` (H14, A01)

Đã rà soát độc lập toàn bộ 148 nhóm của 361 ảnh đạt (`grouping-assist/group-independence-sheets/groups-148-00.jpg`..`groups-148-14.jpg`): tách `idx:282` (gáy sách *다산선생 지식경영법* bị ghép nhầm vào `visual_group_026`) sang `visual_group_073`, đồng thời gộp 21 cụm nhóm cùng cuốn sách (mặt trước/gáy/mặt sau) hoặc cùng thiết kế bìa bộ sách (loại bỏ 27 mã nhóm trùng). Sau khi gộp, toàn bộ 399 ảnh có nhóm thuộc **124 nhóm trực quan**, trong đó **361 ảnh đạt (`approved`) thuộc 121 nhóm độc lập** (3 nhóm chỉ có ảnh `rejected`: `visual_group_052`, `visual_group_062`, `visual_group_111`). Giữ cách ly 259 ảnh (38 ảnh `rejected` + 221 ảnh chưa rõ nhóm).

Đã sao lưu `review-before-group-merge-42e09cf254e0.csv`, cập nhật `prepared-verified/review.csv` (SHA256 `668f59cfb4b9139896764f11dd7875b6471168c039dab523dda30348882dc183`), tạo lại `prepared-verified/review.html` và chạy `python -m vision.yolo.prepare split` tạo `data/local/damaged_books_v1/split-reviewed-v1` cùng gói `split-reviewed-v1.zip` (SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`, version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`, seed `42`):

- **Train:** **253 ảnh** (`70,08%`), **83 nhóm** (`68,60%`) — 1.399 hộp (`Barcode`: 77, `Notch`: 250, `Ripped`: 173, `Spot`: 355, `Wornout`: 544).
- **Val:** **54 ảnh** (`14,96%`), **18 nhóm** (`14,88%`) — 327 hộp (`Barcode`: 25, `Notch`: 53, `Ripped`: 39, `Spot`: 65, `Wornout`: 145).
- **Test:** **54 ảnh** (`14,96%`), **20 nhóm** (`16,53%`) — 267 hộp (`Barcode`: 13, `Notch`: 32, `Ripped`: 43, `Spot`: 60, `Wornout`: 119).
- **Quarantined:** **259 ảnh** (không sao chép vào các tập). Giao nhau nhóm giữa `train`/`val`/`test` = `0`.

H14 và A01 hoàn tất (`DONE`). Báo cáo chi tiết: `data/local/damaged_books_v1/grouping-assist/group-independence-round4.json` và `data/local/damaged_books_v1/split-reviewed-v1/split_manifest.json`. Các mục bên dưới là lịch sử.

**Đúng một việc tiếp theo:** chuẩn bị/xác minh phiên Colab GPU (`H08` / `A02`) để huấn luyện YOLO11n trên gói `split-reviewed-v1.zip` (giữ nguyên tập `test` độc lập, chỉ chọn ngưỡng trên `val`). Chưa huấn luyện trong lượt này.

## Cập nhật 2026-11-11 — rà nhãn 368 ảnh đã gán nhóm

Đã xem trực tiếp toàn bộ 368 ảnh có nhóm đang `label_review=pending` trên 46 bảng đối chiếu song song ảnh gốc / ảnh vẽ hộp nhãn (`grouping-assist/label-sheets/label-sheet-00.jpg`..`label-sheet-45.jpg`). Kết quả trên 368 ảnh: duyệt `approved` 330 ảnh có hộp và lớp đúng; đánh dấu `rejected` 38 ảnh có nhãn sai lớp (tem chữ Tag bị gán nhầm Barcode/Spot), thiếu hộp ở vết rách/mòn/bẩn rõ hoặc hộp nhiễu đè lên chữ in/hình vẽ/vệt lóa.

Tính trên toàn bộ 399 ảnh đã gán nhóm (151 nhóm trực quan): 361 ảnh `approved` (gồm 330 ảnh có hộp lỗi + 31 mẫu âm đã duyệt trước đó, phủ 148/151 nhóm với 1.993 hộp đủ 5 lớp: Barcode 115, Notch 335, Ripped 255, Spot 480, Wornout 808), 38 ảnh `rejected` và 0 ảnh `pending`. Toàn dataset 620 ảnh: 381 `approved`, 38 `rejected`, 201 `pending` (toàn bộ 201 ảnh `pending` thuộc 221 ảnh chưa rõ nhóm đang cách ly). Giữ nguyên 51/51 mẫu âm đã duyệt và không sửa tệp nhãn trong `prepared-verified`.

Đã sao lưu `review-before-label-review-076f7499062b.csv`, cập nhật `prepared-verified/review.csv` và `prepared-verified/review.html`. Kiểm chứng PASS: 620 ID duy nhất, 620 checksum ảnh và tệp nhãn khớp `manifest.json`, HTML khớp CSV, 221 ID cách ly khớp `quarantine-round2.csv`. Báo cáo chi tiết: `data/local/damaged_books_v1/grouping-assist/label-review-round3.json`, `questionable-labels-round3.csv` và `label-review-validation.txt`. Các mục bên dưới là lịch sử.

**Đúng một việc tiếp theo:** xác nhận xử lý 38 ảnh `rejected` (giữ cách ly cùng 221 ảnh chưa rõ nhóm hay tạo bản sửa nhãn mới) và kiểm tra quan hệ mặt trước/mặt sau còn nghi vấn trước khi chạy `A01` chia tập `train`/`val`/`test`. Chưa chia tập, chưa train hay tích hợp AI.

## Cập nhật 2026-11-11 — rà nhóm vòng 2

Đã xem toàn bộ 286 ảnh chưa nhóm trên bảng ảnh, đối chiếu lớn các cặp có căn cứ: thêm 65 ảnh vào nhóm và tách một nhóm ghép nhầm (sách nuôi cá / sách lãnh đạo). Hiện có 399/620 ảnh trong 151 nhóm trực quan; 221 ảnh chưa xác định được danh tính được liệt kê riêng tại `grouping-assist/quarantine-round2.csv`. Không gán ID giả cho ảnh đơn lẻ chỉ để đủ số lượng. Chưa chứng minh mọi quan hệ giữa các nhóm đã được nhận diện.

Đã lưu review.csv, sao lưu trước sửa và tạo lại review.html. PASS: giữ nguyên 620 ID và mọi trạng thái duyệt, gồm 51 mẫu âm; 620 checksum ảnh và tệp nhãn khớp manifest; HTML khớp CSV. Bằng chứng cục bộ: `data/local/damaged_books_v1/grouping-assist/round2-result.json` và `round2-validation.txt`. Các số 334/286 bên dưới là lịch sử.

**Một việc tiếp theo:** rà nhãn trên phần ảnh đã gán nhóm; 221 ảnh chưa rõ tiếp tục được cách ly. Tổng 569 nhãn còn pending; chưa chia tập, train hay tích hợp AI. Người dùng không cần nhập lại nhóm. H14/A01 chưa hoàn tất.

## Cập nhật 2026-11-11 — hỗ trợ gán nhóm bằng đối chiếu ảnh

Đã lưu 334/620 ảnh vào 124 nhóm trực quan trong `prepared-verified/review.csv`, giữ nguyên 51 kết quả duyệt mẫu âm. Còn 286 ảnh chưa xác định nhóm, để riêng; 569 nhãn vẫn pending. Nhóm đã ghi có thể cần gộp thêm khi xác định quan hệ mặt trước/mặt sau. Chưa đủ điều kiện chia tập hoặc huấn luyện.

Đã sao lưu CSV trước thay đổi và tạo lại review.html. Báo cáo cục bộ: `data/local/damaged_books_v1/grouping-assist/visual-review-report.json`. Người dùng đã giao phần rà nhóm cho trợ lý, không yêu cầu tự nhập lại 620 ảnh. Việc tiếp theo: tiếp tục xử lý các góc chụp chưa xác định; không tự duyệt nhãn còn nghi vấn.

## Cập nhật 2026-11-11 — kiểm tra CSV đã duyệt mẫu âm

Đã đọc `prepared-verified/review.csv`: 620 dòng, 620 ID duy nhất, khớp manifest; cả 51 ứng viên mẫu âm có `label_review=approved` và `negative_review=approved` theo lựa chọn người dùng. Kiểm tra lưu dữ liệu PASS, không phải đánh giá độc lập lại chất lượng nhãn. Còn 569 nhãn pending và 618 ảnh chưa có nhóm; H14/A01 chưa hoàn tất.

**Đúng một việc tiếp theo:** gán nhóm theo cuốn/thiết kế bìa trong trang review. Khi mở lại trang, nạp CSV vừa lưu trước khi sửa để giữ 51 kết quả đã duyệt. Chưa chia tập hoặc huấn luyện. Các mục bên dưới là lịch sử.

## Điểm tiếp tục mới nhất — 2026-11-10, phiên 2

Đã làm bước đầu theo kế hoạch mới: chuẩn hóa Damaged Books thành Barcode/Notch/Ripped/Spot/Wornout; giữ 620 ảnh, 3.610 hộp và 34 nhãn rỗng, bỏ 379 hộp Tag. Đối chiếu toàn bộ ảnh/nhãn với ZIP nguồn PASS; bản chuyển đổi ở `data/local/damaged_books_v1/prepared-verified`, không ghi đè nguồn.

Mã nằm trong worktree damaged-books-abc (hồ sơ cục bộ), nhánh `feat/damaged-books-dataset`; đã push commit `10b5a22` và mở [PR #11](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/11), base `feat/vietnamese-capture-ui`, chưa merge. Main vẫn `d431f10`; mã collector ở checkout chính không đổi. Kiểm tra repository/ledger PASS; 102 test PASS (93 hồi quy collector + 9 test dataset). CI remote cần phân biệt với test local, xem PR.

Split cũ 618/1/1 không dùng để đánh giá và có cặp cùng cuốn giữa train/test. Chưa tạo split mới: 620 ảnh chưa duyệt nhãn, 618 ảnh chưa có nhóm, 51 ứng viên mẫu âm chưa duyệt. Chưa train hay nghiệm thu AI/camera/simulator trong bước này.

**Đúng một việc tiếp theo:** mở review.html (hồ sơ cục bộ), rà nhóm theo cuốn/thiết kế và nhãn, kiểm riêng 51 ứng viên âm rồi tải `review.csv`. Hướng dẫn (hồ sơ cục bộ) · TASKS (hồ sơ cục bộ). Các phần phía dưới giữ nguyên làm snapshot phiên 1 và lịch sử.

Cập nhật: 2026-11-10 — phiên 1 (đối chiếu main, worktree phát triển và GitHub; chạy lại test cả hai bản).

Repository: [pbl5-library-book-inspection](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection). Đã đọc lại remote SHA và trạng thái PR trong phiên; không kiểm tra lại CI.

## Phân biệt bản đang mở và bản phát triển

- Checkout đang mở là `main`, commit `d431f10`, trùng remote main. Trước phiên đã có sửa chưa commit ở `PROGRESS.md` và `docs/SESSION_LOG.md`; không có sửa mã nguồn được Git báo cáo.
- Worktree phát triển sạch ở nhánh `feat/vietnamese-capture-ui`, commit `bdf0c00`, trùng remote nhánh đó. Bản này đã gồm V02 (preview độc lập geometry/QR), V07 (cải tiến bìa sáng/tối và nhiều nền), V08 (giao diện tiếng Việt).
- PR #5, #6, #9, #10 vẫn OPEN, chưa merge; vì vậy các cải tiến trên chưa có trong main. PR team #7 (kiểm bundle/pilot) và #8 (phương án detector/UI khác) cũng OPEN, chưa được audit/test trong phiên này; không suy hoàn thành từ tiêu đề PR.
- Hồ sơ ngày 2026-11-09 đúng với checkout main nhưng thiếu tiến độ ở worktree khác. Không dùng các lỗi preview/thiếu cải tiến trên main để kết luận toàn dự án chưa làm chúng.

Tiến độ task của bản phát triển xem [TASKS tại commit đã kiểm](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/blob/bdf0c007331c896ae6ec678b3a6d53ec66b4be17/docs/codex/TASKS.md); điểm tiếp tục xem [STATE](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/blob/bdf0c007331c896ae6ec678b3a6d53ec66b4be17/docs/codex/STATE.md). Bảng dưới tổng hợp mốc, không thay ledger của nhánh phát triển.

## Mốc hiện tại

**M02 — OpenCV xác định vùng sách/crop bìa: IN_PROGRESS, chờ kiểm chứng ảnh/camera thật trên bản mới.** V02/V07/V08 đã hoàn thành acceptance phần mềm theo ledger và test chạy lại; không đồng nghĩa M01–M05 đã được nghiệm thu. Việc rà soát này không xác nhận người dùng đã hoàn thành thêm bài thực hành nào.

| Hạng mục | Trạng thái | Bằng chứng và phần còn thiếu |
|---|---|---|
| Cấu trúc repository và hướng dẫn nhóm | DONE | Kiểm tra cấu trúc cả main và bản phát triển ngày 2026-11-10 PASS; bản phát triển có thêm task ledger/resume validator |
| M01 Camera | IN_PROGRESS | Có CameraAdapter và test frame mới/mất frame; hồ sơ 2026-10-29 ghi DirectShow 1280×720; chưa nghiệm thu độ ổn định webcam/chạy dài |
| M02 Geometry/quality | IN_PROGRESS | V07 đã cải tiến chọn mép và chất lượng bìa sáng/tối, có hồi quy tổng hợp; V01 còn chờ ảnh lỗi thật, V03 còn chờ kiểm chứng camera |
| M03 QR | IN_PROGRESS | Có parser PBL5/LIB1 và decoder; đã đọc B08 trong lần thử cũ; chưa đánh giá trên nhiều bìa |
| M04 Database | TODO | Chưa có SQLite/lookup danh tính; metadata hiện để identity_status=NOT_CHECKED |
| M05 Capture | IN_PROGRESS | Có raw/crop/debug/metadata và manifest; bản phát triển có preview độc lập và UI tiếng Việt; chưa nghiệm thu pilot thật, PR kiểm bundle #7 chưa được audit phiên này |
| M06–M09 Dataset, AI, threshold, policy | TODO | vision/yolo mới có README; chưa có code train/inference hoặc model dự án được kiểm chứng |
| M10–M13 Backend, Web HMI, simulator, protocol | TODO | Chưa có các module này trong mã sản phẩm hiện tại |
| M14 Firmware chức năng | TODO | main.cpp vẫn là template; build mẫu trước đây không chứng minh có state machine/giao thức điều khiển |
| M15–M18 Cơ cấu và feedback | TODO | Chưa có bằng chứng nghiệm thu phần cứng trong hồ sơ hiện có |
| M19–M27 Tích hợp, đánh giá và bàn giao | TODO | Chờ các module và kiểm chứng thiết bị |

## Kiểm chứng ngày 2026-11-10

| Kiểm tra | Kết quả | Phạm vi |
|---|---|---|
| Main: `.venv\Scripts\python.exe scripts/check_repository.py` | PASS | 21 tệp Python, liên kết tài liệu và đường dẫn workspace |
| Main: `.venv\Scripts\python.exe -m unittest discover -s tests -v` | PASS | 22/22 test, 4.085 giây; ảnh tổng hợp/camera mô phỏng/lưu dữ liệu/entrypoint |
| Bản phát triển: `scripts/check_repository.py` và `scripts/check_codex_state.py` | PASS | 34 tệp Python; cấu trúc/liên kết và tính nhất quán task/state; validator không xác minh thiết bị |
| Bản phát triển: `python -m unittest discover -s tests -q` | PASS | 93/93 test, 15.980 giây, commit sạch `bdf0c00`; dùng cùng interpreter venv của main, cwd là worktree phát triển |
| `git ls-remote` và GitHub REST GET pull requests | PASS | Main `d431f10`, V07 `9123758`, V08 `bdf0c00`; PR #5–#10 OPEN, merged_at=null; CI không kiểm lại |
| Webcam thật, pilot nhiều bìa | NOT_RUN | Không mở camera trong phiên rà soát |
| Firmware build/upload, cơ cấu thật | NOT_RUN | Không build, nạp hoặc chạy thiết bị trong phiên này |
| AI và end-to-end | NOT_RUN | Module chưa được triển khai đầy đủ; chỉ số hiện tại N/A |

Đã đọc diff hồ sơ, danh sách worktree/nhánh, mã collector/worker/geometry/UI, metadata, template firmware và ledger ở bản phát triển. Phiên này chỉ cập nhật hồ sơ tại checkout chính; không sửa mã sản phẩm, chuyển nhánh, merge hoặc bắt đầu task kế tiếp.

## Bằng chứng lịch sử — không phải kết quả đo mới

Ngày 2026-11-07 và 2026-11-09 tại main: kiểm tra repository PASS; 22/22 test Python PASS lần lượt trong 9.008 và 8.120 giây. Chi tiết giữ trong [nhật ký](docs/SESSION_LOG.md).

Theo [báo cáo kiểm chứng](docs/COVER_CAPTURE_VALIDATION.md) và [nhật ký](docs/SESSION_LOG.md) ngày 2026-10-29:

- 23 test mô phỏng tiện ích camera Windows PASS; chưa chạy lại phiên này.
- Firmware mẫu BUILD PASS; chưa có xác nhận upload hoặc vận hành cơ cấu.
- CLI/GUI trên ảnh tổng hợp và khôi phục manifest đã hoạt động.
- Với 12 khung bìa B08: 5 khung đọc được QR, 7 khung dừng ở geometry, 0 READY. Đây là thử nghiệm một bố trí, không phải độ chính xác tổng quát.

## Lỗi còn mở

- Main còn bộ chọn tứ giác cũ và preview đồng bộ. Bản phát triển đã có V02/V07; cần dùng đúng bản khi thử và không triển khai lặp các sửa này.
- V07 mới có bằng chứng hồi quy tổng hợp; chưa xác minh độ ổn định mép ngoài trên bộ ảnh lỗi/camera thực tế. V01/H04/V03 vẫn chờ đầu vào và kiểm chứng theo ledger.
- Chưa có pilot nhiều bìa xác nhận chất lượng thu dữ liệu. Nhãn READY chỉ là đủ điều kiện thu ảnh/QR, không phải kết luận sách không lỗi.
- Các PR phát triển chưa merge; PR #8 chồng lấn detector/UI với #9 nên cần review trước khi tích hợp. Không coi code trên nhánh riêng là đã có trong main.

## Đúng một việc tiếp theo

**Kiểm chứng crop bằng camera thật trên bản mới `feat/vietnamese-capture-ui`:** giữ camera cố định, bắt đầu với một bìa sáng và một bìa tối; hiệu chuẩn B khi nền trống, kiểm bốn góc/crop/QR và lưu raw/crop/debug/metadata cùng ca lỗi. Dữ liệu này phục vụ V01/V03; nếu còn chọn sai mép thì tái hiện trên ảnh đã lưu trước khi sửa. Bộ 10–20 cuốn trong roadmap là bước kiểm rộng hơn, chưa tự coi là gate định lượng đã duyệt. Còn chờ người dùng thực hành và bằng chứng thực tế; chưa chuyển bài hoặc đánh DONE-HW.

Ledger đề xuất B01 (schema SQLite/migration) là task code độc lập tiếp theo; B01 chưa bắt đầu. Thông tin này không thay bài kiểm camera đang chờ và không phải yêu cầu triển khai thêm trong phiên rà soát.

Lộ trình sau M02 giữ theo [PLAN.md](docs/PLAN.md): hoàn thiện thị giác/dữ liệu → AI/policy → backend/HMI/mô phỏng/giao thức → phần cứng/feedback → tích hợp/đánh giá/bàn giao.

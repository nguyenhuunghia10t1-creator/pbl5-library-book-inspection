# Quyết định thiết kế

Cập nhật: 2026-10-29.

| ID | Quyết định | Cơ sở |
|---|---|---|
| D04 | OpenCV cho thu ảnh/geometry/QR; YOLO11n là hướng AI ban đầu; FastAPI và SQLite cho giai đoạn tích hợp | Tách xử lý thị giác, dữ liệu và điều phối |
| D05 | Băng tải cố định, hai nhánh A/B và tuyến HOLD | Phân tách sách theo nhóm và ngoại lệ |
| D06 | Hai lớp lỗi: cover_tear và surface_stain | Giới hạn bài toán kiểm tra bìa ban đầu |
| D07 | Một sách/job tại một thời điểm, liên kết bằng UUID | Tránh ghép ảnh và kết quả sai cuốn |
| D09 | Có trạng thái UNCONFIRMED cho lượt xử lý thiếu xác nhận | Không tự hoàn tất job khi mất liên lạc |
| D10 | Lưu riêng simulation/hardware và expected_route/actual_route | Phân biệt lệnh dự kiến với kết quả được xác nhận |
| D11 | Giữ raw bất biến; chia dataset theo cuốn/thiết kế bìa | Truy vết nguồn và tránh rò rỉ train/test |
| D16 | Collector hỗ trợ PBL5-B + 2–6 chữ số và LIB1:copy_id | Tương thích mã bìa đã in; chưa thay thế tra cứu DB |
| D17 | Crop mặc định 630×888; lưu raw/crop/debug và metadata | Chuẩn hóa ảnh nhưng bảo toàn nguồn |
| D18 | Tách firmware, vision, software, tests, scripts, examples và data | Phát triển theo module và review độc lập |
| D19 | Repository public quản lý mã và tài liệu kỹ thuật; main dùng PR/review/CI | Dữ liệu camera, weights, credentials và hồ sơ cục bộ nằm ngoài Git |
| D25 | ĐÃ DUYỆT 2026-11-11: lượt rà 20 ảnh theo hợp đồng mới năm lớp; gán mọi lỗi nhìn rõ, không đặt ngưỡng pixel tùy ý; cho phép hai hiện tượng thật có hộp giao nhau; vùng chưa rõ chờ xác nhận | Kế hoạch người dùng duyệt chỉ lập đề xuất, giữ nguồn/split/test và review cũ; chưa tạo v2/train. [Quy tắc](DAMAGED_BOOKS_ANNOTATION_RULES.md). D20–D24 nằm trên nhánh Colab; D25 chỉ bổ sung quy tắc rà, không sửa collector legacy ở checkout này. |

## Trạng thái dữ liệu

**Điều chỉnh D26, 2026-11-19.** Theo yêu cầu của người dùng, ESP32 và Python trao đổi qua cầu USB–UART ở 115200 baud. Mã lượt gồm phiên khởi động và số sách. Python chỉ ghi nhận quyết định sau ACK đúng mã. Điện thoại vẫn có thể gửi ảnh DroidCam qua mạng tới PC. [Giao thức và cách thử](INSPECTION_STATION.md).

**D26 update, 2026-11-20 (accepted).** Both commissioning and automatic sorting use the USB firmware. Manual Mechanics accepts an operator decision for a single active capture, with an eight-second PC window and a separate history. AI Inspection requires an independently tested camera profile and a passing fixed damaged-cover challenge. Strict NG can reject uncertain predictions from valid images; device failures still stop motion. File-image simulation uses an isolated profile for offline practice. [Operator quick start](STATION_QUICKSTART.html).

**D26 update, 2026-11-21 (accepted).** Use the new ESP32 as a USB-to-ESP-NOW bridge so the conveyor can stay installed without a data cable between the boards. Windows keeps the existing 115200-baud protocol. The bridge uses a fixed channel and a private peer key. Acknowledgements, interlocks and motion belong to the conveyor receiver. [Bridge protocol](../firmware/espnow-bridge/README.md).

**Thử camera và AI trên PC (đã chọn ngày 2026-11-19).** Khi ESP32 chưa đấu cơ cấu, người dùng muốn tự bấm chụp một ảnh để xem top-1 của mô hình. Chế độ `camera-test` chạy riêng, dùng DroidCam và weights thật. Ảnh thử thủ công không tham gia hiệu chỉnh ngưỡng hay điều khiển phân loại của trạm. [Cách mở chế độ thử](INSPECTION_STATION.md).

**D26 — Trạm vận hành OK/NG (đã chọn ngày 2026-11-18).** Bố trí một trạm, một cuốn mỗi lượt. Chạy model phân loại trên Windows, bỏ yêu cầu QR trong quyết định OK/NG và dùng WebSocket cục bộ đến ESP32. Dùng lại bốn GPIO của bài test, chuyển servo sang MG996R. Người dùng chọn hồi theo thời gian, chờ thêm 2 giây và chấp nhận giới hạn khi cơ cấu kẹt. `actual_route` để trống nếu thiếu bằng chứng tại khay. [Cấu hình và vận hành](INSPECTION_STATION.md).

QR: VALID_FORMAT, UNREADABLE, INVALID_NAMESPACE, INVALID_FORMAT, AMBIGUOUS. VALID_FORMAT chỉ xác nhận cú pháp. Identity: NOT_CHECKED, VALID, UNKNOWN_ID; chỉ lookup DB mới xác nhận danh tính.

AI quality dự kiến: PASS, REVIEW, DEFECT; chưa inference hoặc ảnh không đủ điều kiện thì quality để null. Route: A, B, HOLD, STOP. Job dự kiến: PENDING, RUNNING, WAIT_CONTROLLER, COMPLETE, FAULT, UNCONFIRMED.

## Điều kiện kỹ thuật cần xác minh

- Camera, ánh sáng, độ phân giải và ngưỡng chất lượng trên bộ bìa pilot.
- Board thực tế, pin map, điện áp/tải, sensor và feedback cơ cấu.
- Framing serial, checksum, timeout/retry và xử lý trùng yêu cầu.
- Phiên bản dataset/model, ngưỡng AI và tiêu chí nghiệm thu.

Cấu hình PlatformIO hiện là esp32dev + Arduino cho firmware mẫu. Chưa phải xác nhận pin map hoặc thiết kế điện của hệ thống.

**2026-11-23 — Camera USB cho trạm (đã chọn).** Theo yêu cầu chạy trực tiếp trên PC, trạm dùng A4tech HD 720P PC Camera qua MSMF. Ảnh nền được lưu theo nguồn camera. Giao diện chính và trang thử AI xem luồng MJPEG riêng với trạng thái máy. [Hướng dẫn](INSPECTION_STATION.md).

**2026-11-23 — Chạy thật theo nhãn cao nhất (đã chọn).** Người vận hành ưu tiên thử luồng cơ khí trước khi đánh giá độ chính xác. Launcher DirectSorting bật tùy chọn --direct cho phiên. Job có tín hiệu CAPTURE từ ESP32 dùng toàn khung USB mới sau khoảng dừng. Mỗi nhãn hợp lệ được ánh xạ sang OK hoặc NG, kể cả độ tin cậy thấp. Bảo toàn kiểm tra ảnh mới, thời hạn, mã job, ACK, nút vật lý và chống kẹt. [Vận hành](INSPECTION_STATION.md).

**2026-11-23 — HMI vận hành tiếng Việt (đã áp dụng).** Lịch sử và KPI cùng ca; hiển thị nhãn model, quyết định và kết quả chu kỳ riêng. Manual dùng nút OK/NG cùng thời hạn backend, Simulation có vùng chọn nguồn riêng. Duy trì Start/dừng vật lý. Cài đặt Direct tách khỏi hồ sơ hiệu chuẩn. [Vận hành](INSPECTION_STATION.md).

**2026-11-23 — Diện mạo và ngôn ngữ của HMI (đã áp dụng).** Bố cục dùng nền sáng cho dữ liệu, vùng xem camera tối và thanh điều hướng cố định. Khi mất hình, hiển thị sơ đồ vị trí camera, sách và băng tải cùng thông báo. Hướng dẫn, lỗi và đơn vị đo dùng tiếng Việt; mã thiết bị, lệnh truyền và nhãn sách giữ nguyên để đối chiếu với nhật ký.

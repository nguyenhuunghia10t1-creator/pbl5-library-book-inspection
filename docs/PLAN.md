# Kế hoạch kỹ thuật

## HMI vận hành — 2026-11-23

Nghiệm thu phần mềm theo từng chế độ, bằng dữ liệu lịch sử và kích thước viewport. Nghiệm thu cơ khí còn cần receiver và webcam online, một lượt OK và một lượt NG có quan sát tại khay.


## Chạy hai tuyến theo nhãn trực tiếp — 2026-11-23

Dùng [DirectSorting.cmd](../scripts/windows/DirectSorting.cmd) để thử cơ cấu bằng quyết định hai lớp của model. Nghiệm thu bằng lượt OK và NG trên băng, ghi phản hồi ESP32 và quan sát sách đến khay. Chế độ hiệu chỉnh riêng vẫn dùng InspectBooks.cmd.

## Two-board radio link — 2026-11-21

The paired boards returned six status replies with the conveyor receiver installed. Firmware reported complete manual OK and NG cycles. Recheck the physical NG route after the fourth job stopped with `NG_NOT_CLEAR`, then verify camera freshness and run the known-book checks before enabling automatic operation. [Progress](../PROGRESS.md) · [Bridge protocol](../firmware/espnow-bridge/README.md).

## Trạm OK/NG một vị trí — thiết kế USB ban đầu, 2026-11-18

Bước thử riêng trên PC theo yêu cầu 2026-11-19 dùng [TestCameraAI.cmd](../scripts/windows/TestCameraAI.cmd). Nghiệm thu khi người dùng đặt một cuốn sách trước camera USB, bấm chụp và thấy đúng ảnh vừa chụp cùng nhãn và độ tin cậy. [Tiến độ](../PROGRESS.md).

Phần mềm Windows, HMI, mô phỏng và firmware MG996R dùng USB Serial 115200 giữa ESP32 và PC theo cập nhật ngày 2026-11-19. M01–M02, M08–M09 và M14–M24 cần bằng chứng trên đúng camera, nguồn và cơ cấu. Kiểm tra bắt tay COM khi chưa cấp nguồn tải, kiểm tra camera và AI tại vị trí dừng, sau đó thử từng tải, rút USB giữa lượt và pilot 30 lượt. [Tiêu chí từng bước](INSPECTION_STATION.md).

## Cập nhật 2026-11-11 — lượt rà nhãn 20 ảnh

Theo kế hoạch người dùng duyệt, bước hiện tại của dữ liệu AI là khóa 12 ảnh val + 8 ảnh train, áp dụng [quy tắc năm lớp](DAMAGED_BOOKS_ANNOTATION_RULES.md) và lập đề xuất riêng, chưa xuất nhãn v2. Lượt rà đầu đã hoàn thành; còn 17 ảnh có câu hỏi, ưu tiên 9 ảnh cần phân biệt Ripped với lỗi khác. Bước tiếp theo là xử lý các ca chưa rõ trên trang đối chiếu cục bộ. Rà rộng 307 ảnh và pilot Colab chưa bắt đầu; các mục collector bên dưới giữ làm lịch sử kế hoạch checkout legacy.

Các mốc dùng mã M01–M27 để theo dõi từ module độc lập tới nghiệm thu hệ thống. Trạng thái hiện tại xem [PROGRESS.md](../PROGRESS.md).

| Giai đoạn | Mốc | Đầu ra chính |
|---|---|---|
| Thị giác và dữ liệu | M01 Camera, M02 Geometry/quality, M03 QR, M04 Database, M05 Capture | Ảnh có nguồn gốc, identity và kết quả truy vết được |
| AI | M06 Nhãn/split, M07 YOLO baseline, M08 Threshold, M09 Decision policy | Dataset được kiểm, model có đánh giá, luật phân loại độc lập thiết bị |
| Phần mềm | M10 Backend, M11 HMI, M12 Simulator, M13 Protocol | Luồng job tái hiện được và hợp đồng giao tiếp có test |
| Điều khiển | M14 Firmware, M15 Băng tải, M16 Pusher A, M17 Pusher B, M18 Feedback | Từng cơ cấu được thử an toàn, xác nhận đầu ra thực |
| Tích hợp | M19 End-to-end, M20 Fault/recovery | Một sách/job, xử lý ngoại lệ và phục hồi |
| Đánh giá | M21 AI, M22 QR, M23 Cơ khí, M24 Toàn hệ thống | Chỉ số đo trên bộ thử có điều kiện rõ ràng |
| Bàn giao | M25 Freeze, M26 Demo, M27 Handover | Phiên bản đã kiểm thử, tài liệu và hướng dẫn vận hành |

## Công việc trước mắt

- Sửa chọn tứ giác trên nền có đường ron, kiểm thử hồi quy với ảnh đã thu.
- Cải thiện tốc độ preview; giữ liên kết frame/QR/metadata khi xử lý bất đồng bộ.
- Thu pilot với camera cố định, ánh sáng ổn định và nhiều thiết kế bìa.

## Điều kiện nghiệm thu

Mỗi mốc cần đầu ra thực và bằng chứng phù hợp. Test tự động, test mô phỏng, camera và phần cứng được ghi riêng. Một module build được chưa đủ để nghiệm thu vận hành thiết bị. Chia dataset theo cuốn/thiết kế bìa và giữ tập test cuối độc lập.

Thay đổi giao thức, dữ liệu hoặc phạm vi được ghi tại [DECISIONS.md](DECISIONS.md).

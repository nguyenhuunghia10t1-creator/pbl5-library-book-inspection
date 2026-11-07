# V07 — Nhận mép bìa sáng ít tương phản

## Lỗi và phạm vi sửa

Người dùng báo chỉ nhận được bìa tối, bỏ sót vàng nhạt/xanh nhạt; xác nhận chưa hiệu chuẩn B với bàn trống. Detector cũ có mask khác màu nền Lab (default 22) và Canny ảnh xám (45/130). Mép ít tương phản có thể nằm dưới cả hai ngưỡng; màu khác nhau nhưng có cùng mức xám cũng mất tín hiệu khi chuyển grayscale. Đây là lỗi tìm biên, không phải phân loại màu hay suy luận YOLO.

V07 giữ hai nguồn ứng viên cũ và bổ sung Canny riêng từng kênh BGR đã làm mượt. Ngưỡng cao là max(12, 3 × median độ lớn gradient L1), ngưỡng thấp bằng 0.4 lần ngưỡng cao; có sàn nhiễu, bỏ kênh gần phẳng. Hợp các biên màu, đóng khe nhỏ rồi đưa qua cùng bộ lọc diện tích/tứ giác lồi/tỉ lệ/coverage, chọn ứng viên và kiểm nhiều bìa. Mã nguồn đầu vào không bị sửa tại chỗ.

Các hệ số trên là mặc định thuật toán được kiểm bằng fixture, **không phải ngưỡng nghiệm thu hardware đã duyệt**. Giữ nguyên ngưỡng chất lượng, parser QR, raw bất biến, crop 630×888, schema bundle, camera/backend và firmware.

## Bằng chứng phần mềm

Môi trường phiên này: Windows 11 build 26300, PowerShell 7.6.9, Python 3.13.14, OpenCV 5.0.0, NumPy 2.5.4; venv đã có, không cài dependency.

- Baseline nhánh V07 từ commit sạch 8f9198f (V02): 71 tests PASS, checker/validator/whitespace PASS. Nhánh V05 có 21 test audit riêng trong PR #7, không được trộn vào PR sửa geometry này.
- Trước sửa: `tests.opencv.test_light_covers` chạy 11 tests, 27 failure/subtest, tái hiện bỏ sót vàng/xanh/trắng và màu cùng grayscale.
- Thử biên trên Lab còn một ca xanh nhạt có nhiễu thất bại: contour kín lớn nhất 69.5 px² thay vì khoảng 80,543 px². Với cùng ảnh/ngưỡng, biên BGR có contour ngoài 81,419 px²; chuyển trực tiếp từ BGR tránh mất tín hiệu do lượng tử hóa Lab. Giữ Lab cho mask nền như cũ.
- Bộ riêng cuối: 14 tests PASS lúc 2026-11-07T11:00:56+07:00, 2.102s, failures/errors/skips=0. Kết quả bộ đầy đủ và commit/PR được nối ở SESSION_LOG phiên 7.
- Bộ đầy đủ source: checker PASS (27 source), validator PASS, **85 tests PASS**, failures/errors/skips=0, 8.816s lúc 2026-11-07T11:02:30–11:02:40+07:00, HEAD 8f9198f + working-tree changes. GUI và headless lúc 11:04:07–11:04:11+07:00 cùng nhận READY/PBL5-B04 trên fixture vàng nhạt; đã xem crop và bốn góc trong screenshot cục bộ.
- Đã mở lại preview với camera 1/MSMF lúc 11:04:39+07:00; driver báo 1280×720/30fps (không phải phép đo FPS thật). Live/Analyzed tăng nhưng hình tại lần quan sát là đen nên **chưa xác nhận bìa sáng thật**; cần nguồn ảnh DroidCam và bài thử dưới đây. Không nâng V01/V03 thành hoàn thành từ việc mở được backend.

| Ca tổng hợp | Kiểm tra |
|---|---|
| Vàng nhạt, xanh nhạt, trắng, màu cùng grayscale | Mép ngoài, xoay 0°/27°/90°, có/không hiệu chuẩn và phối cảnh |
| Chữ/QR tối trên bìa sáng | Không lấy QR/hình in thay mép ngoài; đọc PBL5-B04 và crop 630×888 |
| Nhiễu nhỏ, đổi phơi sáng toàn ảnh, nền có vân | Giữ được mép ngoài; kiểm cùng điều kiện có/không hiệu chuẩn |
| Nền trống sáng/tối, gradient sáng, nhiễu mạnh, ellipse/tam giác | Không tự tạo bìa |
| Bìa tối, hai bìa sáng, bìa bị cắt mép | Hồi quy phát hiện tối, nhiều bìa, chạm khung |
| Chưa có QR, quá sáng | Không nâng thành READY; vẫn giữ quality gate |

Fixture warp dùng BORDER_REPLICATE để không vô tình vẽ viền đen ở mép bìa — một viền đen giả sẽ che mất lỗi cần tái hiện. Test so byte ảnh trước/sau detector để bảo vệ raw. Toàn bộ fixture tự tạo, không dùng làm bằng chứng độ chính xác trên sách/camera thật.

## Thử lại với camera

Dùng venv đã xác minh và index/backend đã hoạt động. Ví dụ máy hiện tại dùng `--camera 1 --backend msmf`; index có thể đổi khi thay thiết bị.

1. Giữ camera cố định nhìn xuống, nền tương đối đồng nhất và ánh sáng đều. Để bàn trống, chọn cửa sổ OpenCV, bấm B; sau đó đặt nguyên bìa vào giữa khung.
2. Thử lần lượt bìa tối/vàng nhạt/xanh nhạt/trắng. Kiểm bốn góc bám mép giấy thật và crop không lấy hình in bên trong. READY còn cần QR, độ nét, ánh sáng và ổn định đạt điều kiện.
3. Chỉ lưu S khi đúng; D là review. Khi đổi vị trí camera/ánh sáng/nền, lấy sách ra và hiệu chuẩn lại. Nếu phím tắt không nhận do bộ gõ, dùng bàn phím ENG; M bật/tắt ảnh đóng băng chọn góc.

Chưa có mẫu thật H04 với mép chuẩn được xác nhận để kết luận V01 hoặc DONE-HW V03. Nền có đường ron, hình chữ nhật trên bìa, bóng đổ, lóa, nền gần cùng màu hoặc camera rung vẫn có thể gây sai. Không tự đổi trạng thái V01/V03/V06, không tự đặt KPI/cỡ mẫu; gửi bộ thử/video/bundle vào chỗ riêng ngoài Git khi nghiệm thu.

# Kiểm chứng V07: màu bìa và nền

Ngày 2026-11-07. Chỉ kiểm chứng phần mềm trên Windows 11/PowerShell 5.1, Python 3.14.3, OpenCV 5.0.0, NumPy 2.5.3. Baseline là commit sạch `8f9198f0c78030dd21000f4562a0492556c1dce2` của V02; kết quả V07 trước commit ghi **HEAD + working-tree changes** trong SESSION_LOG. Không thêm dependency/model, không mở webcam hoặc điều khiển ESP32.

## Thay đổi được kiểm

- Foreground Lab giữ thông tin sáng/màu; cạnh Canny trên ba kênh có ngưỡng median/MAD thích nghi. Cạnh yếu chưa khép kín được dùng đề xuất convex hull, sau đó vẫn phải qua kiểm cả bốn cạnh.
- B so từng vị trí với nền trống đã làm mượt giống frame hiện tại; trừ dịch Lab chung từ viền ảnh, lọc nhiễu theo median/MAD. Đổi bố trí/camera/nền cần hiệu chuẩn lại.
- Xếp ứng viên theo hình học, hỗ trợ cạnh yếu nhất, dải trong/ngoài ở hai khoảng cách và foreground; loại chạm biên, ưu tiên mép ngoài có căn cứ. Previous chỉ phân xử ứng viên mới gần điểm số, không giữ khung cũ sau khi sách rời đi.
- Giữ brightness/sharpness toàn crop để đối chiếu, thêm detail_sharpness/focus_measurable/detail_tiles, clipped_high/low_fraction và brightness_outside_legacy_range. Không tự chặn bìa trắng vì brightness trung bình cao; ít chi tiết có FOCUS_UNVERIFIED và QUALITY_WARNING. Thiếu nét trên chi tiết vẫn BLURRY, clipping gần toàn vùng vẫn BAD_LIGHT.
- Giữ chữ ký detect/process, parser QR, hướng crop, Result và bundle schema. Helper order_quad/quad_ratio/corner_motion vẫn import được từ pipeline. Worker V02/camera/storage không thay đổi; UI chỉ bổ sung chẩn đoán.

## Fixtures và cách đo

`tests/opencv/color_fixtures.py` sinh 25 cảnh 800×600 có góc ngoài chuẩn: trắng/kem/đen/xanh/đỏ × nền sáng/tối/texture/ron; thêm gần trắng, gần mức xám nhưng khác màu, xoay 27°, phối cảnh với gradient, nền checker. Chạy mỗi cảnh tự động và sau B thành 50 ca. QR và viền in nằm trong bìa để bắt lỗi chọn nhầm mép trong.

Mỗi ca phải có crop 630×888 và khoảng cách góc tệ nhất <10px ở ảnh gốc, so thứ tự cyclic với ground truth; giữ giới hạn hồi quy cũ. Ba ca trắng/đen phối cảnh/xoay còn so pixel BGR trong crop với phép warp từ ground truth, mean absolute error <10/255, bỏ dải mép warp (45px dọc/32px ngang). Đây là giới hạn fixture, không là ngưỡng nghiệm thu camera.

Các test còn kiểm nền trống auto/B, thay sáng chung, đổi nền/hiệu chuẩn lại, lấy sách ra, ranh giới không quan sát được kể cả có viền in, QR bìa sáng/tối, cấu hình JSON cũ và ngưỡng không hợp lệ, bìa trơn/ít chi tiết, ảnh mờ và clipping trắng/đen. Giữ toàn bộ hồi quy cũ: hai sách, chạm biên, xoay/QR, ghi raw/crop/metadata/hash, manifest, camera mock và 17 ca async V02.

## Benchmark geometry thực trên synthetic

Lệnh tại root nhánh V07, dùng interpreter venv (không cần camera):

```powershell
& '.\.venv\Scripts\python.exe' scripts/benchmark_cover_geometry.py --baseline-ref 8f9198f0c78030dd21000f4562a0492556c1dce2 --repeats 3 --processing-width 640
```

Lượt cuối tuần tự lúc 2026-11-07T11:35:47–11:36:00+07:00, fixture alpha compositing không có viền đen giả, exit 0 PASS. Mỗi phiên bản warm-up từng cảnh, đo 150 frame sau warm-up, decode=False. Hai phiên bản cùng Config và cùng fixtures.

| Đo trên 50 ca synthetic | V02 | V07 |
|---|---|---|
| Góc <10px và crop đúng kích thước | 33/50 | 50/50 |
| Sai số góc lớn nhất trong ca có góc | 16.304px | 6.010px |
| Median process, không QR | 13.704ms | 40.066ms |
| p95 process, không QR | 16.165ms | 44.294ms |

Chi phí V07 tăng do phân tích nhiều kênh và xác minh mép; không tuyên bố tăng FPS. Vector hóa lấy mẫu bốn cạnh và cache trong từng frame giảm tính lặp, không bỏ gate. V02 vẫn bỏ frame phân tích trung gian khi bận; preview không đợi decoder. Phần cứng/camera/QR thật chưa được đo. Thời gian phụ thuộc máy, cảnh và tải; các lượt giữa phiên có chạy đồng thời GUI nên không dùng để đặt mục tiêu nghiệm thu.

## Benchmark scheduling và GUI

`benchmark_preview.py --baseline-ref 4d3b402 --frames 15 --delay 0.2`, cùng interpreter, exit 0 PASS lúc 11:30:07–11:30:11+07:00. Với camera/renderer/analysis fake, delay phân tích 200ms: 15/15 frame preview duy nhất, median gap trước 211.276ms, sau 10.806ms; chỉ đo lập lịch, không đo OpenCV/QR/FPS thật.

GUI thật với source-kind synthetic: ba ảnh near-white, đen trên texture và trắng trơn; CLI --image/--duration 3/--screenshot. Lượt 11:29:54–11:30:04+07:00 đều exit 0, đã xem ba screenshot: hai bìa có QR READY, bốn góc ngoài/crop/QR PBL5-B04; bìa trơn QUALITY_WARNING với Detail focus unverified, không báo nhầm BLURRY/BAD_LIGHT. Ảnh/log runtime ở thư mục tạm ngoài repo, không commit. Lượt cuối sau tối ưu vector hóa/UI và fixture không có viền đen giả lúc 11:36:00–11:36:10+07:00 đều exit 0; đã xem lại đủ ba screenshot, cùng kết luận.

## Giới hạn và bước người thật

Synthetic tạo cạnh, texture và màu có kiểm soát; không bao phủ bóng đổ, lóa, cong bìa, độ trễ auto exposure/focus hoặc nền tùy ý. Một hình in đặc giống tứ giác sách vẫn có thể gây nhầm; cần kiểm crop và thu ca lỗi thực tế. Nền/giấy không có ranh giới quan sát được cần B/đổi bố trí/M; không cam kết nhận đúng mọi màu trên mọi nền. Clipping là pixel sát 0/255, chưa đủ phân biệt trắng/đen vật liệu với phơi sáng sai. Các mặc định là kỹ thuật cần pilot; mục tiêu nghiệm thu thực tế **đề xuất, chờ tôi xác nhận**.

Webcam thật, thiết bị ESP32 và đánh giá định lượng trên bộ ảnh thật: **NOT_RUN** trong V07. H04/V01/V03 giữ gate riêng. Người dùng thử theo [bài thử V07](COVER_CAPTURE.md#thử-bìa-sángtối-v07-trên-webcam), gửi video/raw/debug/log ngoài Git; không dùng kết quả synthetic thay DONE-HW. Số test cuối và commit/PR xem [SESSION_LOG](SESSION_LOG.md) và [TASKS](codex/TASKS.md); không duy trì bản sao trạng thái task ở đây.

PR team #8 cũng thực hiện một phương án bìa sáng/UI từ V02. Nhánh V07 này là phương án theo kế hoạch đã duyệt: thêm hiệu chuẩn bù sáng, kiểm mép gần/xa và quality chi tiết. Chưa tích hợp #8 hoặc audit V05 từ #7; cần review phần chồng lấn trước tích hợp, không merge đồng thời hai detector một cách máy móc.

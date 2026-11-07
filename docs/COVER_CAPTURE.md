# Thu ảnh bìa A6

Ứng dụng dành cho một bìa phẳng trong khung hình, camera cố định nhìn từ trên xuống và nền tương đối đồng nhất. Đầu ra gồm ảnh gốc, crop phối cảnh, ảnh chẩn đoán và metadata.

## Chạy

Tại root repository:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Hoặc mở `scripts/windows/CaptureCovers.cmd`. Khi dùng launcher `scripts/capture_covers.py` từ thư mục khác, truyền đường dẫn tuyệt đối tới Python và script.

## Quy trình thu

1. Cố định camera, bố trí ánh sáng đều và chừa nền quanh toàn bộ bìa.
2. Lấy sách khỏi khung, bấm B để ghi nền trống; đặt bìa vào sau khi hiệu chuẩn.
3. Kiểm tra bốn góc, crop và mã QR; giữ yên tới trạng thái READY.
4. Bấm S để xử lý khung nhận mới sau yêu cầu và lưu mẫu đạt điều kiện.
5. Kiểm tra cover.png và metadata trước khi tiếp tục thu nhiều ảnh.

Chọn cửa sổ ứng dụng trước khi dùng phím.

| Phím | Chức năng |
|---|---|
| S | Lưu khung mới đạt điều kiện hình học/chất lượng/QR |
| D | Lưu mẫu có crop vào nhóm review |
| B / C | Hiệu chuẩn nền trống / xóa hiệu chuẩn |
| V | Xem mask tách nền |
| [ / ] | Giảm/tăng ngưỡng khác màu nền, áp dụng trong phiên |
| M | Đóng băng ảnh, chọn bốn góc ngoài bìa; bấm lại để về tự động |
| R | Lật crop 180° |
| Q / Esc | Thoát |

Mẫu chọn góc bằng M lưu đúng ảnh đã đóng băng, không theo dõi cuốn sách sau khi nó di chuyển.

## Camera

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --probe --probe-count 3
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 1
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0 --backend msmf
```

Probe thử từng chỉ số trong tiến trình riêng có timeout. Chỉ số OpenCV có thể đổi khi cắm/rút và không phải tên thiết bị. Backend auto thử DirectShow rồi MSMF trên cùng chỉ số. Nếu camera không mở, đóng ứng dụng khác đang sử dụng nó và kiểm tra quyền camera Windows.

## Trạng thái

| Trạng thái | Xử lý |
|---|---|
| NO_COVER | Kiểm tra toàn bộ bìa trong khung, hiệu chuẩn lại nền hoặc chọn góc M |
| TOUCHING_FRAME | Kiểm tra bìa và ứng viên tứ giác có chạm biên ảnh không |
| MULTIPLE_COVERS | Chỉ giữ một bìa trong khung |
| MOVING | Kiểm tra chuyển động thực tế và hiện tượng nhảy ứng viên góc |
| QUALITY_WARNING | Xem cảnh báo nét, sáng hoặc kích thước nguồn |
| QR_UNREADABLE | Tăng kích thước QR trong ảnh, chỉnh nét, tránh lóa và giữ viền trắng |
| QR_AMBIGUOUS | Giữ một QR trên crop, không tự chọn giữa nhiều mã |
| READY | Kiểm tra crop/ID rồi lưu |

QR hỗ trợ PBL5-B + 2–6 chữ số hoặc LIB1:copy_id. VALID_FORMAT chỉ là cú pháp hợp lệ; chưa lookup DB nên identity giữ NOT_CHECKED.

## Dữ liệu

Mặc định `data/opencv/collection/`; có thể đổi bằng --output.

```text
sessions/<session_id>/session.json, runtime.log, background_<id>.png
captures/<image_id>/raw.png, cover.png, debug.png, metadata.json
manifest.jsonl
```

Raw là toàn khung camera trước annotation/warp, ghi PNG không mất pixel; không phải RAW cảm biến. Cover mặc định 630×888 theo tỉ lệ 105:148, không phải phép đo kích thước vật lý.

Metadata ghi UUID, nguồn real/imported/synthetic, timestamp nhận khung UTC, sequence, QR, corners, metric/config, hướng crop và SHA256. accepted/review là tình trạng mẫu thu; nhãn lỗi AI chưa có và để null. Không dùng debug.png làm ảnh huấn luyện.

Kiểm tra bundle, hash, manifest và thống kê accepted/review theo cuốn bằng [audit chỉ đọc V05](CAPTURE_AUDIT.md). Đóng collector trước khi audit; kết quả không xác nhận nhãn lỗi hoặc danh tính DB.

Đóng các phiên thu trước khi xây lại manifest:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --rebuild-manifest
```

## Cấu hình và giới hạn

Cấu hình tại [cover_capture.json](../vision/opencv/configs/cover_capture.json). Ngưỡng nét/sáng/hình học cần hiệu chuẩn trên bộ bìa pilot. Ảnh được phóng lớn không có thêm chi tiết nguồn.

Timestamp là lúc OpenCV trả khung; bộ đệm driver và độ trễ phơi sáng chưa được hiệu chuẩn. Hướng QR mặc định giả định in cùng chiều bìa; dùng R hoặc tắt orient_by_qr nếu giả định này không phù hợp.

Preview live cập nhật độc lập geometry/QR. Crop/QR bên phải thuộc frame có nhãn Analyzed và tuổi frame; không ghép góc/QR của frame đó lên một frame live mới. Khi worker bận, bỏ qua các frame phân tích trung gian thay vì xếp hàng. S/D chờ frame sau yêu cầu, lưu cùng raw/crop/QR/properties; kết quả quá hạn hoặc thuộc camera/cấu hình cũ bị bỏ. Khi chưa kịp có kết quả trong 3 giây, yêu cầu lưu bị hủy và có thông báo. M giữ đúng ảnh đóng băng; Q/đóng cửa sổ không chờ decoder hoàn tất. Ghi PNG/metadata vẫn đồng bộ nên thao tác lưu có thể gây một khoảng dừng ngắn do ổ đĩa. Bộ chọn tứ giác có thể nhầm đường ron nền hoặc mép hình in với mép giấy; cần kiểm tra crop trước khi lưu và chưa thu hàng loạt khi góc không ổn định.

## Ảnh có sẵn

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg'
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg' --headless --save
```

Ảnh tệp mặc định được đánh dấu imported; fixture tự tạo dùng source-kind synthetic. [Kiểm chứng](COVER_CAPTURE_VALIDATION.md) · [Tiến độ](../PROGRESS.md).


## Thử nhanh preview V02 trên webcam

Đây là kiểm tra riêng hành vi preview/lưu/thoát, chưa thay gate camera/crop V03 hoặc tiêu chí định lượng chưa duyệt. Tại root nhánh fix/preview-v02, dùng Python venv đã xác minh:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Nếu dùng worktree không có venv riêng trên máy hiện tại, thay interpreter bằng đường dẫn venv của checkout chính. Đóng ứng dụng khác đang chiếm camera; thử --camera 1 hoặc --backend msmf nếu sai index/backend.

1. Đưa tay hoặc di chuyển sách: xem số Live frame và hình tiếp tục cập nhật trong khi số Analyzed/crop có thể chậm hơn. Không coi chênh số frame là lỗi ghép ảnh.
2. Bấm B lúc nền trống, đặt một bìa và giữ yên. Khi đủ điều kiện, bấm S một lần; kiểm raw.png, cover.png, QR/capture_seq/camera_session_id trong metadata.json thuộc đúng lần thu. Nếu chưa READY, dùng D để lưu riêng review, không coi đó là sách không lỗi.
3. Thử R và M/chọn bốn góc; kết quả trước thay đổi không được xuất hiện trở lại; M dùng đúng frame đã đóng băng.
4. Rút/cắm lại webcam nếu phù hợp thiết bị: khi mất frame không tiếp tục hiện QR cũ; sau kết nối lại cần hiệu chuẩn nền lại. Bấm Q hoặc đóng cửa sổ để thoát.

Gửi video ngắn thấy Live/Analyzed và thao tác S/Q, thông tin camera/backend/resolution, runtime.log và bundle raw/cover/debug/metadata ngoài Git. Ghi thao tác nào đạt/chưa đạt và mô tả treo/lag nếu có. Không đăng ảnh riêng lên PR public.

Benchmark lập lịch synthetic, không mở camera/cửa sổ và không đo độ chính xác QR:

```powershell
& '.\.venv\Scripts\python.exe' scripts/benchmark_preview.py --baseline-ref 4d3b402 --frames 15 --delay 0.2
```

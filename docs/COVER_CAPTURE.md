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

Đóng các phiên thu trước khi xây lại manifest:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --rebuild-manifest
```

## Cấu hình và giới hạn

Cấu hình tại [cover_capture.json](../vision/opencv/configs/cover_capture.json). Ngưỡng nét/sáng/hình học cần hiệu chuẩn trên bộ bìa pilot. Ảnh được phóng lớn không có thêm chi tiết nguồn.

Timestamp là lúc OpenCV trả khung; bộ đệm driver và độ trễ phơi sáng chưa được hiệu chuẩn. Hướng QR mặc định giả định in cùng chiều bìa; dùng R hoặc tắt orient_by_qr nếu giả định này không phù hợp.

Preview hiện còn chờ xử lý QR. Bộ chọn tứ giác có thể nhầm đường ron nền hoặc mép hình in với mép giấy; cần kiểm tra crop trước khi lưu và chưa thu hàng loạt khi góc không ổn định.

## Ảnh có sẵn

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg'
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg' --headless --save
```

Ảnh tệp mặc định được đánh dấu imported; fixture tự tạo dùng source-kind synthetic. [Kiểm chứng](COVER_CAPTURE_VALIDATION.md) · [Tiến độ](../PROGRESS.md).

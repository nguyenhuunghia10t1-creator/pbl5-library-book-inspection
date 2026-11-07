# Kiểm tra bundle và báo cáo pilot — V05

Đóng các phiên collector trước khi chạy để metadata, ảnh và manifest thuộc cùng một thời điểm. Công cụ chỉ đọc collection; không sửa ảnh, metadata, session hay manifest, không tạo thư mục và không tự khôi phục dữ liệu.

## Cách chạy

Từ root repository, dùng Python venv đã xác minh:

```powershell
& '.\.venv\Scripts\python.exe' scripts/audit_captures.py
& '.\.venv\Scripts\python.exe' scripts/audit_captures.py 'E:\pilot\collection'
& '.\.venv\Scripts\python.exe' scripts/audit_captures.py 'E:\pilot\collection' --json
```

Không truyền collection thì kiểm `data/opencv/collection` của chính checkout chứa script, kể cả khi thư mục hiện tại khác. Với worktree không có venv, dùng đường dẫn tuyệt đối tới interpreter đã xác minh của checkout chính. Audit dùng thư viện chuẩn Python, không cần thêm dependency hoặc camera.

Mặc định in báo cáo dễ đọc; `--json` in một đối tượng JSON để lưu/lập báo cáo. Muốn lưu stdout, chọn file **ngoài collection**, không ghi đè manifest hoặc metadata. Mã thoát: **0** khi không có lỗi; **1** khi kiểm tra FAIL (kể cả không có capture hoàn tất); **2** khi tham số dòng lệnh sai.

## Nội dung được kiểm

- Mỗi thư mục capture có UUID và metadata schema 1; tham chiếu session/frame, timestamp có múi giờ, nguồn `real/imported/synthetic` và trạng thái `accepted/review` hợp lệ.
- Provenance trong capture khớp `session.json`; ảnh nền nếu được tham chiếu phải có ở cùng session. Phát hiện frame được lưu trùng theo `camera_session_id/capture_seq`.
- Ba file `raw.png`, `cover.png`, `debug.png` nằm đúng bundle; SHA256 của byte ảnh khớp metadata. Đường dẫn lệch bundle và symlink/junction bên trong collection bị từ chối.
- `metadata.json` là nguồn chính. Mỗi capture phải có đúng một dòng manifest trùng toàn bộ metadata; báo dòng thiếu, lặp, mồ côi, khác metadata hoặc JSON không đọc được. JSON trùng key và số NaN/Infinity cũng bị từ chối.
- `accepted` yêu cầu `vision_status=READY`, QR `VALID_FORMAT` và có `copy_id`; QR book_id phải khớp copy_id. `review` có thể chưa đọc được mã.

Staging `.pending_*` được báo warning và giữ nguyên, không tính là capture hoàn tất. Nếu có bundle hoàn tất hợp lệ và chỉ có warning, mã thoát vẫn là 0; người thu phải đọc warning trước khi bàn giao. Collection rỗng hoặc chỉ có staging không đạt.

## Đọc số liệu

`summary` tách số capture hoàn tất được phát hiện, bundle hợp lệ/lỗi, staging, lỗi và warning. `by_source_kind`, `by_collection_status`, `by_copy_id` chỉ thống kê **bundle vượt qua kiểm tra metadata/session/file/hash** (`statistics_scope=valid_bundles_only`). Mỗi cuốn có tổng ảnh và số accepted/review; chưa có mã được gom vào `copy_id=null`, hiện `(unidentified)` ở dạng text.

Lỗi manifest được báo riêng và làm toàn báo cáo FAIL, kể cả khi các bundle vẫn nguyên vẹn và xuất hiện trong thống kê. Vì vậy số `valid_bundles` lớn hơn 0 không tự chứng minh collection đã đạt. Báo cáo JSON giữ mã lỗi, đường dẫn tương đối và mô tả để truy lại nguồn.

Nếu chỉ manifest bị thiếu/lệch, xem [cơ chế xây lại manifest](COVER_CAPTURE.md#dữ-liệu). Đóng collector, kiểm metadata/bundle gốc trước khi chủ động dùng `--rebuild-manifest`, rồi chạy audit lại. Audit không gọi lệnh khôi phục, không xóa staging và không sửa checksum để che lỗi.

## Giới hạn bằng chứng

Nguồn ảnh là **khai báo** được đối chiếu với session; audit không thể chứng minh ảnh thực sự đến từ camera. `copy_id` là mã đã ghi, chưa xác nhận danh tính trong DB; không suy tuyến A/B. Hash chỉ chứng minh byte ảnh khớp metadata đã ghi, không giải mã ảnh để xác nhận nội dung hoặc chứng minh crop đúng.

Accepted/review phản ánh điều kiện thu ảnh, không phải sách tốt/xấu hay nhãn rách/bẩn. Báo cáo không đo accuracy YOLO, không đánh giá nhãn, không thay gate webcam V03 hoặc pilot thật V06; không tự đặt cỡ mẫu/ngưỡng nghiệm thu.

Kiểm thử tại [test_capture_audit.py](../tests/opencv/test_capture_audit.py) tạo collection tạm bằng DatasetWriter, bao gồm ảnh bị sửa, file/session/manifest thiếu, metadata lỗi, trùng frame, đường dẫn không an toàn và CLI từ thư mục khác. Toàn bộ là fixture synthetic; các giá trị `real/imported` trong test chỉ thử enum, không phải bằng chứng dữ liệu thật. Test so byte và mtime trước/sau để kiểm tính chỉ đọc. Không commit collection hoặc báo cáo chứa dữ liệu riêng vào Git.

# Thu ảnh bìa A6

Ứng dụng dành cho một bìa phẳng trong khung hình, camera cố định nhìn từ trên xuống. Bộ phát hiện kết hợp màu Lab, cạnh ở các kênh sáng/màu và bằng chứng hai bên mép; hỗ trợ nền sáng, tối, hoa văn và đường ron trong bộ thử tổng hợp. Nền khó nên hiệu chuẩn B; chưa có cam kết nhận đúng mọi nền trên thiết bị thật. Đầu ra gồm ảnh gốc, crop phối cảnh, ảnh chẩn đoán và metadata.

## Chạy

Tại root repository:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Hoặc mở `scripts/windows/CaptureCovers.cmd`. Khi dùng launcher `scripts/capture_covers.py` từ thư mục khác, truyền đường dẫn tuyệt đối tới Python và script.

## Giao diện tiếng Việt

Trên Windows, nội dung giao diện hiển thị tiếng Việt có dấu bằng font Segoe UI có sẵn; không cần cài thêm thư viện. Riêng thanh tiêu đề cửa sổ dùng tiếng Việt không dấu để tương thích HighGUI/ANSI trên Windows. Phím S/D/B/C/M/R/V/Q và [ / ] giữ nguyên. Trạng thái, thông số và hướng dẫn thao tác trên màn hình đã dịch; mã kỹ thuật trong metadata, headless JSON và ảnh debug lưu vẫn giữ để tương thích.

- **SẴN SÀNG LƯU ẢNH**: đạt điều kiện thu mẫu hiện có; chưa kết luận sách không rách/bẩn.
- **CHƯA ỔN ĐỊNH**: giữ yên camera và sách, chờ các góc ổn định; góc nhảy cũng gây trạng thái này.
- **QR: Sai định dạng mã**: kiểm tra nội dung QR, ví dụ PBL5-B04 hoặc LIB1:<copy_id>; chữ in cạnh QR chưa chứng minh payload.
- **Độ sáng**: trung bình thang 0–255, không phải lux. **Độ nét/Nét tại vùng chi tiết**: chỉ số ảnh, không phải phần trăm.
- **Trắng/đen bão hòa**: tỷ lệ pixel gần trắng/đen tuyệt đối. **Cách đây**: tuổi khung đã xử lý. **Xử lý ... lượt/giây**: ước tính từ lượt phân tích vừa xong, không phải FPS camera.

Hướng dẫn và lỗi phổ biến có giải thích tiếng Việt; lỗi hệ thống chi tiết nằm trong runtime.log. Chuỗi quá dài được rút gọn bằng dấu … để không tràn khung. Nền tảng ngoài Windows dùng chữ Việt không dấu để các công cụ headless/test vẫn chạy với OpenCV hiện có. Font Windows dùng GDI [TextOutW](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-textoutw); không đổi thuật toán nhận dạng hoặc ngưỡng.

## Quy trình thu

1. Cố định camera, bố trí ánh sáng đều và chừa nền quanh toàn bộ bìa.
2. Có thể dùng tự động trước. Nếu nền khó/gần màu bìa, lấy sách khỏi khung, bấm B để ghi nền trống rồi mới đặt bìa vào. Nếu đổi nền, di chuyển camera hoặc thay ánh sáng đáng kể, hiệu chuẩn lại; C xóa nền cũ.
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

## Camera điện thoại qua DroidCam

1. Mở DroidCam trên điện thoại và DroidCam Client trên Windows; kết nối tới khi client có hình. Với Wi-Fi, hai thiết bị dùng cùng mạng. Giữ client chạy khi dùng ứng dụng.
2. Thử nguồn camera bằng MSMF:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --probe --probe-count 3 --backend msmf
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 1 --backend msmf
```

Số 1 là ví dụ đã kiểm trên máy phát triển ngày 2026-11-07, không phải định danh cố định của DroidCam. Nếu worktree không có .venv, thay đường dẫn Python bằng interpreter venv đã cài requirements. Trên máy này DirectShow không mở được DroidCam nhưng MSMF nhận khung 1280×720. Không suy chỉ số giữa hai backend hoặc máy khác nhau; kiểm tra lại khi đổi thiết bị.

3. Dùng camera sau, cố định điện thoại nhìn xuống, chừa đủ nền quanh bìa A6. Bấm B khi bàn trống rồi đặt một cuốn vào; xem góc ngoài/crop/QR, bấm S khi READY. Di chuyển điện thoại thì hiệu chuẩn lại. Q thoát ứng dụng, không đóng client trước khi xong.

Đọc được khung camera chưa chứng minh độ chính xác nhận dạng hoặc chất lượng dữ liệu. Kiểm chứng nhiều bìa/nền và gửi raw/crop/debug/metadata/log theo bài thử V07; không commit dữ liệu camera.

Tham khảo: [DroidCam Windows Client](https://droidcam.app/windows/) và [hướng dẫn kết nối](https://droidcam.app/help/).

## Trạng thái

| Trạng thái | Xử lý |
|---|---|
| NO_COVER | Kiểm tra toàn bộ bìa trong khung, hiệu chuẩn lại nền hoặc chọn góc M |
| TOUCHING_FRAME | Kiểm tra bìa và ứng viên tứ giác có chạm biên ảnh không |
| MULTIPLE_COVERS | Chỉ giữ một bìa trong khung |
| MOVING | Kiểm tra chuyển động thực tế và hiện tượng nhảy ứng viên góc |
| QUALITY_WARNING | Xem issues và Detail focus/Clip high-low; thiếu chi tiết để xác minh nét vẫn cần review, không tự READY |
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

Preview live cập nhật độc lập geometry/QR. Crop/QR bên phải thuộc frame có nhãn Analyzed và tuổi frame; không ghép góc/QR của frame đó lên một frame live mới. Khi worker bận, bỏ qua các frame phân tích trung gian thay vì xếp hàng. S/D chờ frame sau yêu cầu, lưu cùng raw/crop/QR/properties; kết quả quá hạn hoặc thuộc camera/cấu hình cũ bị bỏ. Khi chưa kịp có kết quả trong 3 giây, yêu cầu lưu bị hủy và có thông báo. M giữ đúng ảnh đóng băng; Q/đóng cửa sổ không chờ decoder hoàn tất. Ghi PNG/metadata vẫn đồng bộ nên thao tác lưu có thể gây một khoảng dừng ngắn do ổ đĩa. Bộ chọn tứ giác yêu cầu bằng chứng trên cả bốn cạnh, tương phản ở hai khoảng cách trong/ngoài và ưu tiên mép ngoài có căn cứ. Đây là heuristic, vẫn có thể nhầm nền/hoạ tiết chưa gặp; cần kiểm tra crop trước khi lưu. Nếu không quan sát được ranh giới giấy–nền, dùng nền khác/ánh sáng khác hoặc M, không coi khung in là mép sách. B chỉ bù dịch sáng/màu toàn khung, không bù được bóng/lóa cục bộ hoặc camera di chuyển.

## Ảnh có sẵn

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg'
& '.\.venv\Scripts\python.exe' -m vision.opencv --image '.\sample.jpg' --headless --save
```

Ảnh tệp mặc định được đánh dấu imported; fixture tự tạo dùng source-kind synthetic. [Kiểm chứng](COVER_CAPTURE_VALIDATION.md) · [Tiến độ](../PROGRESS.md).


## Thử nhanh preview V02 trên webcam

Đây là kiểm tra riêng hành vi preview/lưu/thoát, chưa thay gate camera/crop V03 hoặc tiêu chí định lượng chưa duyệt. Tại root nhánh đang thử (V07: fix/cover-color-background), dùng Python venv đã xác minh:

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


## Thử bìa sáng/tối V07 trên webcam

1. Dùng nhánh `fix/cover-color-background`, chạy lệnh camera ở đầu tài liệu. Chuẩn bị một bìa trắng/kem và một bìa tối, đều cỡ A6, QR rõ. Thử lần lượt trên nền sáng, tối và nền hoa văn/ron. Đây là bộ thử **đề xuất, chờ tôi xác nhận**, không là ngưỡng nghiệm thu chính thức.
2. Với mỗi cặp bìa/nền: bấm C, thử tự động trước; kiểm bốn góc bám mép giấy, không bám viền hình in. Lấy sách ra: khung/crop cũ phải biến mất sau lượt Analyzed mới. Giữ camera cố định, bấm B lúc nền trống rồi thử lại. Không hiệu chuẩn khi có sách trong khung.
3. Thử bìa hơi xoay, một vùng ánh sáng không đều, sách chạm biên và hai sách: không được lưu nhầm mẫu accepted. Trường hợp không có ranh giới nhìn thấy, dùng M để thu riêng ảnh tĩnh sau khi kiểm crop.
4. Đọc `Detail focus` và `Clip high/low`. Bìa ít họa tiết có `FOCUS_UNVERIFIED`: quá ít chi tiết để xác minh nét, vẫn `QUALITY_WARNING`; đặt nét theo chữ/QR và dùng D để lưu review nếu cần. `BLURRY` cần chỉnh nét/giữ yên. Màu trắng có brightness cao không tự đồng nghĩa cháy sáng. Tỷ lệ pixel sát 0/255 là chẩn đoán clipping, không phân biệt chắc chắn mực đen/giấy trắng với lỗi phơi sáng.
5. Khi READY, bấm S và xem lại raw/cover/debug/metadata. Khi sai góc hoặc cảnh báo, bấm D nếu còn crop; nếu không có crop, chụp/lưu frame gốc bằng công cụ camera và ghi timestamp tương ứng trong video. Không xóa hoặc ghi đè ảnh lỗi.

Gửi ngoài Git: video thấy Live/Analyzed, mã bìa, loại nền, auto hay B, góc đúng/sai và thao tác lấy sách ra; `runtime.log`, bundle raw/cover/debug/metadata nếu có, cấu hình, camera/backend/resolution và commit/nhánh. Ưu tiên một ca bìa sáng trước đây bị lỗi và một ca bìa tối đã chạy tốt. H04/V01/V03 vẫn cần dữ liệu/gate riêng; không hoàn thành từ synthetic.

### Chẩn đoán và ngưỡng kỹ thuật V07

API detect/process, brightness/sharpness cũ và schema bundle được giữ; chẩn đoán mới chỉ thêm vào metrics/issues. JSON cấu hình cũ đọc được nhờ giá trị mặc định trong Config.

| Tham số mặc định mới | Ý nghĩa |
|---|---|
| edge_min_threshold=8, edge_noise_factor=4 | Sàn và hệ số median/MAD cho Canny trên Lab |
| min_side_support=0.50, min_boundary_delta=2 | Bằng chứng tối thiểu trên mỗi cạnh và tương phản hai bên |
| geometry_ring_pixels=5 | Khoảng lấy mẫu gần mép ở ảnh xử lý; dải xa gấp đôi |
| background_noise_factor=4, min_foreground_delta=3 | Ngưỡng foreground thích nghi sau bù dịch sáng/màu |
| min_detail_contrast=12 | Độ trải mức xám để tile có thể dùng đo nét |
| max_clipped_fraction=0.98 | Mức pixel sát trắng/đen kích hoạt BAD_LIGHT |

Các mặc định trên và min_sharpness cần hiệu chỉnh bằng pilot; mục tiêu nghiệm thu thực tế là **đề xuất, chờ tôi xác nhận**. max_brightness vẫn đọc được và ghi chẩn đoán vượt khoảng cũ; không còn chặn chỉ từ trung bình bìa sáng. min_sharpness được áp dụng lên chi tiết có thể đo (phân vị 75% variance Laplacian tile), còn sharpness toàn crop được giữ để đối chiếu. Xem [báo cáo V07](COLOR_BACKGROUND_VALIDATION.md) và script benchmark_cover_geometry.py để tái lập thử synthetic; không dùng tốc độ đó làm FPS webcam.

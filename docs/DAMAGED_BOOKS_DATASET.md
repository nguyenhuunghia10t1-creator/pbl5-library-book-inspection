# Damaged Books v1 — bước chuẩn hóa dữ liệu

Phạm vi phiên này chỉ gồm chuyển nhãn, kiểm nguồn và kiểm tra cách chia dữ liệu. Chưa triển khai notebook huấn luyện, inference, barcode hoặc simulator trên nhánh này. Collector và dữ liệu QR cũ được giữ nguyên.

## Bảng lớp

| ID | Lớp | Vai trò |
|---|---|---|
| 0 | Barcode | Vùng mã vạch, không phải lỗi |
| 1 | Notch | Khuyết/sứt |
| 2 | Ripped | Rách |
| 3 | Spot | Bẩn |
| 4 | Wornout | Mòn/sờn |

Chỉ bỏ các dòng có ID nguồn 4 (Tag); đổi ID nguồn 5 thành 4. Tọa độ các hộp còn lại giữ nguyên; không xóa ảnh, không xóa tem trên ảnh. Tệp nhãn rỗng vẫn tồn tại.

Nguồn: [Damaged Books v1, Roboflow user atcom21-gmail-com](https://universe.roboflow.com/atcom21-gmail-com/damaged-books/dataset/1), giấy phép [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Giữ README nguồn cùng bản chuyển đổi và ghi rõ thay đổi nhãn trong manifest. Bộ xuất nguồn đã kéo giãn ảnh về 640×640; công cụ không đảo ngược phép biến đổi đó.

## Kết quả đã kiểm ngày 2026-11-10

| Hạng mục | Kết quả |
|---|---|
| Ảnh giữ nguyên byte | 620 |
| Hộp sau chuyển đổi | 3.610 |
| Hộp Tag đã loại | 379 |
| Barcode / Notch / Ripped / Spot / Wornout | 194 / 729 / 411 / 937 / 1.339 |
| Nhãn rỗng giữ lại | 34 |
| Ảnh không còn hộp lỗi, cần duyệt mẫu âm | 51, bao gồm 34 ảnh nhãn rỗng |
| Version nội dung | `damaged-books-v1-five-8f203ddd57d4` |
| ZIP nguồn SHA256 | `dc2a81293b0f841b0fd187a410b869a1fc9021077ffc6221f9f33621ff978197` |
| Đối chiếu ảnh/nhãn nguồn với ZIP và bản chuyển đổi | PASS, toàn bộ 620 bản ghi |

Split nguồn 618 train / 1 valid / 1 test không đủ để đánh giá. Validation chỉ có Ripped; test thiếu Spot. Đã xem ảnh và xác nhận `train/IMG_1316...` cùng cuốn/thiết kế với `test/IMG_7...`; hai ảnh phải cùng một nhóm. Đây là bằng chứng rò nhóm của split cũ, chưa phải kết quả rà đủ 620 ảnh. Nhãn của cả hai vẫn pending.

Chưa có split mới được duyệt. Không gọi 51 ảnh trên là sách lành; cần kiểm bằng ảnh xem nhãn lỗi có bị bỏ sót không.

## Chạy công cụ

Chạy tại gốc checkout của nhánh này, kích hoạt môi trường collector hiện có để `python` trỏ đúng interpreter; công cụ chuyển/split chỉ dùng thư viện chuẩn, trang ảnh dùng OpenCV đã có. Không cần cài PyTorch/Ultralytics ở bước này.

```powershell
$sourceRoot = Read-Host 'Đường dẫn thư mục đã giải nén dataset'
$preparedRoot = Join-Path $sourceRoot 'data\local\damaged_books_v1\prepared-verified'
$pythonExe = 'python'

# Chỉ khi tạo một bản mới: --output không được tồn tại.
& $pythonExe -m vision.yolo.prepare convert --source $sourceRoot --output $preparedRoot
& $pythonExe -m vision.yolo.prepare audit --source $sourceRoot --prepared $preparedRoot
& $pythonExe -m vision.yolo.review --prepared $preparedRoot
Start-Process (Join-Path $preparedRoot 'review.html')
```

Bản `prepared-verified` đã được tạo trên máy hiện tại; không chạy lại lệnh convert vào cùng vị trí. Có thể chạy lại audit/review. Trên máy khác thay `$sourceRoot` theo vị trí gói giải nén; dữ liệu phải nằm trong `data/local` được Git bỏ qua hoặc một thư mục dữ liệu riêng ngoài repository. ZIP, train/valid/test và các README nguồn được giữ nguyên tại vị trí giải nén.

`manifest.json` chứa nguồn, giấy phép, ID mapping, version, checksum ảnh/nhãn/ZIP/metadata và thống kê split cũ. `audit` kiểm tra lại byte ảnh, chính xác các dòng nhãn sau remap, tệp rỗng, thống kê và nội dung ảnh/nhãn giải nén so với ZIP.

## Việc hiện tại: rà nhóm và nhãn

Mở `review.html`. Gán cùng `group_id` cho cùng cuốn hoặc thiết kế bìa ở mọi góc chụp, kể cả ảnh ở split nguồn khác nhau. Không dùng tên tệp hay mỗi ảnh làm một nhóm để lách kiểm tra. Bấm ảnh phóng to hộp nhãn, mở ảnh gốc để đối chiếu; ảnh khó xác định giữ pending hoặc rejected.

Chỉ chọn “Đã duyệt” khi hộp và lớp đủ tin cậy. Lọc “Ứng viên mẫu âm” để kiểm riêng 51 ảnh; chỉ duyệt mẫu âm sau khi xác nhận không thấy bốn lỗi trên phần nhìn thấy. Nhãn nghi vấn không tự sửa đè; ghi lại để tạo phiên bản nhãn được duyệt sau.

Tải `review.csv`, giữ bản dự phòng, thay đúng tệp trong thư mục prepared sau khi đã kiểm. Trang nạp sẵn CSV ở thời điểm tạo HTML; nếu tiếp tục phiên khác, nạp CSV mới nhất bằng nút “Nạp review.csv đã lưu”. Trang không tự ghi thay đổi xuống đĩa. Không tải CSV trống đè kết quả đã rà.

Sau khi việc rà đủ tin cậy mới chạy:

```powershell
$splitRoot = Join-Path $sourceRoot 'data\local\damaged_books_v1\split-reviewed-v1'
& $pythonExe -m vision.yolo.prepare split --prepared $preparedRoot --output $splitRoot
```

Chia theo nhóm, seed 42, xấp xỉ 70/15/15 trên các ảnh đã duyệt. Tất cả ba tập phải có đủ năm lớp; không đạt thì báo lỗi trước khi tạo đầu ra. Ảnh thiếu nhóm, nhãn pending/rejected hoặc mẫu âm chưa duyệt vào danh sách `quarantined` trong split manifest, không được sao chép sang các tập. Ảnh byte trùng mà thuộc hai nhóm bị từ chối. Kiểm này không tự phát hiện mọi ảnh gần giống; rà hình ảnh vẫn là điều kiện bắt buộc.

Đầu ra gồm `data.yaml`, `split_manifest.json`, ảnh/nhãn theo tập và ZIP ở cạnh thư mục split. Manifest lưu nhóm, số ảnh/lớp từng tập, checksum tệp, checksum CSV và version split. Không tune trên test. Chỉ tiếp tục Colab sau khi đọc lại báo cáo nhóm/split; bước đó chưa được bắt đầu ở bản bàn giao này.

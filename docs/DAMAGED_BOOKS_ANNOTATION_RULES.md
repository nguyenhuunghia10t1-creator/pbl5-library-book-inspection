# Quy tắc rà nhãn sách — năm lớp

Áp dụng cho lượt rà 20 ảnh train/val đã khóa, theo kế hoạch người dùng duyệt ngày 2026-11-11. Gán **mọi lỗi nhìn rõ, kể cả lỗi nhẹ**; kết quả chỉ phản ánh mặt sách đang nhìn thấy. Đây là quy tắc và đề xuất sửa, chưa phải dataset v2 hoặc chứng nhận chất lượng model. Giữ hợp đồng D20–D24 của nhánh Colab; collector legacy chưa đổi.

| ID | Lớp | Gán khi thấy | Không suy ra từ |
|---|---|---|---|
| 0 | `Barcode` | Vùng sọc mã vạch một chiều, cả tem thư viện lẫn ISBN/EAN in sẵn; hộp sát vùng sọc và biên trắng sát sọc | Tem chỉ có chữ, chữ/họa tiết kẻ sọc, mã nằm ngoài ảnh; không cần giải mã được |
| 1 | `Notch` | Phần khuyết/sứt làm mất vật liệu ở góc/mép | Nếp gấp, rãnh đóng sách, vết xước hoặc phản sáng giữa mặt bìa |
| 2 | `Ripped` | Khe tách, rìa giấy rách hoặc phần giấy bật/lật nhìn rõ | Vùng bạc màu/tróc bề mặt đơn thuần; không dùng mức độ hỏng để đoán rách |
| 3 | `Spot` | Vết bẩn ngoại lai rõ, phân biệt được với thiết kế bìa | Chữ/hình in, bóng đổ, phản sáng, màu giấy hoặc lớp màng tróc |
| 4 | `Wornout` | Mòn/sờn/tróc bề mặt rõ | Phản sáng đơn thuần, viền trang trí hoặc nếp gấp chưa có mòn |

## Hộp và trường hợp chưa rõ

- Xem ảnh gốc trước, bật hộp sau. Vẽ sát tổn thương có thể thấy; không mở rộng hộp để bao phần lỗi suy đoán ngoài khung.
- Một vùng sờn liên tục dùng một hộp; các vùng tách biệt dùng các hộp riêng. Không gộp những tổn thương khác nhau chỉ vì nằm cùng một mép.
- Không đặt ngưỡng loại bỏ tùy ý `8×8 px`, diện tích hoặc tỷ lệ cạnh. Hộp nhỏ/dẹt vẫn hợp lệ nếu bằng chứng rõ.
- Không gán cùng một tổn thương nhiều lớp chỉ vì chưa phân biệt được. Hai tổn thương thật khác nhau được phép có hộp giao nhau hoặc lồng nhau; ví dụ vết bẩn thật trên barcode có cả `Spot` và `Barcode`. IoU/IoA không tự quyết định nhãn sai.
- Không chắc là bẩn, tróc hay phản sáng: ghi `needs_review`, chỉ rõ dòng nhãn/vùng ảnh và câu hỏi. Giữ hộp nguồn trong phần đối chiếu bằng nét đứt, không tự xóa/đổi lớp hoặc duyệt sạch.
- Nhãn rỗng không tự chứng minh mẫu âm. Ảnh không lỗi nhưng có barcode vẫn cần nhãn `Barcode`; ảnh âm chưa rõ vẫn chờ xác nhận. Không suy ra khay C từ việc thiếu nhãn.
- `Ripped → A`, lỗi khác → B là luật phân tuyến sau phân tích, không phải lý do ép vùng nghi ngờ thành Ripped. Chưa xác định tổn thương thì chưa chốt tuyến từ nhãn đề xuất.

## Đầu ra và cách xem

Danh sách khóa, checksum và quan sát thủ công nằm trong [hồ sơ 20 ảnh](reviews/damaged_books_review20.json). Trợ lý đã xem ảnh gốc và ảnh vẽ hộp; script chỉ xác minh cấu trúc/checksum và sinh giao diện, không tự xác nhận nội dung hình ảnh.

Chạy ở thư mục gốc bằng môi trường collector có OpenCV:

```powershell
& '.venv/Scripts/python.exe' scripts/build_damaged_books_review20.py
& '.venv/Scripts/python.exe' scripts/build_damaged_books_review20.py --check
Start-Process 'data/local/damaged_books_v1/run2-review20/review.html'
```

Trang có ảnh gốc / nhãn hiện tại / đề xuất, bấm ảnh để phóng to và lọc câu hỏi ảnh hưởng A/B. CSV tóm tắt và JSON từng hộp ở cùng thư mục cục bộ. JSON ghi `before`, `after`, dòng nguồn (đánh số từ 1), lý do và checksum. `keep` là đề xuất giữ, `change_proposed` là đề xuất sửa đã rõ, `needs_review` có ít nhất một hộp hoặc câu hỏi chưa rõ; **không trạng thái nào là phê duyệt của người vận hành**. Hộp chưa rõ vẫn giữ tọa độ nguồn; không xuất nhãn YOLO mới.

Mọi thay đổi nguồn làm script dừng. Tệp đầu ra đã bị người dùng chỉnh sẽ không bị ghi đè; dùng `--output` tới thư mục mới bên trong `data/local`. Đợt này không đọc ảnh/nhãn test, không đổi nhóm/split, `review.csv` cũ hoặc dữ liệu nguồn.

Điểm bàn giao: xem các câu hỏi còn nghi vấn, ưu tiên phân biệt Ripped với lỗi khác. Chưa xuất dataset v2, chưa train.

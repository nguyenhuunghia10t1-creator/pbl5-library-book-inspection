# Kiểm chứng ứng dụng thu ảnh

Môi trường phát triển đã kiểm tra: Windows, Python 3.14.3, OpenCV 5.0.0, NumPy 2.5.3.

| Hạng mục | Kết quả | Phạm vi |
|---|---|---|
| Unit/integration Python | 22 PASS | Hình học, QR, camera mô phỏng, lưu ảnh, manifest và entrypoint |
| Tiện ích camera Windows | 23 PASS | Mô phỏng policy/recovery; không thao tác PnP thật |
| CLI và lưu bundle | PASS | Ảnh tổng hợp, QR PBL5-B04, re-import và SHA256 |
| GUI | PASS | Hiển thị ảnh mẫu, mở/đóng theo thời hạn |
| Firmware mẫu | BUILD PASS | PlatformIO; chưa upload hoặc thử cơ cấu |
| Bìa thật B08 | Chưa đạt ổn định | 5/12 khung tới bước QR, 7/12 dừng ở geometry, 0 READY |
| Pilot nhiều bìa/chạy dài | Chưa kiểm tra | Cần bộ thử và bố trí camera cố định |

Các ca tổng hợp gồm nhiều góc xoay, phối cảnh, ảnh mờ, thiếu đối tượng, nhiều sách/QR, lỗi đọc và lỗi ghi dữ liệu. Camera mô phỏng kiểm sequence, frame mới sau yêu cầu lưu và release.

## Lỗi đang theo dõi

1. Bộ chọn tứ giác có thể chọn đường ron nền hoặc mép hình in thay cho mép ngoài bìa.
2. Preview còn chờ geometry/QR đồng bộ, giới hạn tốc độ cập nhật.

Kết quả trên một bố trí không được dùng làm độ chính xác tổng quát của hệ thống. Metric chất lượng ảnh không phải nhãn lỗi sách.

## Chạy lại

```powershell
& '.\.venv\Scripts\python.exe' scripts/check_repository.py
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

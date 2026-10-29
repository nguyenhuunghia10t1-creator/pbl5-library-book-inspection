# OpenCV

Module thu ảnh, kiểm tra vùng bìa và đọc QR cho desktop collector.

| Tệp | Vai trò |
|---|---|
| `camera.py` | CameraAdapter, frame/timestamp/sequence, luồng lấy ảnh mới nhất. |
| `pipeline.py` | Tìm tứ giác, warp A6, chất lượng ảnh, QR và các kiểu Result/QRResult. |
| `dataset.py` | Đọc/ghi ảnh, bundle metadata, manifest và checksum. |
| `config.py`, `configs/cover_capture.json` | Cấu hình riêng OpenCV, tìm repo root độc lập thư mục chạy. |
| `__main__.py` | Điểm chạy `python -m vision.opencv`, gọi UI trong software. |
| `requirements.txt` | Dependency của collector hiện tại. |

Chạy tại root repository:

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Launcher `scripts/capture_covers.py` hỗ trợ chạy từ thư mục khác khi dùng đường dẫn tuyệt đối tới Python và script.

Giao diện và vòng điều phối nằm ở [software/desktop/cover_capture_app.py](../../software/desktop/cover_capture_app.py). Dữ liệu mới mặc định ở `data/opencv/collection`; dữ liệu chẩn đoán cũ ở `data/opencv/validation`. [Hướng dẫn](../../docs/COVER_CAPTURE.md), [kiểm chứng](../../docs/COVER_CAPTURE_VALIDATION.md).

Lỗi đã biết: preview bị chặn bởi geometry/QR; chọn nhầm đường ron nền/biên hình in gây nhảy crop. Các lỗi được theo dõi trong Issues.

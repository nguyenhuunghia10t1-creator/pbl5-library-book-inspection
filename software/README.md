# Phần mềm máy tính

Giao diện desktop tại [cover_capture_app.py](desktop/cover_capture_app.py) quản lý hiển thị, thao tác bàn phím và phiên thu ảnh. Xử lý camera, hình học, QR và ghi bundle sử dụng API của vision.opencv.

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Trạm tự động dùng FastAPI trong `software/web`, SQLite và điều phối lượt sách trong `software/inspection`, bộ giao tiếp USB Serial và mô phỏng trong `software/controller`. [Hướng dẫn trạm](../docs/INSPECTION_STATION.md) · [Kiến trúc](../docs/ARCHITECTURE.md).

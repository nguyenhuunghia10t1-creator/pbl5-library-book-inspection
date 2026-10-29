# Phần mềm máy tính

Giao diện desktop tại [cover_capture_app.py](desktop/cover_capture_app.py) quản lý hiển thị, thao tác bàn phím và phiên thu ảnh. Xử lý camera, hình học, QR và ghi bundle sử dụng API của vision.opencv.

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Backend, database, decision policy, Web HMI và ControllerTransport sẽ được phát triển theo [kế hoạch](../docs/PLAN.md). Phần mềm không gọi GPIO trực tiếp. [Kiến trúc](../docs/ARCHITECTURE.md).

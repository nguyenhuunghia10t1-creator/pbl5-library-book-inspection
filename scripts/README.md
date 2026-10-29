# Công cụ hỗ trợ

| Công cụ | Mục đích |
|---|---|
| capture_covers.py | Chạy collector từ thư mục bất kỳ |
| check_repository.py | Kiểm cú pháp nguồn Python, link tài liệu và workspace |
| windows/CaptureCovers.cmd | Chạy collector với venv tại root trên Windows |
| windows/camera-priority | Tiện ích tùy chọn quản lý camera A4tech |

```powershell
& '.\.venv\Scripts\python.exe' scripts/check_repository.py
& '.\.venv\Scripts\python.exe' scripts/capture_covers.py --camera 0
```

Tiện ích camera-priority có bộ test mô phỏng riêng, không cài task hoặc thao tác PnP trong CI. [Hướng dẫn](windows/camera-priority/README.md).

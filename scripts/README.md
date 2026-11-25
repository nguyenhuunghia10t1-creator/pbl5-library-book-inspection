# Công cụ hỗ trợ

| Công cụ | Mục đích |
|---|---|
| capture_covers.py | Chạy collector từ thư mục bất kỳ |
| check_repository.py | Kiểm cú pháp nguồn Python, link tài liệu và workspace |
| windows/ManualMechanics.cmd | Commission the conveyor with operator OK/NG decisions |
| windows/TestCameraAI.cmd | Check live camera and classifier independently |
| windows/InspectBooks.cmd | Operate the camera-driven station after validation |
| windows/SimulateBooks.cmd | Test manual or file-image decisions on the PC |
| windows/FlashInspection.cmd | Upload the single-board wired firmware |
| analyze_colab_run.py | Phân tích tái lập artifacts huấn luyện Colab và thống kê nhãn/box của split |
| windows/CaptureCovers.cmd | Chạy collector với venv tại root trên Windows |
| windows/camera-priority | Tiện ích tùy chọn quản lý camera A4tech |

```powershell
& '.\.venv\Scripts\python.exe' scripts/check_repository.py
& '.\.venv\Scripts\python.exe' scripts/analyze_colab_run.py --output-json data/local/damaged_books_v1/colab-results/run1-analysis.json
& '.\.venv\Scripts\python.exe' scripts/capture_covers.py --camera 0
```

Tiện ích camera-priority có bộ test mô phỏng riêng, không cài task hoặc thao tác PnP trong CI. [Hướng dẫn](windows/camera-priority/README.md).

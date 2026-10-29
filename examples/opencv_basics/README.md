# Các bài học OpenCV gốc

Năm bài `01_camera.py`–`05_rule_based_inspection.py` được chuyển từ root, giữ nguyên byte/SHA256. Đây là ví dụ học tập, không phải các entrypoint sản phẩm.

Từ root repository:

```powershell
& '.\.venv\Scripts\python.exe' examples/opencv_basics/01_camera.py
```

Các bài dùng camera index theo code gốc và có thể chạy vòng lặp/cửa sổ khi import; chỉ chạy trực tiếp để học, không import vào sản phẩm hoặc unit test.

`requirements-observed.txt` là bản ghi phiên bản môi trường trước đây, được giữ nguyên từ requirements root cũ. Cài ứng dụng hiện tại qua `requirements.txt` ở root hoặc `vision/opencv/requirements.txt`; không coi phiên bản quan sát là bộ dependency AI.

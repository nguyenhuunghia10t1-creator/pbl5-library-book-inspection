# PBL5 · Library Book Inspection

Hệ thống thử nghiệm kiểm tra tình trạng và phân loại sách thư viện bằng Machine Vision và AI. Camera nhận ảnh bìa, OpenCV xác định vùng sách và đọc QR; phần mềm tổng hợp kết quả để tích hợp với cơ cấu phân loại ESP32.

[![Checks](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/workflows/checks.yml/badge.svg)](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/workflows/checks.yml)
![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)
![PlatformIO](https://img.shields.io/badge/Firmware-PlatformIO-F5822A?logo=platformio&logoColor=white)

## Phạm vi

- Nhận dạng bìa sách A6 và mã QR của từng bản sách.
- Căn chỉnh phối cảnh, kiểm tra độ nét và ánh sáng, thu ảnh có metadata.
- Phát triển nhận diện hai nhóm lỗi: `cover_tear` và `surface_stain`.
- Tích hợp phần mềm với ESP32 để phân loại sách vào khay.

Hiện tại có ứng dụng thu ảnh OpenCV và firmware mẫu. Mô hình AI, cơ cấu phân loại và luồng tích hợp đang phát triển. [Tiến độ](PROGRESS.md) · [Kiến trúc](docs/ARCHITECTURE.md) · [Kế hoạch](docs/PLAN.md).

## Cấu trúc repository

```text
firmware/esp32/           Firmware ESP32, cấu hình PlatformIO
vision/opencv/           Camera, xử lý bìa, QR, chất lượng ảnh và cấu hình
vision/yolo/             Phạm vi phát triển mô hình nhận diện lỗi
software/desktop/        Giao diện và điều phối ứng dụng thu ảnh
examples/opencv_basics/   Các bài thực hành OpenCV
scripts/                 Công cụ chạy và kiểm tra
tests/                  Kiểm thử tự động
docs/                   Tài liệu kỹ thuật và quyết định thiết kế
data/                   Hướng dẫn quản lý dữ liệu cục bộ
```

## Cài đặt

Yêu cầu: Git, Python và Windows để sử dụng camera DirectShow/MSMF. Firmware sử dụng PlatformIO; không cài chung công cụ firmware vào môi trường Python của ứng dụng.

```powershell
git clone https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection.git
cd pbl5-library-book-inspection
py -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
```

## Chạy ứng dụng

```powershell
& '.\.venv\Scripts\python.exe' -m vision.opencv --camera 0
```

Có thể chạy `scripts/windows/CaptureCovers.cmd`. Cấu hình camera và ngưỡng xử lý nằm trong [cover_capture.json](vision/opencv/configs/cover_capture.json).

| Phím | Chức năng |
|---|---|
| `B` | Hiệu chuẩn khi nền trống |
| `S` | Xử lý và lưu khung mới đạt điều kiện |
| `D` | Lưu mẫu cần kiểm tra lại |
| `M` | Chọn bốn góc trên ảnh tĩnh |
| `R` | Lật ảnh đầu ra 180° |
| `Q` | Thoát |

Dữ liệu được lưu tại `data/opencv/collection/`: ảnh gốc, ảnh đã căn, ảnh chẩn đoán và metadata. [Hướng dẫn sử dụng](docs/COVER_CAPTURE.md) · [Quy định dữ liệu](data/README.md).

## Kiểm thử

```powershell
& '.\.venv\Scripts\python.exe' scripts/check_repository.py
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Các test dùng ảnh tổng hợp và thiết bị mô phỏng, không yêu cầu camera hoặc ESP32. Kiểm thử thiết bị thật được ghi riêng trong [báo cáo kiểm chứng](docs/COVER_CAPTURE_VALIDATION.md).

## Firmware

Mở `smart-vision-inspection.code-workspace` bằng VS Code hoặc mở trực tiếp `firmware/esp32` trong PlatformIO.

```powershell
pio run --project-dir firmware/esp32
```

Cấu hình hiện tại: `esp32dev`, Arduino. [Hướng dẫn firmware](firmware/README.md).

## Phát triển cùng nhóm

Mỗi thay đổi thực hiện trên nhánh riêng, gửi pull request vào `main` và cần ít nhất một reviewer. Thành viên chưa có quyền ghi có thể fork repository rồi gửi pull request.

[Quy trình đóng góp](CONTRIBUTING.md) · [Issues](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/issues) · [Quyết định thiết kế](docs/DECISIONS.md).

## Hạn chế hiện tại

Preview còn phụ thuộc thời gian xử lý QR. Trên nền có đường ron hoặc bìa có viền gần màu nền, bộ chọn góc có thể nhảy giữa các ứng viên. Cần xử lý hai vấn đề này trước khi thu dữ liệu hàng loạt. Nhãn ảnh đạt điều kiện thu không đồng nghĩa với kết luận sách không có lỗi.

# Quy trình đóng góp

## Phân chia module

| Module | Trách nhiệm |
|---|---|
| `firmware/esp32` | Cảm biến, cơ cấu chấp hành, trạng thái thiết bị và giao tiếp máy tính |
| `vision/opencv` | Camera, vùng bìa, hình học, QR và chất lượng ảnh |
| `vision/yolo` | Dữ liệu có nhãn, huấn luyện, đánh giá và suy luận lỗi bìa |
| `software` | Giao diện, logic phân loại, lưu kết quả và tích hợp |

Mỗi module có người phụ trách và một thành viên review chéo. Thay đổi giao thức hoặc cấu trúc dữ liệu cần thống nhất giữa các module liên quan trước khi merge.

## Nhánh và commit

```powershell
git switch main
git pull --ff-only
git switch -c fix/opencv-cover-boundary
```

Tên nhánh: `feature/<module>-<task>`, `fix/<module>-<bug>`, `docs/<topic>`, `chore/<task>`. Commit mô tả thay đổi cụ thể, ví dụ `fix(opencv): reject frame-border candidates`.

Thành viên có quyền ghi push nhánh lên repository. Thành viên chưa có quyền ghi fork repository, push nhánh lên fork và mở pull request về `main`.

## Kiểm tra trước pull request

```powershell
& '.\.venv\Scripts\python.exe' scripts/check_repository.py
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
git diff --check
git status --short
```

Chỉ stage các tệp thuộc thay đổi. Không commit `.venv`, ảnh camera, metadata riêng, dataset, weights, credentials hoặc output build. [Quy định dữ liệu](data/README.md).

## Review

- Một PR tập trung vào một vấn đề, kèm mô tả hành vi trước/sau và issue liên quan.
- Ghi lệnh test, kết quả và điều kiện chưa kiểm tra; tách mô phỏng khỏi thiết bị thật.
- Có ít nhất một approval ngoài tác giả và các kiểm tra tự động đạt.
- Giải quyết các trao đổi review trước khi merge; không force-push vào `main`.
- Ưu tiên squash merge để lịch sử main phản ánh từng thay đổi hoàn chỉnh.

## Tích hợp

Core Vision không phụ thuộc giao diện, SQL hoặc GPIO. Phần mềm điều phối thông qua kết quả xử lý và adapter thiết bị. Firmware quản lý interlock và xác nhận đầu ra.

Thay đổi schema, cấu hình hoặc giao thức cần cập nhật [DECISIONS.md](docs/DECISIONS.md). Định nghĩa dùng chung chỉ đặt vào `shared/` khi có ít nhất hai module sử dụng. Tiến độ được cập nhật tại [PROGRESS.md](PROGRESS.md); lịch sử kỹ thuật tại [SESSION_LOG.md](docs/SESSION_LOG.md).

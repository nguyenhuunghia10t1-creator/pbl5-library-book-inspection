# Kiểm chứng preview bất đồng bộ — V02

Ngày đo: 2026-11-07, Windows 11 / Windows PowerShell 5.1, Python venv 3.14.3, OpenCV 5.0.0, NumPy 2.5.3. Baseline source 4d3b402a843f6240ccd31fbbc8e27ed8be658dd4. Kết quả sau sửa dưới đây được đo với HEAD + working-tree changes; commit triển khai/PR được ghi ở SESSION_LOG sau khi tồn tại.

## Hành vi được kiểm tra

- Camera latest-frame và vòng hiển thị/phím chạy riêng với worker geometry/QR, chỉ một request in-flight, không tích lũy hàng đợi frame cũ.
- Frame phân tích đi cùng properties/config revision/background reference. Raw/crop/QR/properties của bundle cùng nguồn; frame gửi trước S/D không được lưu cho yêu cầu mới.
- Mất camera/đổi camera session, B/C, tolerance, R, M làm vô hiệu hóa kết quả cũ. Lỗi xử lý được báo và frame sau có thể phục hồi. Kết quả quá tuổi frame bị bỏ; yêu cầu lưu hết hạn bị hủy.
- Preview raw mới không nhận corners/QR cũ; panel crop/QR có nhãn Analyzed/tuổi frame riêng. M lưu đúng ảnh đóng băng. Q/đóng cửa sổ không chờ decoder bị chặn.

## Test tự động và GUI synthetic

| Kiểm tra | Kết quả | Mức bằng chứng |
|---|---|---|
| Baseline checker và unittest trên commit sạch 4d3b402 | PASS; 54 tests, 0 failures/errors/skips; 5.035s | Phần mềm |
| Checker và validator sau sửa | PASS; 26 nguồn Python, links/workspace và task/state | Kiểm tra tĩnh/cấu trúc |
| Unittest discovery sau sửa, 09:41:08–09:41:20+07:00 | PASS; 71 tests = 54 cũ + 17 mới; 0 failures/errors/skips; 10.961s | Synthetic/fake camera/UI + worker thật |
| GUI với ảnh synthetic, đóng sau 2 giây | PASS, exit 0; ảnh READY/crop/QR PBL5-B04 và nhãn frame được xem lại | GUI ảnh tổng hợp, không webcam |
| git diff --check | PASS, exit 0 | Whitespace |
| Webcam và camera/backend thật | NOT_RUN | Chờ người dùng thử theo COVER_CAPTURE |
| Firmware/cơ cấu/AI/end-to-end hardware | NOT_RUN | Ngoài phạm vi V02 |

17 test mới ở tests/opencv/test_async_preview.py: worker bận/không backlog, exception/phục hồi, shutdown khi native decode bị chặn, reset trạng thái; UI tiếp tục frame/thoát, đóng cửa sổ, S/D đúng frame, camera lặp frame cũ, disconnect/reconnect, R, đổi background/config, kết quả quá hạn, M và không vẽ góc cũ lên frame mới. Test S cũ được đổi từ giả định lưu xong ở vòng UI thứ hai sang đợi bundle; vẫn buộc frame sau phím S.

## Benchmark tái lập

```powershell
& '.\.venv\Scripts\python.exe' scripts/benchmark_preview.py --baseline-ref 4d3b402 --frames 15 --delay 0.2
```

Lệnh thực dùng interpreter venv đã xác minh của checkout chính, exit 0 lúc 2026-11-07T09:38:21+07:00. GUI/camera/analysis trong benchmark đều giả lập; cố ý thêm 200 ms mỗi lần phân tích và 10 ms mỗi bước event. Baseline UI lấy bằng git show từ 4d3b402, chạy trong module riêng; không sửa code baseline.

| Chỉ số fixture | Trước | Sau |
|---|---:|---:|
| Số frame preview khác nhau | 15 | 15 |
| Thời gian vòng UI, giây | 3.1701 | 0.2111 |
| Median khoảng cách cập nhật, ms | 211.040 | 10.774 |
| Max khoảng cách cập nhật, ms | 211.613 | 11.284 |
| Số lần phân tích | 15 | 1 |

Worker không phân tích hết mọi frame; nó lấy mẫu mới nhất khi rảnh, không xử lý hàng đợi cũ. Đây là số đo scheduling của fixture, không là FPS camera thật, độ chính xác QR hay ngưỡng nghiệm thu. Không dùng các con số này làm cam kết hiệu năng thiết bị.

## Giới hạn và kiểm tra người dùng

Ghi PNG/metadata vẫn đồng bộ; thao tác lưu có thể dừng ngắn theo tốc độ ổ đĩa. Decoder native không hỗ trợ hủy cưỡng bức trong thread; khi đóng UI, worker daemon bỏ kết quả nếu trả về muộn, không sở hữu camera/file/window. Camera driver vẫn theo cơ chế release timeout sẵn có. Không thay geometry, QR parser hoặc schema bundle; lỗi mép bìa V01 và gate thực tế V03 vẫn cần bằng chứng riêng.

Artifact GUI local: `$env:TEMP/pbl5-v02-smoke-20261107/ui.png`; input/collection đều được đánh dấu synthetic và không commit. Xem [bài thử webcam ngắn](COVER_CAPTURE.md#thử-nhanh-preview-v02-trên-webcam). Mục tiêu/cỡ mẫu nghiệm thu hardware chưa duyệt vẫn là đề xuất, chờ tôi xác nhận; bài thử này chỉ thu bằng chứng hành vi, không tự PASS V03.

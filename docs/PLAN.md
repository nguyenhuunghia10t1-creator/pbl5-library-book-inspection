# Kế hoạch kỹ thuật

## Bước hiện tại: Colab

Theo yêu cầu tiếp nối ngày 2026-11-11, đã chuẩn bị [notebook Colab](../notebooks/damaged_books_colab.ipynb) và [hướng dẫn chạy](COLAB_TRAINING.md) cho split-reviewed-v1 (253/54/54 ảnh). Chờ người dùng chạy GPU thật; chưa nghiệm thu A02. Notebook chỉ train/validation; chọn ngưỡng và đánh giá test là bước sau. Phần ghi ưu tiên dữ liệu bên dưới là lịch sử trước khi có split.

Người dùng yêu cầu đồng bộ để team thử song song: [n640/s640/n960](TEAM_TRAINING.md), cùng dataset phát hành qua GitHub Releases, cùng seed42, mỗi lượt ghi thành viên/cấu hình và xuất CSV validation. Baseline n640 vẫn là điểm so sánh; chưa có model được chọn. D24 ghi phạm vi mở rộng này.

Các mốc dùng mã M01–M27 để theo dõi từ module độc lập tới nghiệm thu hệ thống. Trạng thái hiện tại xem [PROGRESS.md](../PROGRESS.md).

| Giai đoạn | Mốc | Đầu ra chính |
|---|---|---|
| Thị giác và dữ liệu | M01 Camera, M02 Geometry/quality, M03 QR, M04 Database, M05 Capture | Ảnh có nguồn gốc, identity và kết quả truy vết được |
| AI | M06 Nhãn/split, M07 YOLO baseline, M08 Threshold, M09 Decision policy | Dataset được kiểm, model có đánh giá, luật phân loại độc lập thiết bị |
| Phần mềm | M10 Backend, M11 HMI, M12 Simulator, M13 Protocol | Luồng job tái hiện được và hợp đồng giao tiếp có test |
| Điều khiển | M14 Firmware, M15 Băng tải, M16 Pusher A, M17 Pusher B, M18 Feedback | Từng cơ cấu được thử an toàn, xác nhận đầu ra thực |
| Tích hợp | M19 End-to-end, M20 Fault/recovery | Một sách/job, xử lý ngoại lệ và phục hồi |
| Đánh giá | M21 AI, M22 QR, M23 Cơ khí, M24 Toàn hệ thống | Chỉ số đo trên bộ thử có điều kiện rõ ràng |
| Bàn giao | M25 Freeze, M26 Demo, M27 Handover | Phiên bản đã kiểm thử, tài liệu và hướng dẫn vận hành |

## Công việc trước mắt

Theo kế hoạch được người dùng duyệt ngày 2026-11-10, ưu tiên hiện tại chuyển sang M06: [chuẩn hóa Damaged Books v1](DAMAGED_BOOKS_DATASET.md), bỏ Tag, remap Wornout 5→4, giữ nguồn bất biến; rà nhóm/nhãn/mẫu âm trước khi chia xấp xỉ 70/15/15 seed42. Phiên triển khai đầu chỉ làm dữ liệu; chưa tự bắt đầu Colab hoặc ứng dụng.

Thứ tự sau cổng dữ liệu: Colab YOLO11n (640, tối đa100 epoch, patience20, batch16, seed42) → threshold validation (F2 Ripped, F1 còn lại) → AI/barcode desktop → policy/simulator A/B/C → model thật và kiểm camera. Test chỉ dùng đánh giá cuối. Web HMI/firmware/GPIO/serial thật để đợt riêng; bộ ảnh camera độc lập vẫn cần cho đánh giá miền thực tế. Quyết định mới xem D20–D23; các bài collector/camera cũ dưới đây giữ làm lịch sử và việc chưa nghiệm thu.

- Sửa chọn tứ giác trên nền có đường ron, kiểm thử hồi quy với ảnh đã thu.
- Cải thiện tốc độ preview; giữ liên kết frame/QR/metadata khi xử lý bất đồng bộ.
- Thu pilot với camera cố định, ánh sáng ổn định và nhiều thiết kế bìa.

## Điều kiện nghiệm thu

Mỗi mốc cần đầu ra thực và bằng chứng phù hợp. Test tự động, test mô phỏng, camera và phần cứng được ghi riêng. Một module build được chưa đủ để nghiệm thu vận hành thiết bị. Chia dataset theo cuốn/thiết kế bìa và giữ tập test cuối độc lập.

Thay đổi giao thức, dữ liệu hoặc phạm vi được ghi tại [DECISIONS.md](DECISIONS.md).

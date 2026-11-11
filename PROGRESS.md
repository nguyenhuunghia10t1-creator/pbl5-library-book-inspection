# Tiến độ phát triển
## Cập nhật 2026-11-11 — rà nhóm vòng 2

Đã xem toàn bộ 286 ảnh chưa nhóm trên bảng ảnh, đối chiếu lớn các cặp có căn cứ: thêm 65 ảnh vào nhóm và tách một nhóm ghép nhầm (sách nuôi cá / sách lãnh đạo). Hiện có 399/620 ảnh trong 151 nhóm trực quan; 221 ảnh chưa xác định được danh tính được liệt kê riêng tại `grouping-assist/quarantine-round2.csv`. Không gán ID giả cho ảnh đơn lẻ chỉ để đủ số lượng. Chưa chứng minh mọi quan hệ giữa các nhóm đã được nhận diện.

Đã lưu review.csv, sao lưu trước sửa và tạo lại review.html. PASS: giữ nguyên 620 ID và mọi trạng thái duyệt, gồm 51 mẫu âm; 620 checksum ảnh và tệp nhãn khớp manifest; HTML khớp CSV. Bằng chứng cục bộ: `data/local/damaged_books_v1/grouping-assist/round2-result.json` và `round2-validation.txt`. Các số 334/286 bên dưới là lịch sử.

**Một việc tiếp theo:** rà nhãn trên phần ảnh đã gán nhóm; 221 ảnh chưa rõ tiếp tục được cách ly. Tổng 569 nhãn còn pending; chưa chia tập, train hay tích hợp AI. Người dùng không cần nhập lại nhóm. H14/A01 chưa hoàn tất.

## Cập nhật 2026-11-11 — rà nhóm hỗ trợ

Đã lưu 334 ảnh vào 124 nhóm trực quan; 286 ảnh chưa xác định nhóm được để riêng. Giữ nguyên 51 mẫu âm đã duyệt; 569 nhãn vẫn pending. CSV đã sao lưu, review.html đã tạo lại. Báo cáo nằm tại vùng dữ liệu cục bộ `grouping-assist/visual-review-report.json`. H14 chưa hoàn tất; chưa chia tập hoặc huấn luyện. Người dùng đã giao việc rà nhóm cho trợ lý; bước tiếp theo là xử lý các góc chụp chưa rõ, không giao lại toàn bộ ảnh cho người dùng.

## Cập nhật 2026-11-11 — mẫu âm đã được người dùng duyệt

Kiểm tra CSV PASS: 620 dòng/620 ID khớp manifest, đủ 51 ảnh có `label_review=approved` và `negative_review=approved`. Đây là xác minh lưu lựa chọn người dùng, không đánh giá độc lập lại nhãn. Còn 569 nhãn pending và 618 ảnh chưa nhóm; H14/A01 chưa hoàn tất.

**Đúng một việc tiếp theo:** gán nhóm sách theo cuốn/thiết kế bìa. Nạp CSV mới nhất khi mở lại trang để giữ kết quả đã duyệt. Chưa chia tập hoặc train; các mục dưới là lịch sử.

## Điểm tiếp tục 2026-11-10 — Damaged Books

Bước đầu đã thực hiện trên nhánh `feat/damaged-books-dataset`: chuyển 620 ảnh sang năm lớp, 3.610 hộp, bỏ 379 Tag, giữ 34 nhãn rỗng; audit toàn bộ ảnh/nhãn khớp ZIP nguồn. Có trang rà nhóm/nhãn và công cụ split theo nhóm. Kiểm tra repository/ledger PASS; 102 unittest PASS, gồm 9 test dataset và 93 hồi quy collector.

Split nguồn 618/1/1 không đủ đánh giá và có cặp cùng cuốn giữa train/test. Chưa tạo split mới: 620 ảnh còn pending nhãn, 618 ảnh chưa có nhóm, 51 ứng viên mẫu âm chưa duyệt. Chưa train, chưa nghiệm thu AI/camera/simulator. Phần nháp các bước sau được giữ riêng cục bộ, không gộp vào nhánh dữ liệu.

**Đúng một việc tiếp theo:** mở `review.html` cục bộ để rà nhóm sách và nhãn, kiểm riêng 51 ứng viên âm; lưu `review.csv`. [Hướng dẫn](docs/DAMAGED_BOOKS_DATASET.md) · [TASKS](docs/codex/TASKS.md) · [STATE](docs/codex/STATE.md). Các bảng bên dưới là lịch sử, không phải trạng thái song song.

Cập nhật: 2026-10-29.

Repository: [pbl5-library-book-inspection](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection). Kiểm tra tự động: [GitHub Actions](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/workflows/checks.yml).

| Hạng mục | Trạng thái | Kết quả |
|---|---|---|
| Cấu trúc repository và hướng dẫn nhóm | Hoàn thành | Tách firmware, vision, software, ví dụ và test |
| Camera và thu ảnh | Đang phát triển | DirectShow nhận khung 1280×720; có bundle ảnh và metadata |
| Hình học bìa A6 | Đang phát triển | Căn phối cảnh được; chọn góc chưa ổn định trên nền có đường ron |
| QR | Đang phát triển | Hỗ trợ PBL5/LIB1; đã đọc PBL5-B08 trên bìa thật |
| Firmware ESP32 | Khởi tạo | Code mẫu Arduino build được; chưa tích hợp cơ cấu |
| Mô hình phát hiện lỗi | Chưa triển khai | Hai lớp mục tiêu: cover_tear, surface_stain |
| Database, policy và tích hợp | Chưa triển khai | Theo kế hoạch kỹ thuật |

## Kiểm chứng

- 22 test Python đạt: hình học/QR, camera mô phỏng, lưu dữ liệu và đường dẫn chạy.
- 23 test mô phỏng của tiện ích camera Windows đạt.
- Firmware mẫu build thành công với PlatformIO; chưa thử upload hoặc vận hành cơ cấu.
- CLI/GUI thu ảnh tổng hợp và khôi phục manifest hoạt động.

Trong đợt kiểm tra 12 khung bìa B08, 5 khung đọc được QR; 7 khung dừng tại bước kiểm tra hình học. Chưa có khung đạt READY liên tiếp. Đây là kết quả thử một bố trí, không phải phép đo độ chính xác tổng quát của QR.

## Ưu tiên

1. Ổn định bộ chọn mép ngoài bìa, loại ứng viên dính đường ron hoặc biên khung.
2. Tách cập nhật preview khỏi xử lý QR.
3. Kiểm tra pilot trên nhiều bìa và điều kiện chiếu sáng trước khi thu dataset.

[Kiến trúc](docs/ARCHITECTURE.md) · [Kế hoạch](docs/PLAN.md) · [Kiểm chứng](docs/COVER_CAPTURE_VALIDATION.md)


## Điểm tiếp tục từ 2026-11-07

[docs/codex/TASKS.md](docs/codex/TASKS.md) là nguồn sự thật duy nhất về tiến độ task; [STATE.md](docs/codex/STATE.md) là điểm tiếp tục, [ROADMAP.md](docs/codex/ROADMAP.md) là kế hoạch và [WORKFLOW.md](docs/codex/WORKFLOW.md) là quy trình phiên. Các bảng phía trên được giữ như snapshot lịch sử ngày 2026-10-29, không cập nhật thành bản trạng thái song song. Đọc [CODEBASE_MAP.md](docs/codex/CODEBASE_MAP.md) để đối chiếu audit và giới hạn bằng chứng.

Hướng dẫn thử bìa sáng/tối: [COVER_CAPTURE — V07](docs/COVER_CAPTURE.md#thử-bìa-sángtối-v07-trên-webcam). Kết quả phần mềm và giới hạn: [COLOR_BACKGROUND_VALIDATION](docs/COLOR_BACKGROUND_VALIDATION.md); tiến độ và điểm tiếp tục vẫn xem [TASKS](docs/codex/TASKS.md) và [STATE](docs/codex/STATE.md).

Hướng dẫn dùng điện thoại: [DroidCam/MSMF](docs/COVER_CAPTURE.md#camera-điện-thoại-qua-droidcam). Tiến độ và phần kiểm chứng thực tế vẫn theo [TASKS](docs/codex/TASKS.md) và [STATE](docs/codex/STATE.md).

Giao diện thu ảnh đã có hướng dẫn tiếng Việt: [cách dùng](docs/COVER_CAPTURE.md#giao-diện-tiếng-việt); theo dõi V08 tại [TASKS](docs/codex/TASKS.md), điểm tiếp tục tại [STATE](docs/codex/STATE.md).

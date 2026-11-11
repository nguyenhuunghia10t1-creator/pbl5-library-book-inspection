# Tiến độ phát triển
## Cập nhật 2026-11-11 — kiểm tra độc lập nhóm và tạo split `split-reviewed-v1` (H14, A01)

Đã rà soát độc lập toàn bộ 148 nhóm của 361 ảnh đạt (`grouping-assist/group-independence-sheets/groups-148-00.jpg`..`groups-148-14.jpg`): tách `idx:282` (gáy sách *다산선생 지식경영법* bị ghép nhầm vào `visual_group_026`) sang `visual_group_073`, đồng thời gộp 21 cụm nhóm cùng cuốn sách (mặt trước/gáy/mặt sau) hoặc cùng thiết kế bìa bộ sách (loại bỏ 27 mã nhóm trùng). Sau khi gộp, toàn bộ 399 ảnh có nhóm thuộc **124 nhóm trực quan**, trong đó **361 ảnh đạt (`approved`) thuộc 121 nhóm độc lập** (3 nhóm chỉ có ảnh `rejected`: `visual_group_052`, `visual_group_062`, `visual_group_111`). Giữ cách ly 259 ảnh (38 ảnh `rejected` + 221 ảnh chưa rõ nhóm).

Đã sao lưu `review-before-group-merge-42e09cf254e0.csv`, cập nhật `prepared-verified/review.csv` (SHA256 `668f59cfb4b9139896764f11dd7875b6471168c039dab523dda30348882dc183`), tạo lại `prepared-verified/review.html` và chạy `python -m vision.yolo.prepare split` tạo `data/local/damaged_books_v1/split-reviewed-v1` cùng gói `split-reviewed-v1.zip` (SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`, version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`, seed `42`):

- **Train:** **253 ảnh** (`70,08%`), **83 nhóm** (`68,60%`) — 1.399 hộp (`Barcode`: 77, `Notch`: 250, `Ripped`: 173, `Spot`: 355, `Wornout`: 544).
- **Val:** **54 ảnh** (`14,96%`), **18 nhóm** (`14,88%`) — 327 hộp (`Barcode`: 25, `Notch`: 53, `Ripped`: 39, `Spot`: 65, `Wornout`: 145).
- **Test:** **54 ảnh** (`14,96%`), **20 nhóm** (`16,53%`) — 267 hộp (`Barcode`: 13, `Notch`: 32, `Ripped`: 43, `Spot`: 60, `Wornout`: 119).
- **Quarantined:** **259 ảnh** (không sao chép vào các tập). Giao nhau nhóm giữa `train`/`val`/`test` = `0`.

H14 và A01 hoàn tất (`DONE`). Báo cáo chi tiết: `data/local/damaged_books_v1/grouping-assist/group-independence-round4.json` và `data/local/damaged_books_v1/split-reviewed-v1/split_manifest.json`. Các mục bên dưới là lịch sử.

**Đúng một việc tiếp theo:** chuẩn bị/xác minh phiên Colab GPU (`H08` / `A02`) để huấn luyện YOLO11n trên gói `split-reviewed-v1.zip` (giữ nguyên tập `test` độc lập, chỉ chọn ngưỡng trên `val`). Chưa huấn luyện trong lượt này.

## Cập nhật 2026-11-11 — rà nhãn 368 ảnh đã gán nhóm

Đã xem trực tiếp toàn bộ 368 ảnh có nhóm đang `label_review=pending` trên 46 bảng đối chiếu song song ảnh gốc / ảnh vẽ hộp nhãn (`grouping-assist/label-sheets/label-sheet-00.jpg`..`label-sheet-45.jpg`). Kết quả trên 368 ảnh: duyệt `approved` 330 ảnh có hộp và lớp đúng; đánh dấu `rejected` 38 ảnh có nhãn sai lớp (tem chữ Tag bị gán nhầm Barcode/Spot), thiếu hộp ở vết rách/mòn/bẩn rõ hoặc hộp nhiễu đè lên chữ in/hình vẽ/vệt lóa.

Tính trên toàn bộ 399 ảnh đã gán nhóm (151 nhóm trực quan): 361 ảnh `approved` (gồm 330 ảnh có hộp lỗi + 31 mẫu âm đã duyệt trước đó, phủ 148/151 nhóm với 1.993 hộp đủ 5 lớp: Barcode 115, Notch 335, Ripped 255, Spot 480, Wornout 808), 38 ảnh `rejected` và 0 ảnh `pending`. Toàn dataset 620 ảnh: 381 `approved`, 38 `rejected`, 201 `pending` (toàn bộ 201 ảnh `pending` thuộc 221 ảnh chưa rõ nhóm đang cách ly). Giữ nguyên 51/51 mẫu âm đã duyệt và không sửa tệp nhãn trong `prepared-verified`.

Đã sao lưu `review-before-label-review-076f7499062b.csv`, cập nhật `prepared-verified/review.csv` và `prepared-verified/review.html`. Kiểm chứng PASS: 620 ID duy nhất, 620 checksum ảnh và tệp nhãn khớp `manifest.json`, HTML khớp CSV, 221 ID cách ly khớp `quarantine-round2.csv`. Báo cáo chi tiết: `data/local/damaged_books_v1/grouping-assist/label-review-round3.json`, `questionable-labels-round3.csv` và `label-review-validation.txt`. Các mục bên dưới là lịch sử.

**Đúng một việc tiếp theo:** xác nhận xử lý 38 ảnh `rejected` (giữ cách ly cùng 221 ảnh chưa rõ nhóm hay tạo bản sửa nhãn mới) và kiểm tra quan hệ mặt trước/mặt sau còn nghi vấn trước khi chạy `A01` chia tập `train`/`val`/`test`. Chưa chia tập, chưa train hay tích hợp AI.

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

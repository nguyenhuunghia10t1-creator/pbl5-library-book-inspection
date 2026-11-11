Active task: NONE
Last updated: 2026-11-11
Branch: feat/damaged-books-dataset
Last green commit: 10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9

## Resume notes

2026-11-11 vòng 2 (hiện tại): đã rà toàn bộ 286 ảnh còn lại, thêm65 ảnh và tách một nhóm ghép nhầm sách nuôi cá/lãnh đạo. Hiện399 ảnh/151 nhóm,221 ảnh chưa rõ được cách ly trong grouping-assist/quarantine-round2.csv. CSV đã sao lưu, HTML tạo lại. PASS620 ảnh/nhãn khớp manifest, mọi trạng thái duyệt giữ nguyên, gồm51 mẫu âm. Báo cáo round2-result.json và round2-validation.txt. Chưa đủ căn cứ tuyên bố split không rò rỉ;569 nhãn vẫn pending. Các số334/286 bên dưới là lịch sử.

2026-11-11 (mới nhất): người dùng giao trợ lý rà nhóm. Đã ghi 334 ảnh / 124 nhóm trực quan, giữ nguyên 51 duyệt âm; 286 ảnh chưa có nhóm và 569 nhãn pending. Nhóm có thể cần gộp thêm qua góc chụp khác, chưa dùng để split. Đã sao lưu CSV và tạo lại HTML. Báo cáo local: grouping-assist/visual-review-report.json. Các số 618 chưa nhóm bên dưới là lịch sử.

2026-11-11: đã kiểm CSV người dùng lưu, 620 dòng/ID khớp manifest; cả 51 ứng viên âm có hai trạng thái approved. Còn 569 nhãn pending, 618 ảnh chưa nhóm. Xác minh lưu kết quả PASS; chưa đánh giá độc lập lại nhãn hoặc hoàn tất H14/A01. Các số pending trong ghi chú 2026-11-10 bên dưới là lịch sử.

Bước đầu theo kế hoạch người dùng: chuẩn hóa Damaged Books v1 năm nhãn và kiểm split, chỉ phạm vi A05. Nhánh từ feat/vietnamese-capture-ui bdf0c00, giữ preview/collector/UI tiếng Việt. Checkout chính main và hai hồ sơ sửa sẵn không bị gộp vào commit. Xem [hướng dẫn dataset](../DAMAGED_BOOKS_DATASET.md), [TASKS](TASKS.md) và SESSION_LOG 2026-11-10 phiên 2.

Đã chuyển 620 ảnh, 3.610 hộp; bỏ 379 Tag; giữ 34 nhãn rỗng; 51 ứng viên mẫu âm cần duyệt. Checksum nguồn/ảnh/nhãn đã đối chiếu với ZIP. Version damaged-books-v1-five-8f203ddd57d4. Split nguồn 618/1/1 không hợp lệ để đánh giá; đã xem cặp train IMG_1316 / test IMG_7 cùng sách. Nhóm của cặp được ghi nhưng nhãn vẫn pending; các ảnh còn lại chưa có nhóm đã duyệt.

Last green ở đầu file là commit nguồn đã được CI GitHub xác nhận completed/success: [run 42758217749](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/runs/42758217749). Kết quả local trước commit ghi riêng trong SESSION_LOG. Không suy AI accuracy, webcam hoặc hardware PASS từ unittest.

## Human actions pending

**Đúng một việc tiếp theo: H14 — rà nhãn phần ảnh đã gán nhóm.** Giữ riêng221 ảnh chưa rõ; người dùng không cần nhập lại nhóm. Tổng569 nhãn còn pending. Pending/rejected không được đưa vào split; chưa chạy Colab hoặc thử phần cứng.

A01 giữ BLOCKED tới khi H14 đủ đầu vào. Quy tắc lớp/route và chọn Colab đã được duyệt D20–D23, không hỏi lại quyết định đó. Bộ camera độc lập, model thật, latency và simulator thuộc các bước sau, chưa nghiệm thu. Các gate IO/board/reviewer/KPI chưa có bằng chứng vẫn giữ trong TASKS.

Bản nháp app/Colab/simulator đã được lưu riêng ở nhánh cục bộ feat/damaged-books-abc, commit b46faf8, chưa chấp nhận, chưa xuất bản và không nằm trong nhánh bước dữ liệu. Không tự kích hoạt hoặc coi đó là task hoàn thành.

Các PR nền #5/#6/#9/#10 chưa được merge theo bằng chứng phiên trước; xác minh lại remote khi tiếp tục. Không merge hoặc đóng PR của team. V05/#7 và nhánh detector/UI team/#8 chưa được audit tích hợp ở đây.

## Xuất bản bước dữ liệu

Commit nguồn 10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9 đã push và được ls-remote xác nhận. [PR #11](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/11) OPEN, base feat/vietnamese-capture-ui, chưa merge. [Nhánh mới](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/tree/feat/damaged-books-dataset) · [ZIP mã nguồn](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/archive/refs/heads/feat/damaged-books-dataset.zip). ZIP mã nguồn không chứa dataset/model; dùng bản dữ liệu cục bộ đã audit. Bằng chứng local102 tests nằm ở lượt working tree trước commit; CI theo SHA nguồn đọc riêng trong nhật ký.

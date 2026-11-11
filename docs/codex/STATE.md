Active task: NONE
Last updated: 2026-11-11
Branch: feat/damaged-books-colab
Last green commit: 10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9

## Resume notes

Hiện tại: notebook Colab đã chuẩn bị, xem docs/COLAB_TRAINING.md. Split thật253/54/54 và checksum đã kiểm; rà nhóm/nhãn dựa trên báo cáo Gemini vòng4. GPU train NOT_RUN, H08/A02 BLOCKED. Việc tiếp theo duy nhất: mở notebook trên Colab GPU và chạy với split-reviewed-v1.zip. Ghi chú rà nhóm bên dưới là lịch sử.

2026-11-11 vòng 2 (hiện tại): đã rà toàn bộ 286 ảnh còn lại, thêm65 ảnh và tách một nhóm ghép nhầm sách nuôi cá/lãnh đạo. Hiện399 ảnh/151 nhóm,221 ảnh chưa rõ được cách ly trong grouping-assist/quarantine-round2.csv. CSV đã sao lưu, HTML tạo lại. PASS620 ảnh/nhãn khớp manifest, mọi trạng thái duyệt giữ nguyên, gồm51 mẫu âm. Báo cáo round2-result.json và round2-validation.txt. Chưa đủ căn cứ tuyên bố split không rò rỉ;569 nhãn vẫn pending. Các số334/286 bên dưới là lịch sử.

2026-11-11 (mới nhất): người dùng giao trợ lý rà nhóm. Đã ghi 334 ảnh / 124 nhóm trực quan, giữ nguyên 51 duyệt âm; 286 ảnh chưa có nhóm và 569 nhãn pending. Nhóm có thể cần gộp thêm qua góc chụp khác, chưa dùng để split. Đã sao lưu CSV và tạo lại HTML. Báo cáo local: grouping-assist/visual-review-report.json. Các số 618 chưa nhóm bên dưới là lịch sử.

2026-11-11: đã kiểm CSV người dùng lưu, 620 dòng/ID khớp manifest; cả 51 ứng viên âm có hai trạng thái approved. Còn 569 nhãn pending, 618 ảnh chưa nhóm. Xác minh lưu kết quả PASS; chưa đánh giá độc lập lại nhãn hoặc hoàn tất H14/A01. Các số pending trong ghi chú 2026-11-10 bên dưới là lịch sử.

Bước đầu theo kế hoạch người dùng: chuẩn hóa Damaged Books v1 năm nhãn và kiểm split, chỉ phạm vi A05. Nhánh từ feat/vietnamese-capture-ui bdf0c00, giữ preview/collector/UI tiếng Việt. Checkout chính main và hai hồ sơ sửa sẵn không bị gộp vào commit. Xem [hướng dẫn dataset](../DAMAGED_BOOKS_DATASET.md), [TASKS](TASKS.md) và SESSION_LOG 2026-11-10 phiên 2.

Đã chuyển 620 ảnh, 3.610 hộp; bỏ 379 Tag; giữ 34 nhãn rỗng; 51 ứng viên mẫu âm cần duyệt. Checksum nguồn/ảnh/nhãn đã đối chiếu với ZIP. Version damaged-books-v1-five-8f203ddd57d4. Split nguồn 618/1/1 không hợp lệ để đánh giá; đã xem cặp train IMG_1316 / test IMG_7 cùng sách. Nhóm của cặp được ghi nhưng nhãn vẫn pending; các ảnh còn lại chưa có nhóm đã duyệt.

Last green ở đầu file là commit nguồn đã được CI GitHub xác nhận completed/success: [run 42758217749](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/runs/42758217749). Kết quả local trước commit ghi riêng trong SESSION_LOG. Không suy AI accuracy, webcam hoặc hardware PASS từ unittest.

## Human actions pending

Mở notebooks/damaged_books_colab.ipynb trên Colab, chọn GPU, tải split-reviewed-v1.zip và chạy. Chưa train/threshold/test/camera; A02/H08 chờ bằng chứng GPU. Không yêu cầu rà lại các nhóm đã duyệt trong bước này.

## Xuất bản bước dữ liệu

Commit nguồn 10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9 đã push và được ls-remote xác nhận. [PR #11](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/11) OPEN, base feat/vietnamese-capture-ui, chưa merge. [Nhánh mới](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/tree/feat/damaged-books-dataset) · [ZIP mã nguồn](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/archive/refs/heads/feat/damaged-books-dataset.zip). ZIP mã nguồn không chứa dataset/model; dùng bản dữ liệu cục bộ đã audit. Bằng chứng local102 tests nằm ở lượt working tree trước commit; CI theo SHA nguồn đọc riêng trong nhật ký.

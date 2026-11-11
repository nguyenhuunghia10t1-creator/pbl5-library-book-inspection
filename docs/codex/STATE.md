Active task: NONE
Last updated: 2026-11-11
Branch: feat/damaged-books-colab
Last green commit: 10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9

## Resume notes

Hiện tại: đã đồng bộ hồ sơ Gemini cbe14bb và công cụ team b310c53 lên remote. Dataset release damaged-books-reviewed-v1 đã public; tải lại checksum PASS. Notebook tự tải dữ liệu, cấu hình n640/s640/n960, mã thành viên và CSV validation. 111 tests PASS. H08/A02 vẫn chờ GPU thật; một việc tiếp theo: team chạy Colab với mã thành viên/cấu hình riêng. Xem TEAM_TRAINING.md.

2026-11-11 vòng 4 (hiện tại): đã kiểm tra độc lập toàn bộ 148 nhóm của 361 ảnh đạt (`groups-148-00.jpg`..`groups-148-14.jpg`), tách `idx:282` sang `visual_group_073` và gộp 21 cụm nhóm cùng sách/thiết kế bìa thành **121 nhóm độc lập** (361 ảnh `approved`), giữ cách ly **259 ảnh** (38 `rejected` + 221 chưa rõ nhóm). Đã cập nhật `review.csv` (SHA256 `668f59cfb4b9139896764f11dd7875b6471168c039dab523dda30348882dc183`), `review.html` và chạy `vision.yolo.prepare split` tạo `split-reviewed-v1` + `split-reviewed-v1.zip` (SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`, version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`, seed `42`): `train` 253 ảnh/83 nhóm, `val` 54 ảnh/18 nhóm, `test` 54 ảnh/20 nhóm; đủ 5 lớp ở cả 3 tập, giao nhau nhóm = 0. `H14` và `A01` đã `DONE`.

2026-11-11 vòng 3: đã rà trực tiếp toàn bộ 368 ảnh có nhóm còn pending trên 46 bảng ảnh đối chiếu (`label-sheet-00.jpg`..`label-sheet-45.jpg`); duyệt `approved` 330 ảnh, đánh dấu `rejected` 38 ảnh có nhãn sai lớp/thiếu hộp/hộp nhiễu. Trong 399 ảnh đã gán nhóm (151 nhóm): 361 `approved` (thuộc 148 nhóm, 1.993 hộp đủ 5 lớp), 38 `rejected`, 0 `pending`. Toàn dataset 620 ảnh: 381 `approved`, 38 `rejected`, 201 `pending` (thuộc 221 ảnh chưa rõ nhóm cách ly); giữ nguyên 51/51 mẫu âm đã duyệt. Đã sao lưu CSV, cập nhật `review.csv` và `review.html`; PASS đối chiếu 620 ảnh/nhãn với manifest và CSV/HTML. Báo cáo: `grouping-assist/label-review-round3.json`, `questionable-labels-round3.csv`, `label-review-validation.txt`. Các số 569 pending bên dưới là lịch sử.



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

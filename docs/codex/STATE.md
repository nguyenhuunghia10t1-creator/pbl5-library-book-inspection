Active task: NONE
Last updated: 2026-11-10
Branch: feat/damaged-books-dataset
Last green commit: 91237589588c8023fd9420994e7fef8290ff9436

## Resume notes

Bước đầu theo kế hoạch người dùng: chuẩn hóa Damaged Books v1 năm nhãn và kiểm split, chỉ phạm vi A05. Nhánh từ feat/vietnamese-capture-ui bdf0c00, giữ preview/collector/UI tiếng Việt. Checkout chính main và hai hồ sơ sửa sẵn không bị gộp vào commit. Xem [hướng dẫn dataset](../DAMAGED_BOOKS_DATASET.md), [TASKS](TASKS.md) và SESSION_LOG 2026-11-10 phiên 2.

Đã chuyển 620 ảnh, 3.610 hộp; bỏ 379 Tag; giữ 34 nhãn rỗng; 51 ứng viên mẫu âm cần duyệt. Checksum nguồn/ảnh/nhãn đã đối chiếu với ZIP. Version damaged-books-v1-five-8f203ddd57d4. Split nguồn 618/1/1 không hợp lệ để đánh giá; đã xem cặp train IMG_1316 / test IMG_7 cùng sách. Nhóm của cặp được ghi nhưng nhãn vẫn pending; các ảnh còn lại chưa có nhóm đã duyệt.

Last green ở đầu file là bằng chứng lịch sử đã tồn tại, không phải SHA của working tree mới. Lệnh và kết quả mới ghi trong SESSION_LOG. Không suy AI accuracy, webcam hoặc hardware PASS từ unittest.

## Human actions pending

**Đúng một việc tiếp theo: H14 — mở review.html, rà nhóm theo cuốn/thiết kế và nhãn; kiểm riêng 51 ứng viên âm.** Tải review.csv, giữ bản dự phòng; đặt lại đúng thư mục prepared sau khi kiểm. Pending/rejected không được đưa vào split. Chưa chạy Colab, chưa yêu cầu lắp phần cứng hoặc thu bộ camera ngay bước này.

A01 giữ BLOCKED tới khi H14 đủ đầu vào. Quy tắc lớp/route và chọn Colab đã được duyệt D20–D23, không hỏi lại quyết định đó. Bộ camera độc lập, model thật, latency và simulator thuộc các bước sau, chưa nghiệm thu. Các gate IO/board/reviewer/KPI chưa có bằng chứng vẫn giữ trong TASKS.

Bản nháp app/Colab/simulator đã được lưu riêng ở nhánh cục bộ feat/damaged-books-abc, commit b46faf8, chưa chấp nhận, chưa xuất bản và không nằm trong nhánh bước dữ liệu. Không tự kích hoạt hoặc coi đó là task hoàn thành.

Các PR nền #5/#6/#9/#10 chưa được merge theo bằng chứng phiên trước; xác minh lại remote khi tiếp tục. Không merge hoặc đóng PR của team. V05/#7 và nhánh detector/UI team/#8 chưa được audit tích hợp ở đây.

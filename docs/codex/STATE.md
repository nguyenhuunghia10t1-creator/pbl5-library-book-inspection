Active task: NONE
Last updated: 2026-11-07
Branch: chore/codex-harness
Last green commit: 37d98d2031996b424c8441633617ddd49223b061

## Resume notes

Đọc TASKS.md → WORKFLOW.md → đuôi ../SESSION_LOG.md → quyết định liên quan trong ../DECISIONS.md. Trạng thái task chỉ ở TASKS; không cập nhật bản sao tại đây.

Worktree harness riêng trên chore/codex-harness; checkout chính vẫn main với PROGRESS/SESSION_LOG sửa sẵn được giữ nguyên, không đưa vào PR. Commit gốc và remote main đã đọc cùng SHA d431f10fbb79dc086c8912702552463ca20262ab. Không reset/stash/checkout đè thay đổi cũ. PR harness: [#5](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5), mở vào main, chưa merge; cần H02 review. Toàn bộ thay đổi phiên nằm trong worktree của nhánh harness, không ở checkout chính đang có sửa sẵn.

Task CODEX kế tiếp đề xuất: **V02**, tách preview khỏi geometry/QR bằng fixture chậm/lỗi và ràng buộc frame. V01 cần mẫu hồi quy được xác nhận H04. Không tự bắt đầu V02 khi kết thúc phiên harness. Nếu PR nền chưa merge, fetch rồi tạo nhánh fix/preview-v02 dựa trên origin/chore/codex-harness và PR xếp tầng base chore/codex-harness; ghi dependency PR, không merge thay người. Nếu đã merge, tạo nhánh từ origin/main mới nhất. Kiểm working tree trước mọi chuyển nhánh; chọn worktree sạch khi cần.

Lệnh bắt đầu sau khi xác minh checkout sạch và PR nền (PowerShell, PYTHON là interpreter đã kiểm):

```powershell
git status --short --branch
git fetch origin
git switch -c fix/preview-v02 origin/chore/codex-harness
& $PYTHON scripts/check_repository.py
& $PYTHON scripts/check_codex_state.py
& $PYTHON -m unittest discover -s tests -v
```

Chỉ sau baseline và chọn V02 mới đổi TASKS sang IN_PROGRESS và Active task sang V02. Lệnh trên không được tự thực hiện trong phiên H01.

## Baseline đã đo

Last green commit ở đầu tệp là commit harness 37d98d2031996b424c8441633617ddd49223b061 đã tồn tại và được kiểm nguyên trạng trên worktree sạch lúc 2026-11-07T09:03:20–09:03:25+07:00: check_repository PASS (23 source), check_codex_state PASS, unittest discovery PASS 54 tests/0 failures/0 errors/0 skips (4.515s), git diff --check PASS. Commit metadata sau đó chỉ ghi kết quả/PR/task; không ghi SHA tự tham chiếu.

Baseline gốc d431f10 lúc 08:53:10+07:00: checker PASS 21 source và 22 tests PASS. Những lượt kiểm khi đang sửa được ghi HEAD + working-tree changes trong SESSION_LOG, không coi là kiểm HEAD nguyên trạng.

Windows 11, PowerShell 5.1, venv Python 3.14.3, OpenCV 5.0.0, NumPy 2.5.3; dùng interpreter của checkout chính cho worktree sạch, không cài dependency mới. Build scaffold và 23 test policy camera mô phỏng cũng PASS; xem lệnh/thời điểm/giới hạn trong [SESSION_LOG](../SESSION_LOG.md). Đây không phải kiểm chứng camera/cơ cấu thật hoặc kết quả CI remote của PR mới.

## Human actions pending

- **H04 + H05, ưu tiên dữ liệu:** gửi vị trí gói raw/crop/debug/metadata ngoài Git, mã cuốn/điều kiện chụp và ví dụ nhãn rách/bẩn/ca biên được xác nhận. Mở khóa V01 rồi A01 sau pilot; không đăng ảnh riêng vào PR.
- **H03, ưu tiên phần cứng:** ảnh/model board, danh mục sensor/driver/motor/servo, điện áp/nguồn/tải, hành trình/home/endstop/feedback, kết nối PC. Gửi bảng IO và tài liệu thiết bị; mở khóa thiết kế S05/F01, chưa nạp khi chưa review.
- **H06 + H12:** phản hồi bảng route và mapping QR enums; mở khóa S01/V04.
- **H07:** phản hồi mục tiêu/cỡ mẫu/điều kiện nghiệm thu; mở khóa việc kết luận các gate/đánh giá, không chặn công việc fixture độc lập.
- **H08 + H09:** thông số máy train và mẫu schema danh mục sách/nguồn hợp pháp; mở khóa A02/B02.
- **H10 + H11 + H02:** tên người phụ trách/reviewer, hạn và phạm vi demo, review PR harness. Chưa ghi ai IN_PROGRESS nếu họ chưa nhận việc.
- V03/F02/F04/F06/F08/F10/I04/E03 cần bằng chứng người dùng: code/firmware/config/model version, điều kiện, video và log có timestamp/job ID, kết quả mong đợi/thực tế, số lần đạt/lỗi. Chỉ DONE-HW khi đáp ứng acceptance đã duyệt.

## Câu hỏi mở

- **Q1 (H06/S01):** Category nào vào A/B? HOLD giữ sách ở đâu và ai giải phóng? STOP có cần thao tác reset/home nào? Xác nhận bảng xử lý QR/ID/AI lỗi; ví dụ nguồn dùng STOP_FAULT/GOOD khác STOP/PASS của DECISIONS. Hai nhánh A/B + HOLD đã có D05, không hỏi lại số nhánh.
- **Q2 (H03/S05/F01):** Model/IO/nguồn/tải, cơ cấu/hành trình và feedback thực tế, kết nối PC–ESP32 là gì? esp32dev+Arduino hiện chỉ scaffold, chưa chứng minh thiết bị.
- **Q3 (H11/R02):** Hạn demo và phạm vi cần trình diễn là gì, hay hiện chưa có hạn? Không tự đặt ngày.
- **Q4 (H07/A03/E01–E04):** Mục tiêu, cỡ mẫu và điều kiện chấp nhận của từng KPI? Các cách đo trong ROADMAP là đề xuất, chờ tôi xác nhận khi chưa có nguồn duyệt.
- **Q5 (H10/H02/R03):** Ai phụ trách từng module, ai review PR ngoài tác giả? CONTRIBUTING yêu cầu reviewer nhưng chưa nêu người.
- **Q6 (H08/A02):** Máy train OS/GPU/VRAM/tài nguyên và quyền sử dụng? Chưa có máy được xác minh.
- **Q7 (H09/B02):** Danh mục sách lấy ở đâu, schema/copy_id/category và quy tắc cập nhật? Cần mẫu được phép dùng, không tự tạo dữ liệu thật.
- **Q8 (H04/H05/V01/V06/A01):** Bộ ảnh B08/pilot nào được phép dùng hồi quy nội bộ, mép chuẩn và ví dụ nhãn rách/bẩn/ca biên nào được duyệt? Phạm vi hiện có A6 theo README; chưa đề nghị đổi cỡ sách.
- **Q9 (H12/V04):** PENDING/DECODE_ERROR giữ nội bộ collector và map ra enum chuẩn, hay bổ sung hợp đồng? Chưa tự chọn phương án.

HMI đã có câu trả lời: HTML/CSS/JS, qua backend/adapter; giữ hướng dẫn AGENTS local và roadmap Bước 11. D04 đã chọn FastAPI/SQLite/YOLO11n làm hướng ban đầu. Không mở lại những lựa chọn này chỉ vì module chưa được viết.

## Quyết định chờ

H06: bảng route/reason và semantics HOLD/STOP (D05/D09/D10 + ví dụ Bước 9 local). H07: mục tiêu/cỡ mẫu/KPI (PLAN phần nghiệm thu). H03: board/IO/giao tiếp (DECISIONS phần cần xác minh và issue #3). H05: quy tắc nhãn (D06/D11 và issue #4). H12: enum QR (D16 + CODEBASE_MAP C1). Chỉ sau phản hồi mới ghi quyết định chính thức vào DECISIONS trong task được phép; phiên H01 giữ nguyên file đó.

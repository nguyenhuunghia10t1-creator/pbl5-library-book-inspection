Active task: NONE
Last updated: 2026-11-07
Branch: fix/cover-color-background
Last green commit: 6a0e1bbb2421b250297cfe6081cc53607ccc80fe

## Resume notes

Đọc TASKS → đuôi SESSION_LOG → COLOR_BACKGROUND_VALIDATION/COVER_CAPTURE và DECISIONS liên quan. Chỉ TASKS giữ tiến độ; không tự chuyển task IN_PROGRESS khi phiên đã bàn giao.

Nhánh V07 `fix/cover-color-background` từ V02 `8f9198f0c78030dd21000f4562a0492556c1dce2`. PR nền [#6](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6) base chore/codex-harness và [#5](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5) base main còn OPEN khi xác minh GitHub. PR V07 sẽ mở base fix/preview-v02 sau kiểm cuối và push; URL được bổ sung trong commit metadata. Không merge. Main và sửa có sẵn trong checkout chính giữ nguyên.

GitHub đồng thời có [PR #7 V05](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/7) và [PR #8 bìa sáng/UI](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/8) từ fork team, cùng base V02. Không chứa mã của hai PR này trong nhánh hiện tại, không tuyên bố đã test chúng. Review #8 vì chồng lấn detector/UI và hồ sơ V07; không merge cả hai bản mà chưa đối chiếu. Không thực hiện lặp V05.

Task CODEX kế tiếp đề xuất **B01** (SQLite/schema/migration với DB tạm): độc lập H04/H03, phụ thuộc H01 đã có bằng chứng. Không bắt đầu trong phiên V07. Đầu phiên sau xác minh lại PR/main mới nhất, baseline và ledger trên đúng nhánh; nếu các PR nền còn mở, có thể tạo nhánh B01 từ origin/fix/cover-color-background và PR base cùng nhánh đó, ghi quan hệ xếp tầng.

```powershell
git status --short --branch
git fetch origin
git switch -c feature/sqlite-schema-b01 origin/fix/cover-color-background
& $PYTHON scripts/check_repository.py
& $PYTHON scripts/check_codex_state.py
& $PYTHON -m unittest discover -s tests -v
```

Xác định `$PYTHON` là interpreter venv của checkout thực tế, không giả định worktree có .venv riêng. Chỉ sau baseline/chọn B01 mới đổi TASKS và Active task. Nếu reviewer yêu cầu sửa V07 thì tiếp tục phạm vi V07 trước.

## Baseline đã đo

V07 bắt đầu từ commit sạch 8f9198f, 2026-11-07T11:12:05–11:12:13+07:00: checker PASS (26 source), 71 tests PASS/0 failures/errors/skips trong 6.459s. Lượt source trước commit ghi HEAD + working-tree changes, kết quả cuối tham chiếu SESSION_LOG phiên 6; không coi là kiểm nguyên trạng HEAD.

Last green phía trên vẫn là commit V02 đã kiểm sạch 6a0e1bb (SESSION_LOG phiên 4: checker/validator, 71 tests, diff PASS). Chỉ nâng sang commit V07 sau khi commit tồn tại và kiểm sạch; không tạo vòng hash tự tham chiếu.

Môi trường E1: Windows 11/PowerShell 5.1, Python venv 3.14.3, OpenCV 5.0.0, NumPy 2.5.3, không thêm dependency. Benchmark geometry xử lý OpenCV thật trên synthetic, benchmark UI scheduling fake và ba GUI synthetic được ghi riêng trong [báo cáo V07](../COLOR_BACKGROUND_VALIDATION.md). Webcam mới/ESP32/AI/KPI hardware NOT_RUN. H04/V01/V03 không hoàn thành bằng synthetic; mục tiêu thực tế là “đề xuất, chờ tôi xác nhận”.

## Human actions pending

- **Ưu tiên thử V07 ngay:** theo [bài thử bìa sáng/tối](../COVER_CAPTURE.md#thử-bìa-sángtối-v07-trên-webcam): bìa sáng và tối A6, nền sáng/tối/hoa văn; C thử auto rồi B trên nền trống, lấy sách ra kiểm khung biến mất. Gửi video Live/Analyzed, camera/backend/resolution/commit, runtime.log, raw/cover/debug/metadata ngoài Git. Chưa có raw lỗi sáng mới; dữ liệu này hỗ trợ H04/V01, không tự hoàn tất V03 khi gate chưa duyệt.
- **Review phương án song song:** PR team #8 cũng sửa V07/UI từ V02; chưa tích hợp vào nhánh phiên này. Người review đối chiếu detector/UI và chọn cách tích hợp, không tự merge/đóng PR người khác. V05 có PR #7 riêng nên tránh thực hiện lại; trạng thái trên nhánh này chưa được nâng theo PR chưa audit lại.

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

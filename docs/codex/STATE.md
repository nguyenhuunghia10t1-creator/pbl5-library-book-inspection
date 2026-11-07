Active task: NONE
Last updated: 2026-11-07
Branch: feature/capture-bundle-audit-v05
Last green commit: 11d635d29f1bdab111f710b2279e1b8bf176ca4a

## Resume notes

Đọc TASKS → đuôi SESSION_LOG → CAPTURE_AUDIT và quyết định liên quan. Chỉ TASKS giữ trạng thái; ký hiệu trước tên việc giúp đọc nhanh.

Phiên V05 dùng worktree sạch, nhánh feature/capture-bundle-audit-v05 từ origin/fix/preview-v02 tại 8f9198f. PR nền [#6](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6) đã xác minh OPEN/chưa merge, base chore/codex-harness; PR harness [#5](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5) cũng OPEN/chưa merge. Tài khoản hiện tại không có quyền push kho gốc; V05 đã push lên [nhánh fork](https://github.com/truongthinh994/pbl5-library-book-inspection/tree/feature/capture-bundle-audit-v05) và mở [PR #7](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/7) về base fix/preview-v02 của kho nhóm. PR #7 xác minh OPEN/chưa merge. Checkout cũ và cấu hình DroidCam sửa sẵn được giữ nguyên, không đưa vào commit này.

Phạm vi đã nhận: V05 kiểm bundle/manifest/hash/provenance và thống kê pilot theo cuốn bằng fixture. Metadata là nguồn chính; báo cáo tách bundle lỗi, lỗi manifest và staging chưa hoàn tất. Audit chỉ đọc, giữ raw/crop/debug/metadata/session/manifest nguyên trạng. Kiểm source chỉ đối chiếu khai báo, không chứng nhận nguồn thật, danh tính DB, crop đúng hoặc nhãn lỗi. Không thêm dependency và không đổi writer/schema, camera, geometry, QR hay firmware.

V05 đã đạt acceptance phần mềm; xem [hướng dẫn audit](../CAPTURE_AUDIT.md) và SESSION_LOG phiên 6. B01 là một việc tiếp theo được đề xuất (Depends H01 DONE), chưa bắt đầu. Phiên sau kiểm worktree/PR/base thật trước khi tạo nhánh riêng rồi chạy baseline:

```powershell
& $PYTHON scripts/check_repository.py
& $PYTHON scripts/check_codex_state.py
& $PYTHON -m unittest discover -s tests -v
git diff --check
```

Đã chạy baseline sạch rồi mới làm V05; commit triển khai 11d635d đã được kiểm sạch với 92 tests PASS và xác minh SHA trên fork. PR #7 xếp tầng đã mở, không merge; B01 chưa bắt đầu. Team có thể tải [ZIP đúng nhánh V05](https://github.com/truongthinh994/pbl5-library-book-inspection/archive/refs/heads/feature/capture-bundle-audit-v05.zip); không lấy main để thử phần này. CI remote chưa có check được báo ở PR khi truy vấn lúc 10:14:17+07:00, chưa kết luận PASS.

## Baseline đã đo

Last green commit 11d635d29f1bdab111f710b2279e1b8bf176ca4a đã kiểm nguyên trạng lúc 2026-11-07T10:13:16–10:13:27+07:00, git status sạch trước/sau: checker PASS (29 source), validator PASS, unittest discovery PASS 92 tests/0 failures/0 errors/0 skips (9.492s), git diff --check PASS. Commit metadata tiếp theo chỉ ghi bằng chứng/URL, không tự tham chiếu SHA của chính nó.

V05 trên HEAD 8f9198f + working-tree changes lúc 2026-11-07T10:11:07–10:11:18+07:00: checker PASS (29 source), validator PASS, unittest discovery PASS 92 tests/0 failures/0 errors/0 skips (9.211s), git diff --check PASS. Các test dùng fixture synthetic và DB/collection tạm, không có bằng chứng camera/pilot thật mới.

Baseline V05 trên commit sạch 8f9198f lúc 2026-11-07T09:57:25–09:57:35+07:00: checker PASS (26 source), validator PASS, unittest discovery PASS 71 tests/0 failures/0 errors/0 skips (8.500s), git diff --check PASS. Môi trường phiên này: Windows 11 build 26300, Python 3.13.14, OpenCV 5.0.0, NumPy 2.5.4; dùng venv đã có của checkout cũ, không cài dependency.

Lịch sử V02: commit 6a0e1bbb2421b250297cfe6081cc53607ccc80fe đã kiểm nguyên trạng lúc 2026-11-07T09:43:51–09:44:03+07:00: checker PASS (26 source), validator PASS, 71 tests PASS/0 failures/0 errors/0 skips trong 11.165s, git diff --check PASS. Commit metadata chỉ bổ sung URL/bằng chứng; không tự tham chiếu hash của chính nó.

Baseline gốc V02 4d3b402 có checker và 54 tests PASS trên cây sạch. Lượt source trước commit lúc 09:41:08–09:41:20+07:00 ghi HEAD + working-tree changes, 71 tests PASS trong 10.961s. Xem SESSION_LOG để phân biệt từng lượt.

Môi trường E1 Windows 11/PowerShell 5.1, Python venv 3.14.3, OpenCV 5.0.0, NumPy 2.5.3; không thêm dependency. GUI thật với ảnh synthetic và benchmark scheduling PASS; webcam/thiết bị thật NOT_RUN. Chi tiết [PREVIEW_VALIDATION](../PREVIEW_VALIDATION.md) và [SESSION_LOG](../SESSION_LOG.md).

## Human actions pending

- **Thử riêng V02, có thể làm ngay:** chạy webcam ở nhánh này theo [COVER_CAPTURE](../COVER_CAPTURE.md#thử-nhanh-preview-v02-trên-webcam). Gửi video thấy Live/Analyzed, thao tác S/D/Q, runtime.log và một bundle ngoài Git; ghi camera/backend/resolution. Đây là kiểm hành vi preview/lưu/thoát, không thay gate đầy đủ V03 và không tự đổi trạng thái nghiệm thu hardware.

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

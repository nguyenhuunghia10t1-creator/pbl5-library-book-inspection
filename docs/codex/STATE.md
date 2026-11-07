Active task: NONE
Last updated: 2026-11-07
Branch: fix/preview-v02
Last green commit: 6a0e1bbb2421b250297cfe6081cc53607ccc80fe

## Resume notes

Đọc TASKS → đuôi SESSION_LOG → COVER_CAPTURE/PREVIEW_VALIDATION và quyết định liên quan. Chỉ TASKS giữ trạng thái; ký hiệu trước tên việc giúp đọc nhanh.

Nhánh fix/preview-v02 từ commit gốc 4d3b402 của chore/codex-harness. PR nền [#5](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5) vẫn mở, chưa merge; PR V02 [#6](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6) OPEN, base chore/codex-harness, chưa merge; cần người review ngoài tác giả. Checkout chính main và các sửa có sẵn vẫn giữ nguyên. Worktree đang mở chính là nhánh V02.

Task CODEX kế tiếp đề xuất **V05**, kiểm bundle/manifest/hash/provenance; H01 có bằng chứng, chưa cần dữ liệu thật. Không bắt đầu trong phiên V02. V01 còn chờ H04. Nếu PR V02 chưa merge, phiên tiếp theo có thể tạo nhánh feature/capture-bundle-audit-v05 từ origin/fix/preview-v02 và PR base fix/preview-v02, ghi PR nền. Sau khi các PR nền merge thì xác minh main mới và chọn base phù hợp; không tự merge.

Lệnh bắt đầu ở phiên tiếp theo, sau khi kiểm working tree/PR:

```powershell
git status --short --branch
git fetch origin
git switch -c feature/capture-bundle-audit-v05 origin/fix/preview-v02
& $PYTHON scripts/check_repository.py
& $PYTHON scripts/check_codex_state.py
& $PYTHON -m unittest discover -s tests -v
```

Chỉ sau baseline và chọn V05 mới đổi TASKS/Active task; không tự chuyển task trong phiên hiện tại.

## Baseline đã đo

Last green commit là 6a0e1bbb2421b250297cfe6081cc53607ccc80fe đã kiểm nguyên trạng lúc 2026-11-07T09:43:51–09:44:03+07:00: checker PASS (26 source), validator PASS, 71 tests PASS/0 failures/0 errors/0 skips trong 11.165s, git diff --check PASS. Commit metadata chỉ bổ sung URL/bằng chứng; không tự tham chiếu hash của chính nó.

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

Active task: NONE
Last updated: 2026-11-07
Branch: fix/light-cover-detection-v07
Last green commit: 6c4619af1bb5aea64487174a1b6f402772b51231

## Resume notes

Đọc TASKS → đuôi SESSION_LOG → COVER_CAPTURE/PREVIEW_VALIDATION và quyết định liên quan. Chỉ TASKS giữ trạng thái; ký hiệu trước tên việc giúp đọc nhanh.

Nhánh fix/light-cover-detection-v07 từ origin/fix/preview-v02 tại 8f9198f. PR nền [#6](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6) OPEN/chưa merge, base chore/codex-harness; #5 cũng chưa merge. V07 có PR riêng base fix/preview-v02, không trộn code audit V05. Nhánh V05 vẫn được giữ ở 525ca41 và [PR #7](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/7) trên fork; không xóa dữ liệu camera cục bộ, không sửa config DroidCam ở checkout cũ. Baseline nhánh V07 là 71 tests vì chưa chứa 21 test audit của PR #7.

V07 đạt acceptance phần mềm theo yêu cầu sửa nhận bìa vàng nhạt/xanh nhạt. Người dùng xác nhận chưa bấm B với nền trống. Bổ sung biên ba kênh BGR với ngưỡng theo gradient/nhiễu, giữ mask nền Lab và biên xám cũ, vẫn lọc tứ giác/diện tích/tỉ lệ và bảo vệ chạm biên/nhiều bìa/quality/QR. Không thay parser, schema, crop 630×888, YOLO hoặc firmware. Fixture không tạo viền đen giả khi warp. V01 vẫn chờ mẫu thật H04; không suy test tổng hợp thành nghiệm thu camera V03. Chi tiết [LIGHT_COVER_VALIDATION](../LIGHT_COVER_VALIDATION.md).

Lệnh kiểm lại trong phiên này:

```powershell
git status --short --branch
& $PYTHON scripts/check_repository.py
& $PYTHON scripts/check_codex_state.py
& $PYTHON -m unittest discover -s tests -v
```

V07 đã commit/push lên [nhánh fork](https://github.com/truongthinh994/pbl5-library-book-inspection/tree/fix/light-cover-detection-v07), mở [PR #8](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/8) về fix/preview-v02; xác minh OPEN/chưa merge và head đúng commit triển khai. Team tải [ZIP đúng nhánh V07](https://github.com/truongthinh994/pbl5-library-book-inspection/archive/refs/heads/fix/light-cover-detection-v07.zip). B01 chỉ đề xuất, chưa bắt đầu. Preview bản mới đã được mở với camera 1/MSMF; tại lần quan sát ảnh đầu vào đen dù Live/Analyzed tăng, chưa thử được mép bìa thật. Chờ người dùng mở DroidCam/cung cấp nguồn hình rõ và thử B với nền trống. CI remote chưa có check trong statusCheckRollup khi xác minh; chưa kết luận PASS.

## Baseline đã đo

Last green commit 6c4619af1bb5aea64487174a1b6f402772b51231 đã được kiểm nguyên trạng, status sạch trước/sau, lúc 2026-11-07T11:06:54–11:07:06+07:00: checker PASS (27 source), validator PASS, unittest PASS 85 tests/0 failures/0 errors/0 skips (9.926s), git diff --check PASS. Commit metadata tiếp theo chỉ ghi URL/bằng chứng, không tự tham chiếu hash của chính nó.

V07 source trên HEAD 8f9198f + working-tree changes, 2026-11-07T11:02:30–11:02:40+07:00: checker PASS (27 source), validator PASS, 85 tests = 71 baseline + 14 mới PASS/0 failures/0 errors/0 skips (8.816s), git diff --check PASS. GUI và headless synthetic vàng nhạt PASS/READY/PBL5-B04 lúc 11:04:07–11:04:11+07:00. Kiểm camera chỉ xác nhận mở backend, không chứng minh bìa thật đạt gate.

Phiên V07, Windows 11 build 26300/PowerShell 7.6.9, Python 3.13.14/OpenCV 5.0.0/NumPy 2.5.4, venv checkout cũ: commit sạch 8f9198f lúc 2026-11-07T10:55:40–10:55:47+07:00, checker PASS (26 source), validator PASS, 71 tests PASS/0 failures/0 errors/0 skips (6.342s), git diff --check PASS. Trước đổi nhánh, 525ca41 cũng đã baseline 92 tests PASS. Xem SESSION_LOG phiên 7 để phân biệt.

Lịch sử V02: commit 6a0e1bbb2421b250297cfe6081cc53607ccc80fe đã kiểm nguyên trạng lúc 2026-11-07T09:43:51–09:44:03+07:00: checker PASS (26 source), validator PASS, 71 tests PASS/0 failures/0 errors/0 skips trong 11.165s, git diff --check PASS. Commit metadata chỉ bổ sung URL/bằng chứng; không tự tham chiếu hash của chính nó.

Baseline gốc V02 4d3b402 có checker và 54 tests PASS trên cây sạch. Lượt source trước commit lúc 09:41:08–09:41:20+07:00 ghi HEAD + working-tree changes, 71 tests PASS trong 10.961s. Xem SESSION_LOG để phân biệt từng lượt.

Môi trường E1 Windows 11/PowerShell 5.1, Python venv 3.14.3, OpenCV 5.0.0, NumPy 2.5.3; không thêm dependency. GUI thật với ảnh synthetic và benchmark scheduling PASS; webcam/thiết bị thật NOT_RUN. Chi tiết [PREVIEW_VALIDATION](../PREVIEW_VALIDATION.md) và [SESSION_LOG](../SESSION_LOG.md).

## Human actions pending

- **Thử bìa sáng V07:** mở DroidCam và giữ màn hình điện thoại sáng khi preview đen. Camera cố định, đưa sách ra khỏi khung, bấm B lúc bàn trống; thử vàng nhạt/xanh nhạt/trắng và kiểm mép ngoài/crop/QR. Gửi ví dụ lỗi/đúng qua nguồn riêng ngoài Git để bổ sung H04; không tự đổi V01/V03/V06 chỉ từ fixture hoặc backend mở được.

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

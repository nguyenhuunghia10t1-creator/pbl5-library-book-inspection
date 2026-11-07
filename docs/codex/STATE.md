Active task: NONE
Last updated: 2026-11-07
Branch: fix/light-cover-detection-v07
Last green commit: e3f3846e4ff32e7f063f49725ac0b53d74c5c7ef

## Resume notes

Đọc TASKS → đuôi SESSION_LOG → LIGHT_COVER_VALIDATION/COVER_CAPTURE và DECISIONS liên quan. TASKS là nguồn trạng thái duy nhất.

V07 hoàn thành phần mềm theo phiên 7–8, cùng nhánh fix/light-cover-detection-v07 và [PR #8](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/8) OPEN/chưa merge, base fix/preview-v02. Phiên 7 bổ sung biên màu BGR cho bìa sáng. Phiên 8 xử lý phản hồi khung xanh nhấp nháy: ba ô LIVE/DETECTED/RECTIFIED giữ đúng nguồn, không ghép góc cũ lên live; manual/frozen/MASK giữ vùng xem lớn. B bỏ qua key-repeat liên tục và từ chối khi kết quả phân tích gần nhất thấy QR sách hợp lệ, nhưng không tự chứng minh bàn trống nếu chưa đọc được QR.

Đã xem ảnh nền B cục bộ có cả bìa vàng, thấy B lặp nhiều lần; detector trên một ảnh đó vẫn tìm được mép/QR. Người dùng xác nhận camera chưa cố định và phần nhấp nháy là khung bên trái. Không đổi thêm detector hoặc giữ kết quả quá hạn để che lỗi UI. Phiên camera mới đã mở, chưa tự hiệu chuẩn B; người dùng cần bố trí nền thật trống và camera cố định. Kết quả một ảnh/fixture không thay V01/H04 hoặc nghiệm thu V03/V06.

PR nền #6 (fix/preview-v02 → chore/codex-harness) và #5 chưa merge khi kiểm. V05 vẫn ở nhánh feature/capture-bundle-audit-v05/PR #7 riêng, mã audit không nằm trong V07. Checkout cũ/cấu hình DroidCam và mọi dữ liệu runtime được giữ nguyên. Không force-push hoặc merge.

Team lấy [nhánh V07](https://github.com/truongthinh994/pbl5-library-book-inspection/tree/fix/light-cover-detection-v07) hoặc [ZIP đúng nhánh](https://github.com/truongthinh994/pbl5-library-book-inspection/archive/refs/heads/fix/light-cover-detection-v07.zip). Tài khoản hiện tại push qua fork, origin vẫn là kho nhóm. Cập nhật PR #8 theo phạm vi cuối, không tự bắt đầu B01; B01 chỉ là task CODEX tiếp theo được đề xuất khi mở phiên mới và xác minh base.

## Baseline đã đo

Last green commit e3f3846e4ff32e7f063f49725ac0b53d74c5c7ef đã kiểm sạch lúc 2026-11-07T11:12:04–11:12:14+07:00: checker PASS (27 source), unittest PASS 85 tests/0 failures/0 errors/0 skips (8.987s), git diff --check PASS.

Follow-up phiên 8 trên HEAD e3f3846 + working-tree changes lúc 2026-11-07T11:24:19–11:24:29+07:00: checker PASS (27 source), validator PASS, unittest PASS 89 tests/0 failures/0 errors/0 skips (8.681s), git diff --check PASS. Module async-preview có 21 tests PASS, 4 test mới và một test nguồn ảnh được cập nhật. Đã xem render tổng hợp hai frame khác màu và GUI ba ô trên phiên camera mới; ảnh live khi quan sát đen, không có phép thử live đủ điều kiện với camera cố định.

Môi trường E2: Windows 11 build 26300, PowerShell 7.6.9, Python 3.13.14/OpenCV 5.0.0/NumPy 2.5.4, venv checkout cũ, không thêm dependency. Lịch sử baseline/source/commit sạch của V02 và V07 nằm trong SESSION_LOG; không suy PASS hardware hoặc CI remote từ test local.

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

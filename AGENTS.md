# PBL5 Library Book Inspection

Giao tiếp tiếng Việt ngắn, rõ. Chỉ dẫn hiện tại của người dùng ưu tiên hơn hồ sơ. Khi học: giải thích ngắn → ví dụ → tự làm → kiểm tra → sửa → áp dụng; một bài mỗi lần, giữ bài gốc. Hỏi tiến độ không hủy bài đang học.

## Đầu phiên

- Đọc [STATE](docs/codex/STATE.md), [TASKS](docs/codex/TASKS.md), đuôi [SESSION_LOG](docs/SESSION_LOG.md) và [DECISIONS](docs/DECISIONS.md) liên quan; xem README, PROGRESS, CODEBASE_MAP và mốc M01–M27 trong [PLAN](docs/PLAN.md) khi cần.
- Xác minh checkout, remote, branch, HEAD, working tree và interpreter; chạy baseline theo [WORKFLOW](docs/codex/WORKFLOW.md). Đối chiếu code, không coi dự định là chức năng đã có.
- Không reset/stash/xóa thay đổi có sẵn hoặc gom chúng vào commit. Dùng worktree sạch khi cần; không làm trực tiếp trên main.

## Làm một task

- TASKS là nguồn tiến độ duy nhất; STATE là điểm tiếp tục. Chọn một task CODEX đủ đầu vào, Depends đã hoàn thành, dùng nhánh phù hợp task. Tối đa một CODEX IN_PROGRESS.
- Chỉ sửa trong phạm vi task; ý tưởng mới vào backlog. Nếu cần người thật, đặt task bị ảnh hưởng BLOCKED, ghi yêu cầu vào Human actions pending, chọn CODEX đủ điều kiện khác; không nhảy bài đang chờ người dùng thực hành.
- DONE: acceptance không đòi simulator/phần cứng đã đủ. DONE-SIM: hành vi đạt trên simulator. DONE-HW: người dùng cung cấp bằng chứng thiết bị thật đáp ứng acceptance. Mọi trạng thái hoàn thành cần Evidence và Depends hoàn thành.
- Phân biệt cú pháp/import, unit/integration, simulator, webcam, phần cứng. Kết quả lệnh dùng PASS/FAIL/SKIPPED/NOT_RUN; chưa đo ghi N/A và lý do. Không coi script/build/ACK là nghiệm thu thiết bị.

## Ràng buộc kỹ thuật

Theo [ARCHITECTURE](docs/ARCHITECTURE.md) và DECISIONS:

- D04/D06: OpenCV/QR, SQLite, YOLO11n, FastAPI; lỗi cover_tear, surface_stain. D18: tách module; AI/HMI không gọi GPIO.
- D05/D07/D09/D10: A/B/HOLD, một sách/job UUID; giữ UNCONFIRMED khi thiếu xác nhận; tách simulation/hardware và expected_route/actual_route, không suy actual_route từ lệnh.
- D11/D17: raw bất biến, chia dataset theo cuốn/thiết kế bìa; crop mặc định 630×888, giữ raw/crop/debug/metadata. D16: PBL5-B + 2–6 chữ số hoặc LIB1:copy_id; QR hợp lệ cú pháp chưa phải danh tính DB.
- HMI HTML/CSS/JS; ControllerTransport đổi adapter simulator/serial bằng config (hướng dẫn dự án đã có). Trạng thái QR/identity/quality/route/job theo DECISIONS; chưa inference thì quality null.
- Pin map, nguồn/tải, hành trình, feedback, firmware và ngưỡng chưa đủ căn cứ phải thành câu hỏi; mục tiêu mới ghi “đề xuất, chờ tôi xác nhận”. Fake phải đánh dấu.

## Cuối phiên

Hoàn tất mỗi task đã được kiểm tra thì commit, push nhánh và mở/cập nhật PR ngay trong phiên, không chờ người dùng nhắc. Bàn giao link nhánh mới nhất và link tải ZIP để team tải đúng bản; nếu push bị chặn phải báo rõ commit/nhánh đang có. Giữ quy tắc không merge.

Chạy kiểm tra; cập nhật TASKS, STATE, thêm SESSION_LOG (giữ lịch sử); commit đúng file, push nhánh, mở/cập nhật PR, không merge (D19). Không tự bắt đầu task kế tiếp. Bàn giao kết quả, giới hạn, câu hỏi và một việc tiếp theo; xem WORKFLOW để phục hồi phiên đứt/PR chưa merge. Chỉ đọc/lập kế hoạch thì bàn giao trong chat.

Cấm commit dữ liệu thật, weights, credentials; force-push; bịa bằng chứng phần cứng; vượt phạm vi; thêm dependency nặng khi chưa có DECISION phù hợp. Không sửa bộ nhớ/cấu hình toàn cục để lưu tiến độ.

# Quy trình tiếp tục dự án

## Vai trò hồ sơ

| File | Vai trò |
|---|---|
| [TASKS.md](TASKS.md) | Nguồn sự thật duy nhất về tiến độ task, Depends, acceptance và evidence |
| [STATE.md](STATE.md) | Điểm tiếp tục: task CODEX thực sự đang làm, nhánh, kiểm tra gần nhất, đầu vào/câu hỏi còn chờ |
| [ROADMAP.md](ROADMAP.md) | Phase, phụ thuộc, ba luồng và gate; không sao chép Status task |
| [CODEBASE_MAP.md](CODEBASE_MAP.md) | Inventory đã đọc, luồng code thực tế, thiếu hụt và mâu thuẫn |
| [DECISIONS.md](../DECISIONS.md) | Quyết định đã được xác nhận; câu hỏi chưa trả lời nằm ở STATE |
| [SESSION_LOG.md](../SESSION_LOG.md) | Lịch sử append-only và bằng chứng lệnh/kiểm tra/PR |
| [PLAN.md](../PLAN.md) | Nguồn mốc M01–M27 để đối chiếu, không dùng số heading thay mã mốc |
| [PROGRESS.md](../../PROGRESS.md) | Hồ sơ cũ và đường dẫn tới bộ quản lý hiện tại; không duy trì Status task thứ hai |

Chỉ dẫn hiện tại của người dùng ưu tiên hơn quy ước repo. Đường dẫn dự kiến trong kế hoạch không chứng minh file đã tồn tại. Bản roadmap nguồn cục bộ nếu có là tài liệu tham khảo bất biến; clone sạch không cần file bị ignore đó để tiếp tục. Không sửa bộ nhớ hoặc cấu hình Codex toàn cục.

## Vòng đời một phiên

1. Đọc STATE, bảng Tasks, các mục cuối SESSION_LOG, quyết định và code liên quan. Nêu ngắn task hiện tại, điều đã xác minh và việc sẽ làm. Xem README/CONTRIBUTING khi setup hoặc quy trình thay đổi.
2. Xác minh bằng `git rev-parse --show-toplevel`, `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git status --short`; đọc diff có sẵn. Ghi commit gốc, OS, shell, Python/interpreter/venv thực tế. Thiếu Git là giới hạn quản lý phiên, không tự coi là lỗi ứng dụng.
3. Chạy baseline hiện hành ở README, ít nhất checker và unittest bên dưới. Tách lỗi đã có khỏi lỗi do task. Không làm việc nghiệp vụ chỉ để ép baseline xanh.
4. Chọn một task CODEX đủ đầu vào và Depends hoàn thành trong TASKS; chọn nhánh phù hợp, tạo bằng `git switch -c <nhanh-task>` trước khi sửa. Nhánh đã có thì kiểm tra lịch sử và tiếp tục, không ghi đè. Nhánh harness chỉ dành cho việc thiết lập này, không bắt phiên tương lai dùng nó.
5. Đặt task đó IN_PROGRESS và Active task tương ứng, giữ tối đa một task CODEX IN_PROGRESS. Triển khai đúng acceptance, giữ bài học gốc nếu ngoài phạm vi. Khi người dùng đang học, chỉ giao một bài; câu hỏi tiến độ không hủy bài.
6. Chạy kiểm tra phù hợp thay đổi; đối chiếu diff với phạm vi. Ý tưởng phát sinh được ghi thành task nhỏ trong bảng/backlog để làm sau, không tiện tay triển khai.
7. Cập nhật TASKS/STATE/SESSION_LOG trước lượt kiểm tra cuối. Task kế tiếp chỉ nằm trong Resume notes, không tự đặt IN_PROGRESS. Nếu task dở do phiên đứt, giữ dấu vết công việc thực tế và ghi rõ điểm tiếp tục.
8. Stage file cụ thể; xem staged diff, commit, push nhánh và mở hoặc cập nhật PR đúng head/base. Không merge hoặc force-push. Báo URL/commit chỉ khi Git/GitHub xác nhận. PR nêu kết quả thực, giới hạn, baseline đỏ nếu có, câu hỏi và task kế tiếp.
9. Nếu URL PR chỉ có sau commit, thêm commit metadata cùng nhánh; chạy lại validator và `git diff --check`, push. Nếu metadata làm thay đổi link hoặc quy tắc, chạy checker tương ứng. Hết phiên bàn giao một task kế tiếp; không tự chạy nền, mở phiên mới hoặc tiếp tục ngoài yêu cầu.

Đối với phiên chỉ đọc/lập kế hoạch, báo điểm tiếp tục trong chat, không ghi/commit trái chế độ.

## Kiểm tra và ghi bằng chứng

Dùng interpreter đã xác minh. Ví dụ PowerShell khi có venv tại root:

```powershell
$python = (Resolve-Path '.venv/Scripts/python.exe').Path
& $python scripts/check_repository.py
& $python scripts/check_codex_state.py
& $python -m unittest discover -s tests -v
git diff --check
```

Worktree sạch có thể dùng đường dẫn tuyệt đối tới interpreter/venv đã xác minh của checkout gốc; ghi đúng đường dẫn trong log cục bộ nếu cần, tránh công bố đường dẫn riêng trong PR. Không giả định `python` trên PATH là venv. Chỉ cài dependency đã được repo khai báo khi được phép; không sửa manifest để vượt baseline. Nếu OS khác Windows, ghi lệnh README gốc và lệnh chuyển đổi thực chạy, không báo đã kiểm chứng Windows.

Với mỗi lệnh, SESSION_LOG ghi ngày/phiên hoặc timestamp có múi giờ, OS/shell/interpreter, commit hoặc `HEAD + working-tree changes`, lệnh chính xác, exit code, PASS/FAIL/SKIPPED/NOT_RUN, số test/failure/skip và tóm tắt. Unittest discovery phải tìm được test; zero test không là nghiệm thu. Chưa đo ghi N/A kèm lý do. Khi FAIL, phân biệt nguyên nhân đã biết với giả thuyết và ghi đúng một kiểm tra/sửa tiếp theo.

`check_repository.py` giữ kiểm tra cũ và gọi validator mới; không gọi ngược để tránh vòng lặp. Validator chỉ kiểm tra cấu trúc/tính nhất quán, không xác thực nội dung Evidence hoặc thiết bị thật. Tests validator dùng fixture tạm, không sửa tiến độ thật để tạo lỗi. CI hiện gọi checker và unittest trên Windows; cấu hình workflow tồn tại chưa phải bằng chứng run CI xanh. Check camera, firmware và các bộ kiểm thử khác chỉ chạy khi task cần và đủ điều kiện; ghi riêng mức bằng chứng.

## TASKS và STATE phải nhất quán

Một bảng chuẩn dưới “Tasks”, đúng bảy cột `ID, Task, Who, Depends, Acceptance, Status, Evidence`; không có ký tự pipe bên trong ô. ID ổn định theo prefix H/V/B/A/S/F/I/E/R và hai chữ số, không dùng mã quyết định. Depends là `-` hoặc ID phân cách dấu phẩy, không tự phụ thuộc/chu trình. Who thuộc CODEX, USER-HW, USER-DATA, DECISION, REVIEW.

- TODO: chưa bắt đầu và chưa có trở ngại đầu vào thiết yếu.
- IN_PROGRESS: thực sự đang làm; người thật chỉ dùng sau khi xác nhận họ đang làm.
- BLOCKED: thiếu đầu vào thiết yếu, ghi đang chờ gì và task/người phụ trách; không chặn task độc lập.
- DONE: acceptance không cần chứng minh simulator/phần cứng đã đạt.
- DONE-SIM: hành vi đạt acceptance trên simulator.
- DONE-HW: người dùng cung cấp bằng chứng thiết bị thật đủ acceptance; build, ACK hay simulator không thay thế.

Mọi trạng thái hoàn thành cần Evidence cụ thể, không rỗng/placeholder, và tất cả Depends hoàn thành. Tách task simulator và task hardware nếu cần nghiệm thu riêng. Không dùng DONE để tránh gate hardware. Kết quả kiểm tra PASS/FAIL/SKIPPED/NOT_RUN không phải Status task.

STATE bắt đầu bằng đúng bốn trường: Active task, Last updated, Branch, Last green commit. Active task khớp task CODEX IN_PROGRESS duy nhất; không có thì NONE. Ngày là ngày lịch thực tế YYYY-MM-DD theo múi giờ làm việc. Branch phản ánh nhánh thực, không phải nhánh mong muốn.

Last green commit chỉ là SHA đã tồn tại, được chạy thành công bộ kiểm tra chỉ rõ, tại trạng thái commit đó. Nếu chỉ kiểm tra cây có thay đổi, log ghi `HEAD + working-tree changes`; không gán PASS đó cho HEAD nguyên trạng. Không đủ bằng chứng thì UNKNOWN. Có thể giữ SHA xanh cũ có bằng chứng; không tạo vòng lặp ghi SHA của chính commit đang soạn.

## Phục hồi và chọn nhánh

- **Working tree bẩn:** đọc diff/index/untracked, xác định thay đổi người dùng. Không reset, stash, xóa hoặc commit thay họ. Nếu không thể tách an toàn, tạo worktree sạch từ commit đã xác minh ở vị trí được phép; ghi checkout gốc và worktree làm việc trong điểm bàn giao. Không copy dữ liệu/credentials.
- **PR nền chưa merge:** kiểm tra head/base và trạng thái PR. Nếu chỉ sửa chính task, tiếp tục nhánh/PR đó. Task độc lập nên từ main đã xác minh; task cần code trên PR nền có thể tạo nhánh con/PR phụ thuộc, ghi PR nền và base thật trong Resume notes/PR. Không trộn thay đổi nền thành PR vào main khi chưa giải thích; không tự merge để mở đường.
- **Phiên đứt:** đối chiếu Git, file thực, log và PR; STATE là chỉ dẫn, không chứng minh mọi thay đổi đã được lưu. Khôi phục đúng task trước khi bắt đầu task khác; cập nhật hồ sơ sai lệch bằng chứng.
- **Baseline đỏ:** ghi lỗi gốc, ảnh hưởng và task xử lý nhỏ. Chỉ sửa trong phạm vi được giao; task độc lập vẫn tiếp tục nếu kiểm chứng được. Không báo toàn repo xanh khi còn lỗi, và không nâng task vượt acceptance.
- **Push/PR bị chặn:** hoàn tất local được phép, ghi lệnh/exit/lý do, branch/commit có thật và nội dung PR sẵn bàn giao. Không nói đã push hoặc có PR khi chưa được xác nhận; không merge.
- **AGENTS bị ignore khi bootstrap:** quy tắc ignore cũ không bị sửa trong phiên thiết lập; stage có chủ đích bằng `git add -f AGENTS.md`. Sau khi được theo dõi, các sửa đổi AGENTS được Git phát hiện bình thường.

## Người thật, quyết định và phạm vi

Human actions pending tham chiếu ID task, yêu cầu cụ thể, định dạng bằng chứng (ảnh/video/log, ngày, cấu hình/phiên bản, số lần thử và kết quả), task được mở khóa. Không đưa dữ liệu thật vào Git; dẫn manifest/checksum hoặc tóm tắt đã loại thông tin riêng tới kho riêng phù hợp.

Thiếu hardware/dataset/model/feedback thì ghi đúng thiếu gì, đặt task liên quan BLOCKED và chuyển sang CODEX đủ điều kiện khác; không tự đánh người thật IN_PROGRESS. Nếu người dùng đang thực hành bài hiện tại, giữ bài đó và chờ kết quả, không tự giao bài mới.

Câu hỏi Q1… nằm ở STATE với task ảnh hưởng. Chỉ hỏi phần nguồn chưa giải đáp hoặc mâu thuẫn; không hỏi lại HMI HTML/CSS/JS hay kiến trúc đã chốt. Ý nghĩa route, pin/nguồn/tải/hành trình/feedback, firmware framework, mục tiêu định lượng thiếu căn cứ không được tự chốt. Ngưỡng mới ghi “đề xuất, chờ tôi xác nhận”. Khi được xác nhận và phạm vi task cho phép, ghi quyết định, lý do/ảnh hưởng/nguồn vào DECISIONS; cập nhật kế hoạch nếu phụ thuộc đổi. Fake ghi rõ mục đích test, không đại diện chất lượng AI/thực tế.

Mỗi task CODEX nên tạo một đầu ra nhỏ cho một PR tập trung. Người thật/quyết định/review có thể hoàn thành bằng phản hồi hoặc bằng chứng, không cần ép một PR riêng. Không tạo công cụ quản lý ngoài repo hay gửi thông báo người khác ngoài hành động Git/PR đã được cho phép.

## Mẫu mục SESSION_LOG

```text
## YYYY-MM-DD — phiên N — <task ID>
- Branch; commit gốc; checkout/working tree ban đầu; PR nền nếu có.
- Môi trường: OS; shell; Python/interpreter/venv.
- Thay đổi: file và đầu ra; phần chủ đích giữ ngoài phạm vi.
- Lệnh: thời điểm; commit hoặc HEAD + working-tree changes; lệnh chính xác;
  exit code; PASS/FAIL/SKIPPED/NOT_RUN; tests/failures/skips; kết quả.
- Chưa kiểm chứng: lý do, mức bằng chứng còn thiếu.
- Blocker/câu hỏi: ID task, Qn, đầu vào cần người thật.
- Commit/PR: giá trị đã tồn tại/được xác nhận; không ghi SHA tự tham chiếu.
- Điểm tiếp tục: một ID CODEX, lý do đủ điều kiện, lệnh bắt đầu.
```

Giữ nguyên lịch sử, thêm mục mới cuối file. Mọi sửa hồ sơ phải giữ nguồn tiến độ duy nhất; ROADMAP/STATE/PROGRESS chỉ tham chiếu TASKS và bằng chứng phù hợp.

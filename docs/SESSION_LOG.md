# Nhật ký kỹ thuật

## 2026-10-29 — Cơ sở mã nguồn cho nhóm

- Tổ chức core OpenCV, desktop UI, firmware, test và ví dụ theo module.
- Giữ nguyên nội dung năm bài thực hành và mã firmware mẫu.
- Chuẩn hóa điểm chạy module và launcher độc lập thư mục làm việc.
- Bổ sung tài liệu sử dụng, quy trình đóng góp và kiểm tra tự động.
- 22 test Python, 23 test mô phỏng Windows và build firmware đạt ở môi trường phát triển.

## 2026-10-29 — Kiểm tra bìa B08

Camera DirectShow nhận ảnh 1280×720. Trong 12 khung, 5 khung đọc được PBL5-B08; 7 khung chọn vùng chạm biên nên không chạy QR. Chưa đạt ổn định READY.

Ảnh chẩn đoán cho thấy bộ chọn góc chuyển giữa mép giấy, mép hình in và đường ron nền. Cần sửa lựa chọn tứ giác trước khi thu dữ liệu hàng loạt. Ảnh và metadata thử nghiệm lưu cục bộ, không nằm trong repository.

## 2026-10-29 — Xuất bản repository nhóm

- Khởi tạo repository public pbl5-library-book-inspection với lịch sử main riêng.
- Chuẩn hóa tài liệu kỹ thuật, mẫu issue và pull request; dữ liệu và hồ sơ cục bộ không nằm trong mã công khai.
- Kiểm tra lại 22 test trên snapshot xuất bản; workflow GitHub Actions đạt.
- Main yêu cầu PR, một approval và kiểm tra python; chặn force-push và xóa nhánh.
- Mở bốn issue cho hình học bìa, preview, IO ESP32 và pilot dữ liệu.


## 2026-11-07 — Phiên 2 — H01: Audit và thiết lập Codex harness

- Commit gốc: d431f10fbb79dc086c8912702552463ca20262ab. Origin: https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection.git; remote main cùng SHA theo git ls-remote. Legacy-origin không dùng. Branch mới chore/codex-harness được tạo bằng git switch -c sau khi tạo worktree sạch detached tại commit gốc.
- Preflight checkout chính main có PROGRESS.md và docs/SESSION_LOG.md sửa sẵn từ phiên trước; giữ nguyên, không stash/reset/stage/copy vào worktree. Nhánh harness dùng worktree riêng, không thay lịch sử main. AGENTS local đã đọc và cập nhật có chọn lọc vào worktree; .gitignore không đổi, stage AGENTS có chủ đích bằng git add -f.
- Inventory: git ls-files có 64 tệp baseline, đã đọc đầy đủ source/tests/scripts/config/CI và tài liệu; danh sách trong CODEBASE_MAP. Không audit .venv/.pio/vendor/generated/data thật/weights. Đọc 4 issue mở đầy đủ body; từng comments endpoint không có bình luận; pagination per_page=100 page=1 trả 4 issues và 0 pulls, các endpoint không có trang kế. Thời điểm GitHub audit 2026-11-07T08:53:36+07:00. Không tạo/sửa/đóng issues.
- Môi trường E1: Windows-11-10.0.26200-SP0; Windows PowerShell 5.1.26100.9711 Desktop; Python 3.14.3 AMD64 trong venv của checkout chính; OpenCV 5.0.0, NumPy 2.5.3. Worktree dùng interpreter đã có, không cài dependency. Biến lệnh $py = 'D:/smart-vision-inspection/.venv/Scripts/python.exe'. Cwd mọi lệnh kiểm dưới đây là root worktree chore/codex-harness, không phải checkout chính đang bẩn.
- Lệnh README gốc: `& '.\.venv\Scripts\python.exe' scripts/check_repository.py`; `& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v`; `pio run --project-dir firmware/esp32`. Lệnh thực chỉ đổi đường dẫn interpreter/PlatformIO để dùng môi trường sẵn có; vẫn Windows, không chuyển sang Linux.

### Baseline trước thay đổi

| Thời điểm +07:00 | Môi trường/cây nguồn | Lệnh thực chạy | Exit | Kết quả | Tests/failure/error/skip |
|---|---|---|---|---|---|
| 2026-11-07 08:53:10–08:53:15 | E1, d431f10 sạch tracked/untracked trước sửa | `& $py scripts/check_repository.py` | 0 | PASS: 21 nguồn Python, links, workspace | N/A: kiểm tĩnh |
| 2026-11-07 08:53:10–08:53:15 | E1, d431f10 sạch trước sửa | `& $py -m unittest discover -s tests -v` | 0 | PASS; discovery có 22 tests, 4.101s | 22/0/0/0 |
| 2026-11-07 08:53:56–08:54:29 | E1, source firmware d431f10; HEAD + working-tree changes chỉ harness đang được soạn | `& C:/Users/nguye/.platformio/penv/Scripts/platformio.exe run --project-dir firmware/esp32` | 0 | PASS build esp32dev, 29.79s; warning unused variable result có sẵn | N/A: build không phải hardware test |
| 2026-11-07 08:53:56–08:54:29 | E1, source policy d431f10; HEAD + working-tree changes chỉ harness | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/camera-priority/Test-CameraPriority.ps1` | 0 | PASS SIMULATION; không ghi PnP/task/ACL thật | 23/0/0/0 |

- Không có lỗi baseline repository. Build warning main.cpp biến result chưa dùng có sẵn, ngoài phạm vi nên không sửa.
- Diagnostic môi trường trước baseline: thử ZoneInfo('Asia/Ho_Chi_Minh') exit 1 do Windows venv không có tzdata; đây là lỗi lệnh chẩn đoán, không phải lỗi project. Đã dùng DateTimeOffset UTC+07 để ghi thời gian thực; không cài package. Lệnh exec sandbox ban đầu lỗi khởi tạo trong phiên trước nên phiên này dùng execution được phép cho read/test/write theo phạm vi.
- Webcam/UI tương tác thiết bị, upload, cơ cấu, AI/model thật và end-to-end hardware: NOT_RUN; không có thiết bị/dataset/model được nghiệm thu trong worktree, phiên này chỉ harness. Chỉ số chất lượng thực: N/A. CI PR mới chưa chạy ở thời điểm baseline.

### Thay đổi và điểm tiếp tục

- Tạo CODEBASE_MAP/ROADMAP/TASKS/STATE/WORKFLOW; TASKS là nguồn Status duy nhất với 53 task và mapping M01–M27/issues. Câu hỏi Q1–Q9 giữ ở STATE, không tự chốt route/IO/KPI/nhãn.
- Tạo validator standard library và 32 fixture unittest; checker cũ chỉ thêm lời gọi validator, giữ các kiểm tra cũ và CI hiện có. Validator không xác minh tính thật của evidence hoặc phần cứng.
- AGENTS dưới 5 KB, dùng nhánh phù hợp từng task tương lai, không cấm sửa nghiệp vụ vĩnh viễn. PROGRESS chỉ thêm chỉ dẫn/liên kết; SESSION_LOG chỉ nối mục mới. Không sửa code nghiệp vụ, manifest, PLAN/ARCHITECTURE/DECISIONS/README/CONTRIBUTING.
- Sai khác: enum QR PENDING/DECODE_ERROR ngoài danh sách DECISIONS (H12/V04); ví dụ policy local STOP_FAULT/GOOD khác enum quyết định (H06); issue #2 còn nhắc sleep 150 ms nhưng source hiện không có sleep đó; PROGRESS cũ và AGENTS ignored cần dẫn sang harness. Chi tiết CODEBASE_MAP.
- Hành động người thật ưu tiên H04/H05 (mẫu/nhãn) và H03 (board/IO/feedback); phân công reviewer/hạn demo chưa có. Không ghi người thật IN_PROGRESS khi chưa nhận việc.
- Task kế tiếp đề xuất V02, độc lập mẫu thật còn chờ H04. Chỉ bắt đầu ở phiên sau bằng nhánh fix/preview-v02 đúng base PR, baseline và đổi active task theo WORKFLOW. Không triển khai V02 trong phiên này.
- Commit/PR: chưa tạo tại thời điểm ghi phần này; sẽ nối bằng chứng sau khi có kết quả thực.


### Kiểm tra harness trước commit — 2026-11-07T09:02:16–09:02:22+07:00

Môi trường E1; cây nguồn d431f10 + working-tree changes (harness), không gán các kết quả này cho HEAD nguyên trạng. Các lệnh thực chạy với `D:/smart-vision-inspection/.venv/Scripts/python.exe`:

- `scripts/check_repository.py`: exit 0, PASS; 23 nguồn Python, links/workspace và cấu trúc task/state.
- `scripts/check_codex_state.py`: exit 0, PASS; chỉ cấu trúc/nhất quán, không xác minh nội dung evidence/hardware.
- `-m unittest discover -s tests -v`: exit 0, PASS; 54 tests = 22 cũ + 32 mới, 4.937s, failures=0, errors=0, skips=0. Discovery đã tìm đủ hai nhóm.
- `git diff --check`: exit 0, PASS. Cảnh báo Git chuyển CRLF sang LF của file sửa không phải lỗi whitespace; không format hàng loạt.
- Review phạm vi: chỉ 11 đường dẫn allowlist; PROGRESS/SESSION_LOG bảo toàn byte nội dung commit gốc và chỉ append; không đổi vision/software/firmware/config/CI/dependency hoặc file cấm. AGENTS 3,725 byte UTF-8, dưới 5 KB.
- Baseline còn lỗi: không có lỗi test repository; warning firmware cũ đã ghi riêng. Chưa kiểm chứng webcam, AI/model, PnP thật, cơ cấu, end-to-end hardware và CI remote của PR mới.


### Commit sạch, push và PR — 2026-11-07T09:04:54+07:00

- Commit triển khai đã tồn tại: 37d98d2031996b424c8441633617ddd49223b061, chore/codex-harness. Kiểm lại nguyên trạng khi git status sạch, E1, 2026-11-07T09:03:20–09:03:25+07:00: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/check_repository.py` exit 0 PASS (23 source); cùng interpreter `scripts/check_codex_state.py` exit 0 PASS; `-m unittest discover -s tests -v` exit 0 PASS 54 tests/0 failures/0 errors/0 skips, 4.515s; `git diff --check` exit 0 PASS.
- `git push -u origin chore/codex-harness`: exit 0; `git ls-remote origin refs/heads/chore/codex-harness refs/heads/main`: exit 0, nhánh harness đúng 37d98d2, main vẫn d431f10. Không force-push, không merge.
- GitHub REST GET pulls theo head/base rồi POST pulls: thành công, [PR #5](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5) OPEN, head chore/codex-harness, base main, merged=false. Không có PR trùng và không sửa issue. Nội dung PR có scope, test, baseline warning/giới hạn, câu hỏi Q1–Q9 và V02 kế tiếp.
- Metadata: H01 có bằng chứng DONE; Active task NONE; Last green commit trỏ 37d98d2 đã kiểm sạch; PR được thêm vào Resume notes. Không ghi hash của chính commit metadata. H02 vẫn chờ người review; V02 chỉ đề xuất, chưa bắt đầu.
- CI remote của PR tại thời điểm ghi: NOT_RUN bởi phiên này; kết quả workflow đang chờ truy vấn. Không gán PASS CI từ test local. Phần cứng/model/camera vẫn NOT_RUN.

- Kiểm metadata sau PR lúc 2026-11-07T09:04:54+07:00, E1, 37d98d2 + working-tree changes: cùng interpreter chạy scripts/check_repository.py (23 source) và scripts/check_codex_state.py đều exit 0 PASS; git diff --check exit 0 PASS. Đây là thay đổi tài liệu; không đổi mã từ bộ 54 tests đã chạy trên commit sạch. Chạy lại checker/validator trước commit metadata để kiểm liên kết và ledger cuối.


## 2026-11-07 — Phiên 3 — H13: Ký hiệu tiến độ dễ đọc

- Yêu cầu: thêm đánh dấu để người dùng dễ thấy task đã làm/chưa làm. Nhánh chore/codex-harness, commit gốc 5347e171d7666f09639fae70610028349cd8c866; worktree sạch. PR #5 đã kiểm vẫn OPEN, chưa merge, đúng head SHA.
- Môi trường E1 như phiên 2: Windows/PowerShell, interpreter D:/smart-vision-inspection/.venv/Scripts/python.exe. Baseline commit sạch lúc 2026-11-07T09:18:33–09:18:38+07:00: chạy scripts/check_repository.py exit 0 PASS (23 source, gồm validator); -m unittest discover -s tests -q exit 0 PASS, 54 tests/0 failures/0 errors/0 skips trong 4.422s.
- Thay đổi lúc 2026-11-07T09:19:27+07:00: TASKS có chú giải và icon trong tên task; giữ đủ bảy cột, ID/Who/Depends/Status không đổi. Thêm H13 cho yêu cầu tài liệu này; phân biệt DONE/DONE-SIM/DONE-HW. WORKFLOW nhắc cập nhật icon cùng Status; STATE dẫn cách đọc nhanh.
- Không đổi code, dependency hoặc trạng thái nghiệm thu nghiệp vụ. Icon BLOCKED là đang chờ đầu vào, không phải FAIL. Không có kiểm chứng phần cứng mới; V02 vẫn là việc nghiệp vụ tiếp theo, chưa bắt đầu.

- Kiểm sau sửa lúc 2026-11-07T09:19:27+07:00, E1, HEAD 5347e17 + working-tree changes: cùng interpreter chạy scripts/check_repository.py và scripts/check_codex_state.py đều exit 0 PASS; git diff --check exit 0 PASS. Đối chiếu từng hàng: 53 task cũ chỉ thêm icon, các cột còn lại giữ nguyên; H13 là task tài liệu mới. Mọi icon khớp Status. Không thêm test mới cho thay đổi trình bày.
- Kết thúc H13 theo bằng chứng trên; Active task NONE, Last green commit giữ hash đã được kiểm nguyên trạng. V02 vẫn chưa bắt đầu. Tiếp tục push cùng PR #5 đang mở, không merge.

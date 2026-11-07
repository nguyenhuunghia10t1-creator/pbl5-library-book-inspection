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


## 2026-11-07 — Phiên 4 — V02: Preview độc lập geometry/QR

- Bắt đầu 2026-11-07T09:32:43+07:00; nhánh fix/preview-v02 từ origin/chore/codex-harness tại 4d3b402a843f6240ccd31fbbc8e27ed8be658dd4. PR nền #5 OPEN/chưa merge được kiểm bằng API; nhánh tạo trước sửa file, không đổi main hay thay đổi có sẵn ở checkout gốc.
- Chọn V02 vì H01 DONE và không cần mẫu thật/IO/ngưỡng chưa duyệt. Phạm vi: worker phân tích, UI/capture liên kết frame, test/benchmark synthetic và tài liệu liên quan; không sửa geometry/parser/bundle schema hay firmware.
- Baseline E1 Windows/PowerShell, interpreter D:/smart-vision-inspection/.venv/Scripts/python.exe, worktree sạch tại commit gốc. 2026-11-07T09:30:57–09:31:02+07:00: scripts/check_repository.py exit 0 PASS (23 source); -m unittest discover -s tests -v exit 0 PASS 54 tests/0 failures/0 errors/0 skips, 5.035s.
- Mô hình triển khai: chỉ một worker sở hữu CoverVision, không hàng đợi frame cũ; UI đọc camera/render/event riêng. Kết quả chứa frame/properties/config revision để không ghép crop/QR cũ vào ảnh mới; S/D đợi frame sau yêu cầu. Đổi camera/calibration/flip/manual vô hiệu hóa kết quả cũ.
- Chưa chạy webcam hoặc thiết bị thật. Kết quả fixture không là nghiệm thu V03.

- Hồi quy lần đầu sau sửa: 69 tests được tìm; 68 PASS, test cũ AppTests.test_save_uses_frame_after_keypress FAIL vì giả định S ở vòng 1 và Q ở vòng 2 đã lưu xong. Đây là lỗi tương thích test do V02, không có ở baseline. Một việc sửa tiếp theo đã thực hiện: test đợi bundle hoàn tất trước Q, vẫn bắt buộc capture_seq > frame lúc bấm S; bổ sung test mới so raw/crop/QR/properties cùng frame.

- Sau sửa test S, chạy toàn bộ unittest exit 0 PASS 69 tests/0 failures/errors/skips trong 5.713s lúc 09:38:11–09:38:17+07:00. Hai test bổ sung calibration/config và D làm tổng cuối 71 tests.
- Benchmark lúc 2026-11-07T09:38:17–09:38:21+07:00, E1, HEAD 4d3b402 + working-tree changes: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/benchmark_preview.py` exit 0 PASS. Delay analysis synthetic 200ms; 15 preview frames; trước UI 3.1701s/median gap 211.040ms, sau UI 0.2111s/median gap 10.774ms. Renderer/camera/analysis fake: không dùng làm FPS/accuracy thật. Giá trị đầy đủ trong PREVIEW_VALIDATION.
- GUI smoke cuối lúc 2026-11-07T09:40:32–09:40:35+07:00: cùng interpreter `-m vision.opencv --image $env:TEMP/pbl5-v02-smoke-20261107/fixture.png --source-kind synthetic --output $env:TEMP/pbl5-v02-smoke-20261107/collection --duration 2 --screenshot $env:TEMP/pbl5-v02-smoke-20261107/ui.png`, exit 0 PASS; đã xem ảnh ui.png: READY, crop/QR PBL5-B04, nhãn Frame/Analyzed rõ. Sửa nhãn frame chồng ảnh trước lượt cuối. Không webcam.
- Bộ kiểm cuối source lúc 2026-11-07T09:41:08–09:41:20+07:00, E1, HEAD + working-tree changes: scripts/check_repository.py exit 0 PASS (26 source); scripts/check_codex_state.py exit 0 PASS; -m unittest discover -s tests -q exit 0 PASS 71 tests/0 failures/0 errors/0 skips, 10.961s; git diff --check exit 0 PASS. Lệnh dùng interpreter E1 đã ghi; không sửa dependency/vision pipeline/schema/firmware.
- Ghi V02 DONE theo acceptance phần mềm và bằng chứng PREVIEW_VALIDATION; Active task NONE. Đây không là DONE-HW hay PASS camera thật. Đã thêm bài thử webcam cụ thể vào COVER_CAPTURE và Human actions pending; không tự chốt ngưỡng.
- Việc tiếp theo duy nhất: V05 kiểm bundle/manifest/provenance bằng fixtures; không bắt đầu trong phiên này. PR V02 sẽ mở base chore/codex-harness vì PR nền #5 chưa merge.


### Commit, push, PR và bàn giao — 2026-11-07T09:45:28+07:00

- Commit triển khai 6a0e1bbb2421b250297cfe6081cc53607ccc80fe. Kiểm nguyên trạng khi git status sạch, E1, 2026-11-07T09:43:51–09:44:03+07:00: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/check_repository.py` exit 0 PASS (26 source), cùng interpreter `scripts/check_codex_state.py` exit 0 PASS, `-m unittest discover -s tests -q` exit 0 PASS 71 tests/0 failures/0 errors/0 skips, 11.165s; `git diff --check` exit 0 PASS.
- `git push -u origin fix/preview-v02`: exit 0; `git ls-remote origin refs/heads/fix/preview-v02 refs/heads/chore/codex-harness refs/heads/main`: exit 0, V02 đúng 6a0e1bb, harness vẫn 4d3b402, main vẫn d431f10. Không force-push/merge.
- GitHub REST GET pulls theo head rồi POST pulls: thành công, [PR #6](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6) OPEN, head fix/preview-v02, base chore/codex-harness. PR xếp tầng phụ thuộc #5; không đóng issue #2 vì nghiệm thu camera còn ở V03.
- Cập nhật metadata URL và Last green commit sang 6a0e1bb đã được kiểm sạch; không ghi hash tự tham chiếu của commit metadata. V02 DONE phần mềm theo TASKS; Active task NONE; V05 là việc CODEX kế tiếp, chưa bắt đầu.
- CI remote sẽ kiểm sau push metadata; không suy PASS từ test local. Webcam thật vẫn NOT_RUN. Người dùng thử theo COVER_CAPTURE và gửi video/runtime.log/bundle ngoài Git, không cần quyết định phần cứng mới cho bài smoke V02.

- Kiểm metadata lúc 2026-11-07T09:45:28+07:00, E1, HEAD 6a0e1bb + working-tree changes chỉ tài liệu: scripts/check_repository.py và scripts/check_codex_state.py cùng interpreter E1 đều exit 0 PASS, git diff --check exit 0 PASS. Toàn bộ 14 đường dẫn thuộc V02; không có ảnh/log runtime/dữ liệu thật được stage. Chỉ dẫn webcam và V05 đã có trong STATE, không còn CODEX IN_PROGRESS.


## 2026-11-07 — Phiên 5 — Đồng bộ bàn giao V02 cho team

- Yêu cầu người dùng: hoàn tất task nào thì kiểm tra/commit/push ngay và đưa bản mới để team tải. Xác minh worktree sạch trên fix/preview-v02 tại 9cde7af99149d989b9939ac6f66e8ab4dffa6da1; remote đã có cùng SHA. Không có code V02 bị bỏ lại local.
- Baseline E1 Windows/PowerShell, interpreter D:/smart-vision-inspection/.venv/Scripts/python.exe, commit sạch 9cde7af, 2026-11-07T09:49:40–09:49:47+07:00: scripts/check_repository.py exit 0 PASS (26 source và validator); -m unittest discover -s tests -q exit 0 PASS 71 tests/0 failures/0 errors/0 skips trong 5.797s.
- Bổ sung quy ước đã được người dùng xác nhận vào AGENTS và WORKFLOW: push ngay sau mỗi task được kiểm, mở/cập nhật PR, xác minh remote và cung cấp link nhánh/ZIP; không merge. Không sửa code hoặc trạng thái nghiệp vụ; Active task NONE, V05 chưa bắt đầu.
- Bản team cần lấy là nhánh fix/preview-v02 (gồm kế hoạch/harness và V02), không phải main hoặc bản chỉ có kế hoạch. PR #6 vẫn là PR của phần V02; có thể tải archive ZIP của đúng nhánh khi không dùng Git.


## 2026-11-07 — Phiên 7 — V07: Bìa sáng ít tương phản

- Người dùng yêu cầu sửa code OpenCV bỏ sót bìa vàng nhạt/xanh nhạt; trả lời chưa hiệu chuẩn B với bàn trống. Đã đọc AGENTS/STATE/TASKS, WORKFLOW/DECISIONS và detector/tests. Tách V07 chỉ xử lý tín hiệu biên yếu bằng fixture; V01 vẫn chờ H04, không đánh DONE-HW V03. Không bắt đầu B01 hoặc YOLO.
- Môi trường E2: Windows-11-10.0.26300-SP0, PowerShell 7.6.9; `$PYTHON=E:/smart-vision-inspection/.venv/Scripts/python.exe`, Python 3.13.14/OpenCV 5.0.0/NumPy 2.5.4, `PYTHONDONTWRITEBYTECODE=1`. Không cài dependency. Cấu hình DroidCam checkout cũ và dữ liệu camera cục bộ giữ nguyên.
- Checkout đầu sạch ở 525ca4188cc9a4f1e1fc2590030133ad67ec6978, feature/capture-bundle-audit-v05; baseline 2026-11-07T10:52:58–10:53:08+07:00: `& $PYTHON scripts/check_repository.py` exit 0 PASS (29 sources); validator exit 0 PASS; `& $PYTHON -m unittest discover -s tests -q` exit 0 PASS 92 tests/0 failures/0 errors/0 skips (9.253s); git diff --check exit 0 PASS. PR #7 xác minh OPEN/chưa merge trên fork, head 525ca41; PR #6 OPEN tại 8f9198f, base chore/codex-harness.
- Chọn nhánh độc lập `git switch -c fix/light-cover-detection-v07 origin/fix/preview-v02` trước sửa, dùng lại worktree sạch; nhánh V05/PR #7 vẫn giữ. PR V07 sẽ base fix/preview-v02, chỉ geometry/fixture/tài liệu, không kéo toàn bộ audit vào PR này. TASKS ghi V05 DONE bằng bằng chứng PR #7 ở nhánh riêng, không ngụ ý audit đã nằm trong checkout V07.
- Baseline thật của V07 tại commit sạch 8f9198f0c78030dd21000f4562a0492556c1dce2, 2026-11-07T10:55:40–10:55:47+07:00: `& $PYTHON scripts/check_repository.py` exit 0 PASS (26 sources); `& $PYTHON scripts/check_codex_state.py` exit 0 PASS; `& $PYTHON -m unittest discover -s tests -q` exit 0 PASS 71 tests/0 failures/0 errors/0 skips (6.342s); `git diff --check` exit 0 PASS.
- Tái hiện trước sửa: thêm test_light_covers.py, `& $PYTHON -m unittest tests.opencv.test_light_covers -q` exit 1 FAIL, 11 tests/27 failure hoặc subtest/0 errors/0 skips, 1.733s. Fixture bìa không có viền đen, khác nền ít hơn default mask và có màu cùng grayscale; warp dùng BORDER_REPLICATE để không tạo biên đen giả. Lỗi là tín hiệu grayscale yếu/không còn sắc độ; chưa hiệu chuẩn góp phần nhưng hiệu chuẩn cũng không khắc phục được mọi fixture yếu dưới default 22.
- Thiết kế: giữ mask Lab và Canny xám cũ, bổ sung biên theo từng kênh BGR đã làm mượt, ngưỡng theo median gradient và sàn nhiễu. Dùng chung lọc tứ giác/diện tích/tỉ lệ và nhiều bìa/chạm khung; không sửa quality gate/QR parser/raw/crop/schema/firmware. Không thêm tham số nghiệm thu hoặc dependency.
- Lượt đầu dùng Lab edges, 2026-11-07T10:58:20+07:00: cùng lệnh targeted exit 1 FAIL, 11 tests/1 subtest failure/0 errors/skips, 1.834s; xanh nhạt + nhiễu 1.2 bị đứt viền. Đo gradient kênh b ở mép p10/50/90=8/14/18, contour kín lớn nhất 69.5 px² so với thật 80,543 px². Tăng closing 3→5 trong thử nghiệm không sửa được; không đưa thay đổi đó vào code. Cùng thuật toán trên BGR cho contour 81,419 px²: dùng BGR trực tiếp tránh lượng tử hóa Lab ở biên yếu, vẫn giữ Lab cho mask nền.
- Targeted sau sửa BGR lúc 2026-11-07T11:00:03+07:00: exit 0 PASS 11 tests/0 failures/errors/skips (2.014s). Bổ sung nền có vân, nhiễu mạnh và vật không tứ giác; lượt cuối 2026-11-07T11:00:56+07:00: `& $PYTHON -m unittest tests.opencv.test_light_covers -q` exit 0 PASS 14 tests/0 failures/0 errors/0 skips (2.102s). Các lượt source đều là HEAD 8f9198f + working-tree changes, không gán PASS cho HEAD nguyên trạng.
- Tài liệu LIGHT_COVER_VALIDATION nêu thuật toán, fixture, giới hạn và bài thử B với nền trống; COVER_CAPTURE dẫn cách dùng với bìa sáng. Code/test không chứa ảnh thật, model, runtime log hay config riêng. Camera đang phát khung đen khi quan sát nên chưa có ảnh bìa sáng thật phù hợp để so mép trước/sau; không kết luận đã đạt trên mọi sách thật.
- Kiểm toàn bộ, commit/push/PR sẽ nối dưới đây sau khi có kết quả. Giữ Last green commit là 8f9198f đã kiểm sạch. B01 chỉ đề xuất cho phiên sau, không tự bắt đầu; các đầu vào người thật giữ nguyên.

- Hồi quy toàn bộ source lúc 2026-11-07T11:02:30–11:02:40+07:00, E2, HEAD 8f9198f + working-tree changes: `& $PYTHON scripts/check_repository.py` exit 0 PASS (27 source); `& $PYTHON scripts/check_codex_state.py` exit 0 PASS; `& $PYTHON -m unittest discover -s tests -q` exit 0 PASS, 85 tests = 71 cũ + 14 mới, failures/errors/skips=0 (8.816s); `git diff --check` exit 0 PASS. Warning synthetic decode failure là test hồi phục lỗi đã có, không là lỗi chưa sửa.
- GUI/headless synthetic lúc 2026-11-07T11:04:07–11:04:11+07:00: `& $PYTHON -m vision.opencv --image data/opencv/light-cover-validation/yellow-synthetic.png --source-kind synthetic --output data/opencv/light-cover-validation/gui-collection --duration 2 --screenshot data/opencv/light-cover-validation/gui.png` exit 0 PASS, đã xem hình bốn góc/crop/READY/PBL5-B04. Cùng interpreter `-m vision.opencv --image data/opencv/light-cover-validation/yellow-synthetic.png --headless` exit 0 PASS, vision_status READY, qr VALID_FORMAT, copy_id PBL5-B04. Fixture/UI/runtime dưới data bị ignore, không stage.
- Khởi động lại camera bằng interpreter pythonw cùng venv, `-m vision.opencv --camera 1 --backend msmf --source-kind real --output data/opencv/light-cover-camera-20261107`; runtime log lúc 11:04:39+07:00 xác nhận mở backend, driver báo 1280×720/30fps, không đo FPS/latency thật. Quan sát Live #719/Analyzed #717 nhưng ảnh đen; chưa có bằng chứng mép bìa sáng thật đúng. Đã hỏi người dùng tình trạng nguồn DroidCam; task V07 chỉ DONE phần mềm, V01/V03/V06 và gate người thật không đổi.
- TASKS/STATE cập nhật V07 DONE theo 14 test mới/85 test hồi quy và tài liệu, Active task NONE; B01 chưa bắt đầu. Phiên này chỉ stage 7 file code/test/tài liệu liên quan V07, tiếp tục commit/push/PR sau bộ kiểm hồ sơ.

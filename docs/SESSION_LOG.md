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


## 2026-11-07 — Phiên 6 — V07: Bìa sáng/tối và nhiều nền

- Bắt đầu 2026-11-07T11:15:16+07:00; người dùng duyệt kế hoạch tối ưu app PBL5 mới, chế độ tự động + B hỗ trợ. Chưa có raw/video lỗi bìa sáng mới, người dùng sẽ test thực tế sau; không sửa bài học gốc, không yêu cầu model/dependency.
- Branch fix/cover-color-background tạo từ origin/fix/preview-v02, SHA gốc 8f9198f0c78030dd21000f4562a0492556c1dce2, worktree sạch; main và sửa có sẵn ở checkout gốc giữ nguyên. H04/V01/V03 giữ yêu cầu bằng chứng riêng.
- Baseline E1 Windows/PowerShell, interpreter D:/smart-vision-inspection/.venv/Scripts/python.exe, commit sạch 8f9198f, 2026-11-07T11:12:05–11:12:13+07:00: scripts/check_repository.py exit 0 PASS (26 source), -m unittest discover -s tests -q exit 0 PASS 71 tests/0 failures/0 errors/0 skips, 6.459s.
- Phạm vi V07: candidate geometry Lab/cạnh thích nghi, background B bù ánh sáng, điểm bốn cạnh và dải trong/ngoài, quality theo chi tiết/clipping; metrics/issues bổ sung, giữ API và schema bundle. Mặc định xử lý mới cần pilot, không là ngưỡng nghiệm thu hardware đã duyệt.

### Triển khai và hồi quy V07

- Tách geometry/quality thành module nhỏ và ghép qua CoverVision, giữ import helper cũ/chữ ký detect/process; QR/camera/worker/storage/schema không thay đổi. Thêm ngưỡng default Config có validation; JSON cũ được giữ nguyên để kiểm tương thích. UI thêm detail focus/clipping và lý do FOCUS_UNVERIFIED; không thêm dependency hoặc firmware.
- Kết quả FAIL giữa phiên là lỗi V07 đang phát triển, không là baseline đỏ: lượt test_cover_capture có 2 failures (hai QR bị crop khác; inset border được chọn khi bìa chạm biên). Sửa ưu tiên ứng viên gần nhau và kiểm foreground hai bên. Lượt màu đầu có 4 subcase failures (bìa gần trắng/viền in/bìa trơn); sửa đề xuất hull cho cạnh yếu chưa khép kín, vẫn kiểm đủ bốn cạnh. Khi bổ sung ca giấy trùng màu nền có viền in, phát hiện vẫn chọn khung in; thêm tương phản dải gần/xa và hồi quy NO_COVER. Không sửa test cũ hoặc nới giới hạn góc <10px để ép xanh.
- 2026-11-07T11:23:32+07:00, E1, HEAD 8f9198f + working-tree changes: cùng interpreter `-m unittest discover -s tests -q`, exit 0 PASS 84 tests/0 failures/0 errors/0 skips, 12.942s. Sau đó thêm các ca nền trống auto, đổi nền/hiệu chuẩn, giấy trùng nền có viền và pixel crop ground truth.
- 2026-11-07T11:30:44–11:31:34+07:00, E1, HEAD + working-tree changes: `-m unittest tests.opencv.test_color_background tests.opencv.test_cover_capture.GeometryTests -q`, exit 0 PASS 26 tests/0 failures/0 errors/0 skips, 17.924s; geometry benchmark exit 0 PASS 50/50 so 35/50 baseline, trước sửa fixture antialias. Các con số hiệu năng trung gian không thay số đo cuối.
- 2026-11-07T11:30:07–11:30:11+07:00: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/benchmark_preview.py --baseline-ref 4d3b402 --frames 15 --delay 0.2`, exit 0 PASS; 15/15 preview duy nhất, median gap 211.276→10.806ms, analysis delay fake 200ms. Chỉ đo scheduling, không FPS/QR thật.
- 2026-11-07T11:33:49–11:34:18+07:00, E1, HEAD + working-tree changes: `scripts/check_repository.py` exit 0 PASS (31 Python source); `scripts/check_codex_state.py` exit 0 PASS; `-m unittest discover -s tests -q` exit 0 PASS 88 tests/0 failures/0 errors/0 skips, 27.814s; `git diff --check` exit 0 PASS. Tất cả script Python dùng `& D:/smart-vision-inspection/.venv/Scripts/python.exe`; chưa phải bằng chứng commit sạch.
- Rà fixture thấy warp nội suy với nền đen có thể tạo cạnh giả: đổi sang BORDER_REPLICATE và alpha coverage để trộn với nền, không làm ca gần màu dễ hơn do viền giả. Chạy lại `-m unittest tests.opencv.test_color_background -q` exit 0 PASS 17 tests/0 failures/0 errors/0 skips, 10.238s. Số đo cuối dùng fixture đã sửa, được ghi bên dưới. Fixtures có seed và ground truth, không dùng dữ liệu/weights thật.
- GitHub REST GET open pulls và body/files PR #7/#8 đã xác minh: #7 (V05) và #8 (một phương án V07/hiển thị) là nhánh fork team cùng base fix/preview-v02, đều OPEN; không ghi đè/cherry-pick/merge/đóng chúng. V07 nhánh phiên này thực hiện đúng kế hoạch đã duyệt với phạm vi B/quality/ma trận nền rộng hơn; PR cần nêu chồng lấn #8 để review lựa chọn. V05 có PR riêng nên không đề xuất làm lặp task đó; B01 là task CODEX độc lập kế tiếp.
- Phần chưa kiểm chứng: webcam thật ca sáng mới (người dùng chưa lưu raw/video), ESP32, model AI và KPI hardware NOT_RUN. H04/V01/V03 giữ gate riêng. Hướng dẫn thử V07 và định dạng video/raw/debug/log ngoài Git ở COVER_CAPTURE; mục tiêu thực tế là “đề xuất, chờ tôi xác nhận”. Không tự nhận DONE-HW.

- Số đo cuối fixture không viền đen giả, chạy tuần tự 2026-11-07T11:35:47–11:36:00+07:00, E1, HEAD 8f9198f + working-tree changes: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/benchmark_cover_geometry.py --baseline-ref 8f9198f0c78030dd21000f4562a0492556c1dce2 --repeats 3 --processing-width 640`, exit 0 PASS. 50 ca auto/B, 150 timed frames mỗi bản, decode=False: góc <10px + crop baseline 33/50, V07 50/50; max corner error 16.304→6.010px; median 13.704→40.066ms, p95 16.165→44.294ms. V07 tốn CPU hơn; preview độc lập không chứng minh FPS webcam.
- GUI cuối 2026-11-07T11:36:00–11:36:10+07:00, E1, HEAD + working-tree changes: cùng interpreter `-m vision.opencv --image $env:TEMP/pbl5-v07-smoke-20261107/<name>_nohalo.png --source-kind synthetic --output $env:TEMP/pbl5-v07-smoke-20261107/<name>_nohalo --duration 3 --screenshot $env:TEMP/pbl5-v07-smoke-20261107/<name>_nohalo_ui.png`, name=light,dark,plain; cả ba exit 0 PASS. Đã xem đủ ba ảnh: light/dark READY với góc ngoài/crop/QR PBL5-B04; plain QUALITY_WARNING/FOCUS_UNVERIFIED, lý do hiện rõ và không tự BLURRY/BAD_LIGHT. Đây là GUI với ảnh synthetic, không mở camera. Các lượt screenshot giữa phiên trước sửa fixture giữ ở temp, không commit.
- Cập nhật TASKS V07 hoàn thành acceptance phần mềm, STATE Active task NONE; giữ H04/V01/V03 chờ bằng chứng thật. Task kế tiếp B01 vì V05 đã có PR team #7 ở nhánh khác; chưa bắt đầu B01. Chuẩn bị kiểm cuối, commit/push nhánh và mở PR base fix/preview-v02; không đóng issue #1/#2 hoặc PR #8.

- Kiểm cuối sau cập nhật TASKS/STATE và fixture không viền giả, E1, HEAD 8f9198f + working-tree changes, 2026-11-07T11:38:01–11:38:16+07:00: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/check_repository.py` exit 0 PASS (31 source), cùng interpreter `scripts/check_codex_state.py` exit 0 PASS, `-m unittest discover -s tests -q` exit 0 PASS 88 tests/0 failures/0 errors/0 skips trong 13.418s; `git diff --check` exit 0 PASS. Không còn lỗi baseline/harness do phiên này; webcam vẫn NOT_RUN.
- Đối chiếu 17 đường dẫn thay đổi: detector/config/UI, fixtures/test/benchmark và tài liệu liên quan V07; không đổi camera/worker/storage/QR parser/schema, dependency manifests, firmware, ví dụ gốc, PLAN/ARCHITECTURE/DECISIONS. PROGRESS chỉ thêm link. Không stage ảnh/runtime log/dữ liệu/model. Commit nguồn không tự tham chiếu hash; PR/Last green sẽ ghi ở commit metadata sau kiểm sạch.


### Commit, push và PR V07

- Commit nguồn cd8b48c7afab2c700d36c6553a78598518453704, branch fix/cover-color-background. Kiểm nguyên trạng commit sạch, E1, 2026-11-07T11:39:13–11:39:44+07:00: `& D:/smart-vision-inspection/.venv/Scripts/python.exe scripts/check_repository.py` exit 0 PASS (31 nguồn), cùng interpreter `scripts/check_codex_state.py` exit 0 PASS, `-m unittest discover -s tests -q` exit 0 PASS 88 tests/0 failures/0 errors/0 skips trong 30.405s, `git diff --check` exit 0 PASS. `git status --short` rỗng trước kiểm, nên đây là bằng chứng commit nguyên trạng.
- `git push -u origin fix/cover-color-background` exit 0; `git ls-remote origin refs/heads/fix/cover-color-background refs/heads/main refs/heads/fix/preview-v02` exit 0: nhánh mới đúng cd8b48c, main vẫn d431f10fbb79dc086c8912702552463ca20262ab, V02 vẫn 8f9198f0c78030dd21000f4562a0492556c1dce2. Không force-push/merge.
- GitHub REST GET theo head rồi POST pulls: [PR #9](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/9) OPEN, head fix/cover-color-background, base fix/preview-v02, merged=false. Nội dung nêu mục đích/file/kiểm thực, chi phí CPU tăng, chồng lấn #8 và V05/#7, bằng chứng thực còn thiếu, H10 review và B01 kế tiếp. Không đóng issue hoặc thay PR team.
- Metadata cập nhật TASKS/STATE/SESSION_LOG với URL PR và Last green cd8b48c đã kiểm sạch; Active task NONE, V07 DONE acceptance phần mềm, B01 chưa bắt đầu. CI remote cần kiểm riêng theo SHA; không suy từ local. Link nhánh/ZIP trong STATE; webcam/ESP32/AI vẫn NOT_RUN. Mọi ngưỡng nghiệm thu mới vẫn “đề xuất, chờ tôi xác nhận”.

- Metadata kiểm lúc 2026-11-07T11:41:34+07:00, E1, HEAD cd8b48c + working-tree changes chỉ TASKS/STATE/SESSION_LOG: checker exit 0 PASS (31 nguồn), validator exit 0 PASS và git diff --check exit 0 PASS. Không chạy lại unittest vì chỉ sửa URL/hash/bằng chứng, code đã kiểm sạch ở cd8b48c.
- Xác minh remote lúc 2026-11-07T11:42:22.342465+07:00: GitHub API check-runs và actions/runs của commit nguồn cd8b48c đều completed/success, [Repository checks](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/actions/runs/42339492238). CI Windows Python 3.13 theo workflow hiện có; không suy trạng thái của commit metadata từ lượt này. HTTP HEAD link ZIP nhánh fix/cover-color-background trả 200 application/zip. Không merge hoặc thay đổi main.

## 2026-11-07 — Phiên 7: Kết nối điện thoại qua DroidCam

- Phiên ngày 2026-11-07; mốc mở GUI 21:51:47–21:51:51 +07:00, các probe trước đó không ghi timestamp riêng. Windows/PowerShell 5.1, Python venv 3.14.3, OpenCV 5.0.0. Nhánh fix/cover-color-background; commit gốc 30ae2b5022faa559bf333e49d576199c52c45a89, working tree sạch trước sửa tài liệu. Chỉ hỗ trợ camera cho V07; không bắt đầu B01, không merge.
- DirectShow SystemDeviceEnum (chỉ đọc FriendlyName): index 0 USB2.0 HD UVC WebCam, index 1 DroidCam Video. Người dùng xác nhận DroidCam Client có hình từ điện thoại. Không đổi driver/quyền Windows, không cài dependency.
- `$PYTHON -m vision.opencv --probe --probe-count 3 --backend dshow`: exit 0 do có một nguồn mở được; camera 0 PASS nhận ảnh, camera 1 FAIL mở nguồn, camera 2 FAIL không mở. Exit tổng không chứng minh mọi camera PASS.
- `$PYTHON -m vision.opencv --probe-one 1 --backend msmf`: exit 0 PASS nhận khung thực 1280×720, sequence 2. `$PYTHON -m vision.opencv --camera 1 --backend msmf --headless`: exit 0 PASS đọc ảnh/chạy pipeline; NO_COVER, QR UNREADABLE, copy_id null. Không lưu ảnh bằng headless.
- Khởi chạy GUI bằng pythonw với `-m vision.opencv --camera 1 --backend msmf`: tiến trình còn chạy, runtime.log xác nhận mở camera lúc 21:51:51+07:00. Không tự bấm lưu mẫu. Công cụ computer-use lỗi khởi tạo `helper_unknown_error: setup refresh had errors`, chưa quan sát trực quan cửa sổ qua công cụ; không coi log là bằng chứng hình nhận dạng đúng.
- Thêm hướng dẫn DroidCam trong COVER_CAPTURE, liên kết PROGRESS, ghi điểm tiếp tục STATE. Không thay code nghiệp vụ/config/dependency, không đổi trạng thái H04/V01/V03. Dữ liệu/runtime log nằm ngoài Git. Hạn chế: nhận dạng bìa/QR thật, độ trễ Wi-Fi và pilot nhiều nền chưa kiểm chứng; chờ người dùng thử B/S và gửi bằng chứng. Last green giữ nguyên commit nguồn đã kiểm trước đó.

- Kiểm tra tài liệu lúc 2026-11-07T21:53:28+07:00: HEAD 30ae2b5 + working-tree changes chỉ bốn file docs. `$PYTHON scripts/check_repository.py` exit 0 PASS (31 nguồn); `$PYTHON scripts/check_codex_state.py` exit 0 PASS; `git diff --check` exit 0 PASS. Unittest NOT_RUN lại vì chỉ sửa tài liệu, không sửa code/config. Commit/push cùng nhánh cập nhật PR #9 hiện có; không mở PR trùng. Điểm tiếp tục: người dùng thử nhận dạng với camera điện thoại đang mở.

## 2026-11-07 — Phiên 8: V08 Việt hóa giao diện thu ảnh

- Yêu cầu: chữ và hướng dẫn dễ đọc cho người dùng Việt. Nhánh feat/vietnamese-capture-ui từ 91237589588c8023fd9420994e7fef8290ff9436 (fix/cover-color-background); main và hai file sửa sẵn tại checkout chính giữ nguyên. Windows/PowerShell 5.1, interpreter venv Python 3.14.3/OpenCV 5.0.0; lệnh dưới dùng `$PYTHON` là interpreter này.
- Baseline trước sửa lúc 22:08:44–22:09:18 +07:00: `$PYTHON scripts/check_repository.py` exit 0 PASS 31 nguồn; `$PYTHON -m unittest discover -s tests -q` exit 0 PASS 88 tests/0 failures/errors/skips trong 33.682s, working tree sạch ở commit gốc. Không mở camera cho baseline.
- Dịch title, trạng thái, QR, thông số, phím, hướng dẫn nền/chọn góc/lưu và lỗi phổ biến; mã lưu/JSON/parser/worker giữ nguyên. Thêm renderer Unicode bằng GDI/Segoe UI qua ctypes, cache tối đa 256 nhãn, thu hồi handle mỗi lần dựng chữ, rút gọn theo độ rộng. Không thêm dependency hoặc đổi ngưỡng. Ngoài Windows hiển thị không dấu. annotate chỉ bổ sung show_status=True mặc định để debug cũ không đổi, GUI vẽ nhãn Việt riêng.
- Kiểm tra riêng 22:12:53: 4 test Unicode/giới hạn canvas/fallback/không mutate enum PASS; kiểm 300 nhãn không tăng handle GDI quá giới hạn test. Hồi quy trước chỉnh nhãn trên ảnh: 92 tests PASS/0 failures/errors/skips, 18.517s. Sau sửa nhãn preview và thêm test giữ debug cũ, `$PYTHON -m unittest tests.opencv.test_vietnamese_ui tests.opencv.test_async_preview -q` exit 0 PASS 22 tests trong 1.835s, không skip.
- GUI synthetic: tạo ảnh bằng tests.opencv.color_fixtures.color_scene, lưu ngoài Git tại thư mục TEMP/pbl5-ui-vi-20261107. `$PYTHON -m vision.opencv --image "$env:TEMP/pbl5-ui-vi-20261107/synthetic.png" --source-kind synthetic --output "$env:TEMP/pbl5-ui-vi-20261107/session-final" --duration 3 --screenshot "$env:TEMP/pbl5-ui-vi-20261107/gui-final.png"` exit 0 PASS lúc 22:14:41–22:14:44+07:00. Đã xem ảnh giao diện đầy đủ: dấu Việt đúng, nhãn/phím không tràn, READY trên preview đã dịch. Đã xem render QR sai định dạng và cảnh báo thiếu chi tiết. Thử render 50 lượt cùng fixture trước chỉnh nhãn preview: trung bình 8.192 ms/lượt; không coi là FPS thiết bị.
- Lưu ý camera: ảnh người dùng gửi sau phiên 7 chứng minh nguồn từng xuất xanh dù cap.read trả dữ liệu; không nâng thành nghiệm thu camera từ probe cũ. Ảnh mới người dùng gửi trước V08 đã có bìa thực, nhưng pilot/QR/crop và gate H04/V01/V03 chưa hoàn tất. V08 chỉ nghiệm thu UI bằng synthetic; webcam bản Việt, hiệu năng camera dài hạn, firmware/AI NOT_RUN. Không thay cách lưu raw/debug/metadata. Không tự bắt đầu B01.

- Kiểm cuối 2026-11-07T22:17:40+07:00: HEAD 9123758 + working-tree changes V08. `$PYTHON scripts/check_repository.py` exit 0 PASS (34 nguồn); `$PYTHON scripts/check_codex_state.py` exit 0 PASS; `$PYTHON -m unittest discover -s tests -q` exit 0 PASS 93 tests/0 failures/errors/skips trong 13.915s; `git diff --check` exit 0 PASS. GUI synthetic đã xem chữ có dấu; dữ liệu thực/weights/dependency/firmware không thay đổi. V08 DONE theo acceptance phần mềm; Active task NONE, B01 chỉ là đề xuất tiếp theo. Last green giữ commit baseline đã tồn tại được kiểm sạch, không gán kết quả working tree cho HEAD.

- Bàn giao 2026-11-07T22:18:53+07:00: commit nguồn ef4e8987d855a29d990a95b0da5f9a062cf1c084; `git push -u origin feat/vietnamese-capture-ui` exit 0 và `git ls-remote origin refs/heads/feat/vietnamese-capture-ui` exit 0 đúng SHA. GitHub REST xác nhận [PR #10](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/10) OPEN, base fix/cover-color-background, merged=false. Metadata bổ sung URL/commit đã tồn tại, không tự ghi hash của commit metadata. Mở GUI bản Việt với `pythonw -m vision.opencv --camera 1 --backend msmf` để người dùng thử; việc mở ứng dụng không phải nghiệm thu nhận dạng/QR. Không merge, không đổi main.

- Rà cửa sổ thật sau khởi chạy phát hiện HighGUI làm sai dấu riêng thanh tiêu đề. Sửa tên cửa sổ thành `PBL5 | Thu anh bia sach A6` không dấu; nội dung trong canvas vẫn có dấu qua GDI như ảnh đã kiểm. Đây là sửa tương thích nhãn, không đổi camera/pipeline. Cần mở lại ứng dụng để nạp tên cửa sổ mới.

## 2026-11-10 — Phiên 2: Chuẩn hóa Damaged Books năm nhãn

- Yêu cầu triển khai kế hoạch mới, với bước đầu chỉ chuẩn hóa dataset và kiểm tra lại split. Nhánh feat/damaged-books-dataset từ feat/vietnamese-capture-ui bdf0c007331c896ae6ec678b3a6d53ec66b4be17; không sửa collector/geometry/QR/preview, bài học, firmware hoặc dữ liệu nguồn. Main và sửa có sẵn ở checkout chính không bị gộp vào commit.
- Đọc README/PROGRESS/nhật ký, PLAN/DECISIONS, TASKS/STATE, mã và trạng thái Git. Kế hoạch trực tiếp thay quy tắc hai lớp/QR/HOLD cho luồng mới; đã ghi D20–D23, không coi thiết kế là code đã chạy. Cố gắng giao kiểm toán độc lập cho sub-agent không thành công do model kế thừa không được hỗ trợ; kiểm trực tiếp thay thế.
- Công cụ vision.yolo.prepare convert/audit/split và review: bỏ dòng Tag ID4, đổi Wornout5→4, giữ tọa độ, ảnh và nhãn rỗng; output riêng không ghi đè; hash/version/license/nguồn. Source ZIP SHA256 dc2a81293b0f841b0fd187a410b869a1fc9021077ffc6221f9f33621ff978197; version damaged-books-v1-five-8f203ddd57d4.
- Dữ liệu thật: 620 ảnh, 3610 hộp; Barcode194, Notch729, Ripped411, Spot937, Wornout1339; bỏ379 Tag, giữ34 nhãn rỗng,51 ứng viên mẫu âm pending. README nguồn ghi đã stretch640×640; không thể gọi đó là ảnh gốc trước export.
- Lệnh dùng interpreter collector hiện có E1 Python3.14.3/OpenCV5.0.0: `python -m vision.yolo.prepare convert --source <source-root> --output <local-data>/prepared-verified` PASS; audit620 ảnh/nhãn với ZIP PASS, source_matches_zip=true. Lưu cục bộ manifest.json, review.csv, review.html, audit.json và split-readiness.json, ngoài Git.
- Split cũ618/1/1: validation chỉ Ripped, test thiếu Spot. Đã xem contact sheet train IMG_1316 / test IMG_7: cùng sách/thiết kế với vết rách và tem tương ứng; gán cùng group nhưng label_review vẫn pending. Còn618 ảnh chưa nhóm và620 ảnh chưa duyệt nhãn. Gọi reviewed_split trên dữ liệu thật trả lỗi dự kiến Need reviewed book groups before splitting; không tạo split/ZIP train giả.
- 9 test dataset PASS trong1.591s: remap/nguồn ZIP/nhãn rỗng/mẫu âm/quarantine/group disjoint/seed/class coverage/ảnh trùng/ảnh nhãn thay đổi/dữ liệu lỗi. Suite toàn bộ E1 `python -m unittest discover -s tests -q` PASS102 tests,0 failures/errors/skips trong14.975s (11:42:58–11:43:12+07:00); gồm93 hồi quy collector. `python scripts/check_repository.py` PASS38 nguồn và cấu trúc ledger; git diff --check PASS trước cập nhật hồ sơ cuối.
- Review HTML: `node --check` PASS; Node harness CSV roundtrip (dấu phẩy, ngoặc kép, newline, chuỗi có0 đầu) và từ chối quote chưa đóng PASS. Harness thử đầu viết CSV escape sai nên FAIL, đã sửa dữ liệu fixture theo csv.writer và chạy lại PASS; không sửa nguồn để né test. Kiểm tính năng trình duyệt tương tác trực tiếp NOT_RUN; không coi kiểm JS là thử camera.
- Đã phát hiện nháp phiên trước triển khai sang app/AI/Colab quá bước đầu; lưu cục bộ feat/damaged-books-abc b46faf8 để không mất công việc, chưa push/chấp nhận. Một test QR legacy trong môi trường AI3.11 của nháp FAIL (AMBIGUOUS thành VALID_FORMAT), chưa sửa và không dùng làm bằng chứng nghiệm thu. Nhánh dữ liệu loại toàn bộ mã/dependency ứng dụng đó; suite E1 hiện tại PASS. Môi trường collector không thay đổi; môi trường AI thử trước đó nằm riêng và chưa dùng trong bản bước này.
- Không train thật, không đo accuracy/latency model, không thử camera/thiết bị, không nghiệm thu simulator. A05 hoàn thành phạm vi chuyển đổi/kiểm split cũ; H14/A01 còn chờ rà dữ liệu thật. Đúng một việc tiếp theo: mở review.html, rà nhóm/nhãn và51 ứng viên âm rồi lưu CSV. Không tự bắt đầu bước kế tiếp.

### Xuất bản bước dữ liệu

- Commit nguồn10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9 đã push feat/damaged-books-dataset; ls-remote xác nhận đúng SHA. Base bdf0c00 và main d431f10 không đổi. PR #11 OPEN, merged=false, base feat/vietnamese-capture-ui; chỉ13 tệp dataset/test/docs, không có nguồn ảnh/ZIP/weights/venv hoặc app draft. CI nguồn ở lần đọc đầu đang chạy; không suy PASS từ local. Metadata URL/SHA được bổ sung sau khi commit nguồn đã tồn tại.

- Đọc lại GitHub Actions run42758217749: commit nguồn10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9 completed/success. STATE Last green cập nhật đúng SHA đã có CI; metadata bổ sung sau đó chưa tự suy CI PASS. Repository checker/ledger PASS38 nguồn và diff --check PASS sau bổ sung link; không chạy lại unittest vì chỉ đổi hồ sơ. Không merge.

## 2026-11-11 — Phiên 1: Kiểm tra CSV sau khi duyệt 51 mẫu âm

- Người dùng báo đã lưu review.csv. Đọc CSV UTF-8-sig và đối chiếu manifest: PASS620 dòng,620 ID duy nhất, tập ID khớp; cả51 negative_candidate có label_review=approved và negative_review=approved. Còn569 label_review=pending và618 group_id trống; không thay lựa chọn của người dùng hoặc tự duyệt nhãn khác.
- Đây là xác minh dữ liệu đã lưu, không đánh giá độc lập lại nội dung51 ảnh. H14/A01 chưa hoàn thành; không chia tập hoặc train. Tạo bản sao CSV có SHA trong tên ở cùng thư mục dữ liệu cục bộ, giữ snapshot lựa chọn người dùng.
- Cập nhật PROGRESS và hồ sơ TASKS/STATE nhánh dataset; giữ sửa có sẵn. Không đổi code, ảnh, hộp nhãn hoặc nguồn ZIP. Không chạy lại unittest vì chỉ kiểm CSV và cập nhật hồ sơ. Đúng một việc tiếp theo: gán nhóm sách theo cuốn/thiết kế; nạp review.csv mới nhất khi mở lại trang để giữ51 kết quả đã duyệt.

## 2026-11-11T17:13:43+07:00 — trợ lý hỗ trợ rà nhóm

Người dùng yêu cầu trợ lý làm phần gán nhóm. Đối chiếu contact sheet và ứng viên SIFT; loại các nối sai do tem thư viện hoặc bố cục nhà xuất bản giống nhau. Đã lưu 334 ảnh vào 124 nhóm trực quan; 286 ảnh còn trống group_id được để riêng. Có thể còn quan hệ cùng sách giữa các nhóm qua mặt trước/mặt sau chưa xác định. 569 nhãn vẫn pending; không tự duyệt nhãn.

PASS: 620 ID duy nhất; toàn bộ label_review/negative_review giữ nguyên so với bản sao ff8f6ed26484; giữ nhóm đã có; 620 checksum ảnh khớp manifest; HTML tái tạo khớp CSV. Không sửa ảnh/nhãn nguồn, không split/train. Báo cáo: data/local/damaged_books_v1/grouping-assist/visual-review-report.json. Bước tiếp theo: trợ lý tiếp tục xử lý góc chụp chưa xác định; không yêu cầu người dùng nhập lại toàn bộ ảnh. H14 chưa hoàn tất; thay đổi dữ liệu cục bộ không đưa vào Git.
## 2026-11-11T17:22:40+07:00 — rà tiếp 286 ảnh chưa nhóm

Đã xem 10 bảng ảnh chưa nhóm và 9 bảng so sánh lớn. Thêm 65 ảnh qua 30 quyết định nối; tách IMG chỉ mục50/238 (sách lãnh đạo) khỏi18/128 (nuôi cá). Hiện399 ảnh/151 nhóm,221 ảnh chưa rõ được ghi quarantine-round2.csv. Giữ nguyên mọi trạng thái nhãn,51 mẫu âm đã duyệt, nhóm train/test xác nhận trước đó. Không sửa hộp nhãn;569 nhãn vẫn pending.

Chạy review_round2.py, tạo lại HTML bằng vision.yolo.review. Kiểm chứng PASS:620 ID và trạng thái duyệt không đổi;620 checksum ảnh và nội dung nhãn khớp manifest;HTML khớp CSV;399 ảnh/151 nhóm;221 ID cách ly khớp ảnh chưa nhóm. Bằng chứng trong data/local/damaged_books_v1/grouping-assist/round2-result.json, round2-validation.txt; bản sao CSV có SHA trong tên. Chưa kiểm khả năng tách độc lập giữa mọi nhóm, chưa split/train. Một việc tiếp theo: rà nhãn phần đã gán nhóm, giữ riêng221 ảnh chưa rõ. H14 chưa hoàn tất. Dữ liệu thật chỉ lưu cục bộ, không stage.

## 2026-11-11T19:22:38.9428063+07:00 — Colab handoff

## Cập nhật 2026-11-11 — notebook Colab YOLO11n

Đã tạo notebook độc lập `notebooks/damaged_books_colab.ipynb` và hướng dẫn `docs/COLAB_TRAINING.md` trên nhánh `feat/damaged-books-colab`, worktree `data/local/worktrees/damaged-books-colab`. Nhánh mới dựa trên commit e75eed1; giữ nguyên bốn hồ sơ chưa commit của Gemini trên worktree dataset.

Đối chiếu trực tiếp split-reviewed-v1.zip: SHA256 0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1;253/54/54 ảnh,83/18/20 nhóm,đủ5 lớp;checksum từng tệp và không giao nhau ID/nhóm/nội dung ảnh PASS. Việc này xác minh cấu trúc split, không rà độc lập lại nhận định nhãn/nhóm của Gemini.

Notebook train từ yolo11n.pt,640px,100 epoch,patience20,batch16,seed42; ghim Ultralytics8.4.208 (đã xác minh PyPI). Lưu checkpoint Drive, best.pt, cấu hình thực tế, phiên bản thư viện, báo cáo validation/confusion và ZIP. YAML chạy chỉ chứa train/val; threshold chưa chọn, test chưa đánh giá. Không triển khai ứng dụng AI.

Kiểm chứng: mã các ô compile PASS; kiểm tra gói thật PASS;6 test cổng dữ liệu PASS. Lần test đầu có lỗi fixture dùng chung list lớp, đã sửa fixture và chạy lại PASS. Chưa chạy GPU Colab, chưa có model đã train, chưa có chất lượng AI hoặc độ trễ camera.

**Một việc tiếp theo:** người dùng mở notebook trên Colab, bật GPU, tải split-reviewed-v1.zip và chạy từng ô. A02/H08 còn chờ phiên GPU thật, không đánh DONE từ notebook.

Kiểm chứng cuối phiên Colab:108 tests PASS (28.187s), check_repository PASS, check_codex_state PASS, diff --check PASS. Ultralytics8.4.208 có trên PyPI; API Metric.ap đã kiểm trên môi trường AI riêng. Không cài thêm vào collector. GPU Colab/train thật NOT_RUN.


## 2026-11-11T18:22:00+07:00 — rà nhãn 368 ảnh đã gán nhóm

- Đã tạo 46 bảng đối chiếu song song ảnh gốc / ảnh vẽ hộp nhãn tại `data/local/damaged_books_v1/grouping-assist/label-sheets/label-sheet-00.jpg`..`label-sheet-45.jpg` và xem trực tiếp toàn bộ 368 ảnh có `group_id` đang ở trạng thái `label_review=pending`.
- Kết quả rà 368 ảnh: duyệt `approved` 330 ảnh; đánh dấu `rejected` 38 ảnh có lỗi nhãn rõ (gán nhầm tem chữ Tag thành Barcode/Spot, bỏ sót vết rách/mòn/bẩn hoặc vẽ hàng chục hộp Notch/Spot/Wornout đè lên chữ in, hình minh họa và vệt bóng lóa). Không tự sửa tệp nhãn trong `prepared-verified`.
- Toàn bộ 399 ảnh có nhóm (151 nhóm): 361 `approved` (330 ảnh mới duyệt + 31 mẫu âm đã duyệt, thuộc 148/151 nhóm, 1.993 hộp đủ 5 lớp: Barcode 115, Notch 335, Ripped 255, Spot 480, Wornout 808), 38 `rejected`, 0 `pending` (3 nhóm chỉ có ảnh bị loại: `visual_group_052`, `visual_group_062`, `visual_group_111`). Toàn bộ 620 ảnh: 381 `approved`, 38 `rejected`, 201 `pending`; giữ nguyên 51/51 mẫu âm đã duyệt và cách ly 221 ảnh chưa rõ nhóm.
- Sao lưu `review-before-label-review-076f7499062b.csv`, ghi `prepared-verified/review.csv` (SHA256 `42e09cf254e0e8959547fa3ec4445ce5983273aa18c27af8f3ff8707d5972725`), cập nhật `prepared-verified/review.html` và lưu báo cáo tại `grouping-assist/label-review-round3.json`, `questionable-labels-round3.csv`, `label-review-validation.txt`. Kiểm chứng PASS: 620 ID/checksum ảnh/nhãn khớp `manifest.json`, HTML khớp CSV, 221 ID cách ly khớp `quarantine-round2.csv`.
- Chưa chia tập `A01`, chưa chạy Colab/train. Đúng một việc tiếp theo: xác nhận phương án xử lý 38 ảnh `rejected` (cách ly khi split hay tạo phiên bản sửa nhãn riêng) và rà soát quan hệ cùng cuốn giữa các nhóm trước khi chạy split.

## 2026-11-11T18:52:00+07:00 — kiểm tra độc lập 148 nhóm và tạo split `split-reviewed-v1` (H14, A01)

- Người dùng xác nhận giữ cách ly 38 ảnh nghi vấn (`rejected`) và 221 ảnh chưa rõ nhóm, yêu cầu kiểm tra độc lập giữa 148 nhóm của 361 ảnh đạt, gộp các nhóm cùng sách/thiết kế bìa rồi tạo split khoảng 70/15/15 với `seed=42`.
- Đã tạo 15 bảng tổng hợp 148 nhóm tại `data/local/damaged_books_v1/grouping-assist/group-independence-sheets/groups-148-00.jpg`..`groups-148-14.jpg`, đối chiếu trực quan và SIFT liên nhóm: tách `idx:282` (gáy sách *다산선생 지식경영법*) khỏi `visual_group_026` sang `visual_group_073`, đồng thời thực hiện 21 phép gộp nhóm (loại bỏ 27 mã nhóm trùng do chụp khác mặt bìa/gáy/mặt sau của cùng cuốn hoặc cùng thiết kế bìa bộ sách như KIPF, 민음사 세계문학전집, 다이제스트 100, 제3인류).
- Sau khi gộp: 399 ảnh có nhóm thuộc 124 nhóm trực quan; **361 ảnh `approved` thuộc 121 nhóm độc lập** (3 nhóm chỉ chứa ảnh `rejected`); 259 ảnh cách ly (38 `rejected` + 221 chưa rõ nhóm). Sao lưu `review-before-group-merge-42e09cf254e0.csv`, cập nhật `prepared-verified/review.csv` (SHA256 `668f59cfb4b9139896764f11dd7875b6471168c039dab523dda30348882dc183`), lưu báo cáo `grouping-assist/group-independence-round4.json` và tạo lại `prepared-verified/review.html` PASS.
- Chạy `python -m vision.yolo.prepare split --prepared .../prepared-verified --output .../split-reviewed-v1` PASS: tạo `split-reviewed-v1` và `split-reviewed-v1.zip` (SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`, version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`, seed `42`).
- Kết quả thực tế từng tập (361 ảnh / 121 nhóm, giao nhau nhóm = 0, cả 3 tập đủ 5 lớp):
  - `train`: 253 ảnh (70,08%), 83 nhóm (68,60%) — `Barcode`: 77, `Notch`: 250, `Ripped`: 173, `Spot`: 355, `Wornout`: 544.
  - `val`: 54 ảnh (14,96%), 18 nhóm (14,88%) — `Barcode`: 25, `Notch`: 53, `Ripped`: 39, `Spot`: 65, `Wornout`: 145.
  - `test`: 54 ảnh (14,96%), 20 nhóm (16,53%) — `Barcode`: 13, `Notch`: 32, `Ripped`: 43, `Spot`: 60, `Wornout`: 119.
  - `quarantined`: 259 ảnh.
- Cập nhật `H14` và `A01` sang `DONE`. Chưa huấn luyện mô hình; bước tiếp theo là `H08`/`A02` trên Colab GPU với gói `split-reviewed-v1.zip`.

## 2026-11-11T21:13:02.8620848+07:00 — GitHub team training publication

## Cập nhật 2026-11-11 — đồng bộ GitHub cho team train song song

Đã push hồ sơ rà nhãn/nhóm còn thiếu của Gemini lên feat/damaged-books-dataset (cbe14bb), hợp nhất lịch sử vào feat/damaged-books-colab và push công cụ team (b310c53). Không merge PR vào main. Giữ bản nháp ứng dụng chưa nghiệm thu ngoài gói train và giữ dữ liệu nguồn tại máy.

Notebook tải split-reviewed-v1.zip từ GitHub Releases, kiểm SHA256 và hỗ trợ n640/s640/n960 với cùng seed42. Mỗi lượt ghi TEAM_MEMBER, EXPERIMENT, GPU, model/dataset hash, cấu hình thực tế và experiment-summary.csv. Tất cả so sánh trên validation; test chỉ đánh giá cuối. Phiên n960 chỉ thay kích thước đầu vào của ảnh nguồn640px.

Dataset361 ảnh và manifest/attribution/SHA256SUMS đã phát hành: https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/releases/tag/damaged-books-reviewed-v1 . Tải công khai ZIP12693288 byte và đối chiếu SHA256 PASS; notebook remote khớp blob commit và JSON local PASS. 111 test PASS (38.097s);check_repository/check_codex_state/diff PASS. GPU train NOT_RUN; chưa có model thắng hoặc nghiệm thu camera.

**Một việc tiếp theo:** team mở notebook trên nhánh feat/damaged-books-colab, chọn TEAM_MEMBER và chia n640/s640/n960, chạy bằng GPU riêng rồi gửi ZIP và experiment-summary.csv để so sánh. H08/A02 còn chờ phiên GPU thật. Xem docs/TEAM_TRAINING.md và docs/COLAB_TRAINING.md trên nhánh Colab.
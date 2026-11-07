# Codebase map

Audit baseline `d431f10fbb79dc086c8912702552463ca20262ab`, ngày 2026-11-07. Inventory lấy từ `git ls-files` của worktree sạch, không suy từ danh sách thư mục. Đã đọc toàn văn 64/64 tệp tracked baseline, chia ba phần: vision/software/examples/tests; firmware/scripts/config/CI; tài liệu dự án. Không có mã tracked chưa đọc trong snapshot này. Các file harness mới được review riêng sau triển khai; xem SESSION_LOG.

Ngoài inventory, đã đọc AGENTS.md local và các phần policy/HMI của roadmap nguồn local; hai file này bị ignore tại baseline. Không copy dữ liệu local hay thay đổi có sẵn ở checkout chính vào PR. Không tính `.venv`, `.pio`, vendor, ảnh/metadata riêng, weights hoặc file generated là source; không audit nội dung các tập đó. Vì vậy không kết luận dữ liệu riêng không tồn tại, chỉ xác nhận chúng không có trong clean checkout.

## Bản đồ module

| Đường dẫn | Mục đích | Entry hoặc bên gọi | Config | Dependency | Test tương ứng |
|---|---|---|---|---|---|
| vision và software namespace | Gói Python, version collector | import/module CLI | chưa có config riêng | stdlib | import gián tiếp |
| vision/opencv/__main__.py | Điểm chạy collector | python -m vision.opencv → cover_capture_app.main | CLI | software.desktop | RelocationTests |
| vision/opencv/config.py | Đọc/kiểm cấu hình và đường dẫn độc lập cwd | UI, pipeline, dataset | configs/cover_capture.json | stdlib | ConfigTests, RelocationTests |
| vision/opencv/camera.py | Thread latest-frame, session/sequence/timestamp, release/lỗi đọc | CameraAdapter từ UI/headless/probe | camera index/backend/resolution | cv2 | CameraTests, FakeCapture |
| vision/opencv/pipeline.py | Geometry A6, warp, quality, ổn định, QR | CoverVision, QRReader từ process_snapshot/headless | Config; tỉ lệ 105:148 | cv2, numpy | GeometryTests, QRTests |
| vision/opencv/dataset.py | Bundle PNG/JSON, checksum/manifest/rebuild | DatasetWriter từ UI/headless | output/config | cv2, numpy, stdlib | StorageTests |
| vision/yolo | Tài liệu phạm vi AI, chưa có train/inference | chưa có | chưa có | AI chưa khai báo | chưa có |
| software/desktop/cover_capture_app.py | OpenCV GUI, phím/mouse, CLI/headless/probe | main/run_ui/headless | CLI + Config | vision.opencv, cv2, numpy | AppTests, RelocationTests |
| software phần còn lại | Dự định DB/policy/API/HMI/transport | chưa có | chưa có | chưa có FastAPI/AI/serial trong manifests | chưa có |
| examples/opencv_basics/01_camera.py | Bài camera gốc | chạy trực tiếp | camera 0 trong code | cv2 | chưa có; không import vào sản phẩm |
| examples/opencv_basics/02_image_processing.py | Gray/blur/threshold | chạy trực tiếp | threshold 120, camera 0 | cv2 | chưa có |
| examples/opencv_basics/03_find_contours.py | Otsu/contour/bounding box | chạy trực tiếp | MIN_AREA | cv2 | chưa có |
| examples/opencv_basics/04_object_features.py | Area/perimeter/aspect/circularity | chạy trực tiếp | MIN_AREA/BORDER_MARGIN | cv2, math | chưa có |
| examples/opencv_basics/05_rule_based_inspection.py | So mẫu tham chiếu nhấn R, OK/NG học tập | chạy trực tiếp | ngưỡng area/aspect/rect | cv2 | chưa có; không phải policy A/B |
| firmware/esp32 | Scaffold Arduino | setup gọi myFunction(2,3), loop rỗng | platformio.ini: esp32dev/Arduino | espressif32 | test/README chỉ là mẫu; build không là test cơ cấu |
| scripts/capture_covers.py | Launcher độc lập cwd | gọi desktop.main | CLI | Python/collector | RelocationTests |
| scripts/windows/CaptureCovers.cmd | Launcher Windows về root | người vận hành | .venv tại root | cmd/Python | chưa có test wrapper riêng |
| scripts/windows/camera-priority/CameraPolicy.psm1 | Policy disable/restore camera | CameraPriority.ps1 | thiết bị A4tech/laptop được cấu hình | Windows PowerShell/PnP | Test-CameraPriority.ps1 |
| scripts/windows/camera-priority/CameraPriority.ps1 và .cmd | Menu, Diagnose/Install/Run/Pause/Uninstall | tiện ích độc lập collector | config/state tại thư mục công cụ Windows | PnP/WMI/Scheduled Tasks/ACL | 23 test mô phỏng, không kiểm PnP/video thật |
| scripts/check_repository.py | AST Python, link tài liệu, workspace; thêm gọi validator harness | CLI và CI | workspace JSON | stdlib | chạy trực tiếp; giữ các kiểm cũ |
| scripts/check_codex_state.py | Kiểm cấu trúc và nhất quán TASKS/STATE | checker hoặc CLI --root | docs/codex/TASKS.md, STATE.md | stdlib | tests/test_codex_state.py với fixture tạm |
| tests/opencv/test_cover_capture.py | 19 test trước harness | unittest discover | fixture tự sinh/fake camera | unittest, cv2, numpy | không thiết bị thật |
| tests/test_repository_layout.py | 3 test entrypoint/config/cwd | unittest discover | thư mục tạm | subprocess/unittest | CLI --help, không camera |
| .github/workflows/checks.yml | CI PR/push main/manual | GitHub Actions | windows-latest, Python 3.13 | manifests hiện có | check_repository và unittest; không firmware/thiết bị |
| .github templates và CONTRIBUTING | Quy trình issue/review PR | người đóng góp | nhánh riêng, reviewer ngoài tác giả | Git/GitHub | review thủ công |
| data READMEs | Quy định dữ liệu ngoài Git | người thu/huấn luyện | real/imported/synthetic, raw bất biến | chưa có dataset tracked | chưa chứng minh chất lượng dữ liệu |
| docs/codex | Tiến độ/tiếp tục/roadmap/quy trình | AGENTS.md | TASKS duy nhất giữ Status | validator stdlib | fixture validator + review nội dung |

Dependencies runnable baseline: requirements.txt trỏ vision/opencv/requirements.txt với opencv-python>=4.10,<6 và numpy>=1.26,<3. requirements-observed.txt là ghi nhận bài học, không phải dependency AI đã duyệt. Config quality là default triển khai, chưa phải mục tiêu nghiệm thu chính thức.

## Luồng thực tế và mức bằng chứng

Code nối được: CLI/module → cover_capture_app → CameraAdapter hoặc ảnh import → CoverVision/QRReader → DatasetWriter → raw/cover/debug PNG + metadata JSON + manifest JSONL. Baseline đã chạy đường synthetic/fake trong 22 tests; không mở camera phiên này. Kết quả cũ B08 trong COVER_CAPTURE_VALIDATION là hồ sơ lịch sử, không được nâng thành DONE-HW trong TASKS.

Mắt xích thiếu: SQLite lookup → identity VALID/UNKNOWN_ID → AI/model → policy A/B/HOLD/STOP → job API/HMI → ControllerTransport/simulator/serial → firmware điều khiển → feedback khay. dataset.py đặt identity_status=NOT_CHECKED, title_id=None, ai_quality/defect_labels=None. Không dùng accepted/READY làm PASS AI hoặc đúng khay.

## Sai khác và giới hạn cần theo dõi

| Mã | Căn cứ | Tác động | Câu hỏi/task |
|---|---|---|---|
| C1 | DECISIONS.md mục Trạng thái dữ liệu có 5 QR enums; pipeline.py:80 QRReader.read tạo DECODE_ERROR, :214 CoverVision.process tạo PENDING | API sau này cần mapping rõ; chưa tự chọn mở rộng enum hay giữ nội bộ | Q9, H12, V04 |
| C2 | CONTRIBUTING/PLAN/PROGRESS cũ trỏ PROGRESS là tiến độ; yêu cầu phiên này chọn TASKS làm nguồn duy nhất | Không sửa các file ngoài allowlist; PROGRESS thêm chỉ dẫn, bảng cũ chỉ snapshot lịch sử | H01, WORKFLOW |
| C3 | .gitignore bỏ /AGENTS.md và /docs/ROADMAP_SOURCE.md; clean clone chưa có hai file hướng dẫn local | Force-add duy nhất AGENTS đã review; không thay .gitignore; kế hoạch versioned dùng PLAN và docs/codex | H01 |
| C4 | Roadmap nguồn local Bước 9 dùng STOP_FAULT/GOOD trong ví dụ; DECISIONS dùng STOP/PASS; D05 chưa có mapping category cụ thể | Ví dụ nguồn không tự thành policy chính thức; giữ enum quyết định, hỏi nghĩa nghiệp vụ chưa rõ | Q1, H06, S01 |

Không phải mâu thuẫn: firmware/AI chỉ là dự định trong ARCHITECTURE, READMEs đã nói chưa triển khai; README/COVER_CAPTURE/PLAN đều thừa nhận preview đồng bộ và lỗi mép bìa. Issue #2 nói nghỉ thêm 150 ms nhưng run_ui hiện chỉ thấy waitKey(10), không có sleep(0.15); phần mô tả thời gian của issue không khớp snapshot code. V02 phải đo baseline thực tế, không dùng 150 ms làm số đo. A6 đúng phạm vi README hiện tại, không tự mở rộng mọi cỡ sách. Chưa xác minh camera thật, PnP thật, Linux, model, cơ cấu hoặc end-to-end hardware.

## Inventory đã đọc tại commit gốc

Danh sách dưới đây là toàn bộ `git ls-files` baseline (64 tệp), tất cả đã đọc đầy đủ; không phải danh sách file mới của harness.

```text
.editorconfig
.gitattributes
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/task.yml
.github/pull_request_template.md
.github/workflows/checks.yml
.gitignore
CONTRIBUTING.md
PROGRESS.md
README.md
data/README.md
data/opencv/README.md
docs/ARCHITECTURE.md
docs/COVER_CAPTURE.md
docs/COVER_CAPTURE_VALIDATION.md
docs/DECISIONS.md
docs/PLAN.md
docs/SESSION_LOG.md
examples/opencv_basics/01_camera.py
examples/opencv_basics/02_image_processing.py
examples/opencv_basics/03_find_contours.py
examples/opencv_basics/04_object_features.py
examples/opencv_basics/05_rule_based_inspection.py
examples/opencv_basics/README.md
examples/opencv_basics/requirements-observed.txt
firmware/README.md
firmware/esp32/.gitignore
firmware/esp32/include/README
firmware/esp32/lib/README
firmware/esp32/platformio.ini
firmware/esp32/src/main.cpp
firmware/esp32/test/README
requirements.txt
scripts/README.md
scripts/capture_covers.py
scripts/check_repository.py
scripts/windows/CaptureCovers.cmd
scripts/windows/camera-priority/.gitignore
scripts/windows/camera-priority/CameraPolicy.psm1
scripts/windows/camera-priority/CameraPriority.cmd
scripts/windows/camera-priority/CameraPriority.ps1
scripts/windows/camera-priority/README.md
scripts/windows/camera-priority/Test-CameraPriority.ps1
scripts/windows/camera-priority/VALIDATION.md
smart-vision-inspection.code-workspace
software/README.md
software/__init__.py
software/desktop/__init__.py
software/desktop/cover_capture_app.py
tests/__init__.py
tests/opencv/__init__.py
tests/opencv/test_cover_capture.py
tests/test_repository_layout.py
vision/__init__.py
vision/opencv/README.md
vision/opencv/__init__.py
vision/opencv/__main__.py
vision/opencv/camera.py
vision/opencv/config.py
vision/opencv/configs/cover_capture.json
vision/opencv/dataset.py
vision/opencv/pipeline.py
vision/opencv/requirements.txt
vision/yolo/README.md
```


## Delta V02 — 2026-11-07

Inventory baseline phía trên được giữ làm căn cứ audit ban đầu. V02 bổ sung software/desktop/analysis_worker.py (AnalysisWorker, SnapshotProcessor; gọi từ run_ui, config snapshot, stdlib/thread + CoverVision), tests/opencv/test_async_preview.py (17 regressions synthetic) và scripts/benchmark_preview.py (entry CLI, delay/frames/baseline-ref; dùng dependency hiện có, không camera). Đã đọc/review các tệp mới và diff UI/tests cũ. Luồng live hiện là camera → preview mới nhất song song worker → completion gắn frame → writer; preview không chờ geometry/QR. Xem [báo cáo V02](../PREVIEW_VALIDATION.md), trạng thái chỉ trong TASKS. Các nhận định đồng bộ ở phần baseline không mô tả phiên bản sau V02.


## Delta V07 — 2026-11-07

Baseline inventory và các mâu thuẫn ở trên được giữ làm lịch sử; hiện trạng geometry/quality sau V07 đối chiếu [báo cáo](../COLOR_BACKGROUND_VALIDATION.md). Đã đọc toàn bộ file mới và diff liên quan; không audit lại các module không đổi hoặc suy nghiệm thu thiết bị.

| Module/đường dẫn | Mục đích và entry/bên gọi | Config/dependency | Test |
|---|---|---|---|
| vision/opencv/geometry.py | detect_cover, prepare_lab và helper góc; CoverVision.detect/calibrate gọi | Config ngưỡng Lab/cạnh/dải mép; OpenCV/NumPy hiện có | test_color_background và GeometryTests cũ |
| vision/opencv/quality.py | assess_quality; CoverVision.process gọi trước quyết định quality | min_sharpness/detail/clipping; OpenCV/NumPy | CoverQualityTests và test blur cũ |
| vision/opencv/pipeline.py, config.py | Giữ API, QR, warp, temporal stability; ghép geometry/quality mới và metrics | JSON cũ vẫn hợp lệ, default mới trong Config | Toàn bộ tests/opencv, storage/async vẫn chạy |
| software/desktop/cover_capture_app.py | render thêm Detail focus/Clip và lý do thiếu chi tiết | Không đổi worker/camera/save; không dependency mới | GUI synthetic và test_async_preview |
| tests/opencv/color_fixtures.py, test_color_background.py | 25 cảnh × auto/B; góc/crop ground truth và các ca an toàn/quality | Synthetic có seed; QR encoder OpenCV có sẵn | unittest discovery |
| scripts/benchmark_cover_geometry.py | CLI so baseline Git với hiện tại trên cùng fixtures | baseline-ref/repeats/processing-width; stdlib/OpenCV/NumPy | Lệnh benchmark, 50 ca và báo sai góc; chưa camera |

Luồng camera → worker → geometry/quality/QR → crop/bundle vẫn nối như V02; B so nền theo vị trí và bù dịch Lab chung, mép cần bằng chứng cả bốn cạnh/tương phản gần-xa. Không đổi DB/AI/controller/firmware chưa có. Các mô tả baseline dùng Canny cố định và brightness trung bình chặn trực tiếp đã được thay ở V07; chẩn đoán cũ vẫn giữ để đối chiếu. Enum QR C1/H12 chưa được tự quyết. Không có raw lỗi sáng mới do người dùng cung cấp; H04/V01/V03 chưa được nghiệm thu.

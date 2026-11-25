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

## 2026-11-07 — Phiên 1: Rà soát tiến độ và thứ tự phát triển

- Yêu cầu: báo tiến độ thực tế và những phần cần phát triển để hoàn chỉnh dự án.
- Đã đọc README, PROGRESS, PLAN, DECISIONS, nhật ký, báo cáo kiểm chứng và các bước liên quan trong roadmap nguồn; đối chiếu mã collector, metadata, README AI/software và firmware.
- Git local trước khi ghi hồ sơ sạch tại d431f10 (2026-10-29); không kiểm tra lại remote/CI.
- Lệnh `.venv\Scripts\python.exe scripts/check_repository.py`: PASS, 21 tệp Python, liên kết tài liệu và đường dẫn workspace.
- Lệnh `.venv\Scripts\python.exe -m unittest discover -s tests -v`: PASS, 22/22 test trong 9.008 giây. Phạm vi là phần mềm với ảnh tổng hợp/camera mô phỏng, không phải nghiệm thu webcam/cơ cấu.
- Webcam, pilot, build/upload firmware, phần cứng và AI/end-to-end: NOT_RUN trong phiên này; không tạo chỉ số thay thế.
- Làm rõ tiến độ: collector đã có code; vision/yolo mới có tài liệu, main.cpp là template; database/backend/HMI/simulator/protocol chưa có module sản phẩm. Không có bằng chứng hoàn thành thêm bài thực hành.
- Cập nhật PROGRESS theo mã mốc/trạng thái chuẩn, tách bằng chứng 2026-10-29 khỏi kết quả hiện tại. Không thay đổi mã nguồn hoặc bài học; không thay đổi phạm vi/kiến trúc.
- Điểm nghẽn: lựa chọn mép bìa sai trên nền có đường ron; preview vẫn xử lý geometry/QR đồng bộ.
- Đúng một việc tiếp theo: ổn định geometry/crop M02 từ ảnh B08, rồi kiểm chứng camera cố định với khoảng 10–20 cuốn và lưu raw/crop/debug; còn chờ thực hành/kiểm chứng thực tế.

## 2026-11-09 — Phiên 1: Đối chiếu tiến độ và việc tiếp theo

- Yêu cầu: kiểm tra dự án đang đến đâu và xác định bước tiếp theo.
- Đã đọc AGENTS, README, PROGRESS, mục nhật ký gần nhất, PLAN, DECISIONS và điều kiện nghiệm thu M02 trong ROADMAP_SOURCE; đối chiếu danh sách tệp, camera, bộ chọn tứ giác, vòng UI, metadata, README AI/software và firmware mẫu.
- Git: `git status --short` và `diff -- PROGRESS.md docs/SESSION_LOG.md`; commit local `d431f10` (2026-10-29). Trước phiên đã có thay đổi chưa commit ở hai hồ sơ này; không có thay đổi mã nguồn được Git báo cáo. Không sửa cấu hình Git toàn cục, không kiểm tra lại remote/CI.
- Lệnh `.venv\Scripts\python.exe scripts/check_repository.py`: PASS, 21 tệp Python, liên kết tài liệu và đường dẫn workspace.
- Lệnh `.venv\Scripts\python.exe -m unittest discover -s tests -v`: PASS, 22/22 test trong 8.120 giây; phạm vi ảnh tổng hợp, camera mô phỏng, lưu dữ liệu và entrypoint.
- Webcam/pilot, tiện ích PnP thật, firmware build/upload và cơ cấu thật: NOT_RUN trong phiên này. AI/end-to-end: NOT_RUN vì chưa có module đầy đủ; các chỉ số chưa đo là N/A.
- Trạng thái giữ nguyên: M02 IN_PROGRESS; M01/M03/M05 có code nhưng chưa đủ nghiệm thu; M04 và các mốc AI/backend/HMI/điều khiển/tích hợp vẫn TODO. YOLO mới có README, metadata identity_status=NOT_CHECKED, main.cpp vẫn là template.
- Điểm nghẽn chưa được sửa trong phiên: bộ chọn tứ giác có thể bám đường ron/mép hình in; vòng UI vẫn gọi xử lý geometry/QR đồng bộ. Chỉ cập nhật hồ sơ, không sửa bài học hoặc mã sản phẩm.
- Đúng một việc tiếp theo: ổn định chọn mép ngoài/crop bìa ở M02, bắt đầu bằng tái hiện lỗi trên ảnh B08 đã lưu; sau sửa kiểm chứng camera cố định với khoảng 10–20 cuốn, lưu raw/crop/debug và các ca lệch/ngoài vùng. Còn chờ thực hành và bằng chứng camera thật; chưa chuyển bài.

## 2026-11-10 — Phiên 1: Đối chiếu tiến độ giữa main và các nhánh phát triển

- Yêu cầu: xem xét dự án đã đến đâu và chọn việc tiếp theo. Đã đọc README/PROGRESS/nhật ký, PLAN/DECISIONS, điều kiện M02 trong ROADMAP_SOURCE; đối chiếu code, Git và ledger của worktree phát triển.
- Checkout chính: main `d431f10fbb79dc086c8912702552463ca20262ab`; trước phiên chỉ có sửa chưa commit ở PROGRESS.md và docs/SESSION_LOG.md. Đọc diff, giữ nội dung lịch sử; không sửa code, chuyển nhánh hoặc merge.
- `git worktree list --porcelain` và `branch -avv` tìm thấy worktree sạch nhánh feat/vietnamese-capture-ui tại `bdf0c007331c896ae6ec678b3a6d53ec66b4be17`. Đọc TASKS/STATE, mã AnalysisWorker, geometry/quality, UI tiếng Việt và test. Bản này đã gồm V02/V07/V08; các chức năng đó chưa có trong main.
- Xác minh mạng: `git ls-remote origin refs/heads/main refs/heads/feat/vietnamese-capture-ui refs/heads/fix/cover-color-background` PASS; remote lần lượt là d431f10, bdf0c00, 9123758. GitHub REST GET `/repos/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pulls?state=all&per_page=20&sort=updated&direction=desc` trả PR #5–#10 OPEN, merged_at=null. Không kiểm CI; không sửa PR hoặc gửi thông điệp cho team.
- Main: `.venv\Scripts\python.exe scripts/check_repository.py` PASS (21 Python source); `.venv\Scripts\python.exe -m unittest discover -s tests -v` PASS 22/22 trong 4.085 giây.
- Worktree feat/vietnamese-capture-ui, dùng interpreter venv của checkout chính: `python scripts/check_repository.py` PASS (34 source); `python scripts/check_codex_state.py` PASS; `python -m unittest discover -s tests -q` PASS 93/93 trong 15.980 giây. Dòng synthetic decode failure trong log là ca kiểm lỗi giả lập; kết quả toàn bộ suite OK. Test dùng ảnh tổng hợp/camera mô phỏng, không nghiệm thu thiết bị.
- Sai khác hồ sơ: kết luận ngày 2026-11-09 chỉ phản ánh main nên bỏ sót tiến độ nhánh khác. Đã sửa PROGRESS để tách main khỏi bản phát triển; không lặp lại task preview/Việt hóa/cải tiến synthetic đã có. PR #7/#8 chỉ xác minh trạng thái, chưa audit code/test nên không nâng task theo tiêu đề.
- M02 vẫn IN_PROGRESS: V01/H04/V03 chờ ảnh lỗi và kiểm chứng thật. SQLite/AI/backend/HMI/controller/firmware chức năng chưa có trong bản đã kiểm. Camera thật, pilot, build/upload, cơ cấu, AI/end-to-end NOT_RUN; chỉ số chưa đo N/A.
- Đúng một việc tiếp theo: thử crop trên camera thật bằng bản feat/vietnamese-capture-ui, bắt đầu với một bìa sáng và một bìa tối, camera cố định, hiệu chuẩn B nền trống; lưu raw/crop/debug/metadata và ca sai mép để phục vụ V01/V03. B01 là task code độc lập kế tiếp trong ledger nhưng chưa bắt đầu; câu hỏi tiến độ không thay bài đang chờ thực hành.

## 2026-11-10 — Phiên 2: Bước đầu Damaged Books năm nhãn

- Người dùng duyệt kế hoạch mới, giới hạn bước triển khai đầu ở chuẩn hóa dataset và kiểm split. Tạo nhánh feat/damaged-books-dataset từ bản preview/Việt hóa bdf0c00; worktree data/local/worktrees/damaged-books-abc. Không đổi main, mã collector chính, dữ liệu ZIP/ảnh/nhãn nguồn hoặc gộp sửa hồ sơ có sẵn vào commit nhánh.
- Đã chuyển bản dữ liệu riêng data/local/damaged_books_v1/prepared-verified: 620 ảnh,3610 hộp; Barcode194/Notch729/Ripped411/Spot937/Wornout1339; xóa379 hộp Tag, remap5→4, giữ34 nhãn rỗng và51 ứng viên âm pending. Manifest version damaged-books-v1-five-8f203ddd57d4, giấy phép CC BY4.0 và checksum nguồn. Audit toàn bộ620 ảnh/nhãn so ZIP PASS; ZIP SHA256 dc2a81293b0f841b0fd187a410b869a1fc9021077ffc6221f9f33621ff978197.
- Có công cụ convert/audit/review và split theo nhóm seed42/xấp xỉ70/15/15, bắt buộc đủ5 lớp và loại ảnh chưa duyệt khỏi train/val/test. Đã xem bằng chứng cùng cuốn train IMG_1316 / test IMG_7. Split cũ618/1/1 bị loại cho đánh giá; gọi split thật bị chặn đúng vì nhóm/nhãn chưa duyệt, chưa tạo split train giả.
- Dùng môi trường collector cũ, không thay dependency: 9 test dataset PASS1.591s; toàn suite nhánh mới PASS102 tests/0 failures/errors/skips14.975s; repository/ledger checker PASS38 nguồn; git diff --cached --check PASS. Node kiểm cú pháp JavaScript và CSV roundtrip PASS. Tương tác trình duyệt, Colab/train, AI accuracy/latency, webcam và hardware NOT_RUN ở bản bước dữ liệu.
- Mã/dependency app/Colab/simulator của bản nháp trước đó được giữ riêng cục bộ feat/damaged-books-abc b46faf8, chưa xuất bản/chấp nhận, không gộp vào nhánh dataset. Môi trường AI thử nằm riêng và chưa dùng để nghiệm thu; collector cũ không bị thay. Nhánh bàn giao chỉ chứa13 tệp mã/test/docs của bước dữ liệu.
- Commit nguồn10b5a22f73c3d4202b1a21b3d2315e5ed131cbb9 đã push; ls-remote xác nhận đúng SHA, base bdf0c00/main d431f10 không đổi. GitHub REST xác nhận PR #11 OPEN, merged=false, base feat/vietnamese-capture-ui: https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/11 . CI nguồn đang chạy ở lần đọc đầu, không suy PASS từ local.
- Cập nhật PROGRESS bằng mục mới, giữ toàn bộ sửa có sẵn và lịch sử. Còn620 nhãn pending,618 ảnh chưa nhóm và51 ứng viên âm pending. Đúng một việc tiếp theo: mở review.html, rà nhóm/nhãn rồi lưu review.csv. Chưa chuyển sang Colab hoặc app.

- Xác minh cuối: GitHub Actions run42758217749 của commit nguồn10b5a22 completed/success. Main/base vẫn giữ nguyên; metadata bàn giao không được tự gán kết quả CI nguồn. git diff --check checkout chính PASS, chỉ hai hồ sơ và dữ liệu giải nén sẵn có được báo thay đổi.

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

## 2026-11-11T19:22:38.9428063+07:00 — Colab handoff

## Cập nhật 2026-11-11 — notebook Colab YOLO11n

Đã tạo notebook độc lập `notebooks/damaged_books_colab.ipynb` và hướng dẫn `docs/COLAB_TRAINING.md` trên nhánh `feat/damaged-books-colab`, worktree `data/local/worktrees/damaged-books-colab`. Nhánh mới dựa trên commit e75eed1; giữ nguyên bốn hồ sơ chưa commit của Gemini trên worktree dataset.

Đối chiếu trực tiếp split-reviewed-v1.zip: SHA256 0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1;253/54/54 ảnh,83/18/20 nhóm,đủ5 lớp;checksum từng tệp và không giao nhau ID/nhóm/nội dung ảnh PASS. Việc này xác minh cấu trúc split, không rà độc lập lại nhận định nhãn/nhóm của Gemini.

Notebook train từ yolo11n.pt,640px,100 epoch,patience20,batch16,seed42; ghim Ultralytics8.4.208 (đã xác minh PyPI). Lưu checkpoint Drive, best.pt, cấu hình thực tế, phiên bản thư viện, báo cáo validation/confusion và ZIP. YAML chạy chỉ chứa train/val; threshold chưa chọn, test chưa đánh giá. Không triển khai ứng dụng AI.

Kiểm chứng: mã các ô compile PASS; kiểm tra gói thật PASS;6 test cổng dữ liệu PASS. Lần test đầu có lỗi fixture dùng chung list lớp, đã sửa fixture và chạy lại PASS. Chưa chạy GPU Colab, chưa có model đã train, chưa có chất lượng AI hoặc độ trễ camera.

**Một việc tiếp theo:** người dùng mở notebook trên Colab, bật GPU, tải split-reviewed-v1.zip và chạy từng ô. A02/H08 còn chờ phiên GPU thật, không đánh DONE từ notebook.

Kiểm chứng cuối phiên Colab:108 tests PASS (28.187s), check_repository PASS, check_codex_state PASS, diff --check PASS. Ultralytics8.4.208 có trên PyPI; API Metric.ap đã kiểm trên môi trường AI riêng. Không cài thêm vào collector. GPU Colab/train thật NOT_RUN.


## 2026-11-11T21:13:02.8620848+07:00 — GitHub team training publication

## Cập nhật 2026-11-11 — đồng bộ GitHub cho team train song song

Đã push hồ sơ rà nhãn/nhóm còn thiếu của Gemini lên feat/damaged-books-dataset (cbe14bb), hợp nhất lịch sử vào feat/damaged-books-colab và push công cụ team (b310c53). Không merge PR vào main. Giữ bản nháp ứng dụng chưa nghiệm thu ngoài gói train và giữ dữ liệu nguồn tại máy.

Notebook tải split-reviewed-v1.zip từ GitHub Releases, kiểm SHA256 và hỗ trợ n640/s640/n960 với cùng seed42. Mỗi lượt ghi TEAM_MEMBER, EXPERIMENT, GPU, model/dataset hash, cấu hình thực tế và experiment-summary.csv. Tất cả so sánh trên validation; test chỉ đánh giá cuối. Phiên n960 chỉ thay kích thước đầu vào của ảnh nguồn640px.

Dataset361 ảnh và manifest/attribution/SHA256SUMS đã phát hành: https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/releases/tag/damaged-books-reviewed-v1 . Tải công khai ZIP12693288 byte và đối chiếu SHA256 PASS; notebook remote khớp blob commit và JSON local PASS. 111 test PASS (38.097s);check_repository/check_codex_state/diff PASS. GPU train NOT_RUN; chưa có model thắng hoặc nghiệm thu camera.

**Một việc tiếp theo:** team mở notebook trên nhánh feat/damaged-books-colab, chọn TEAM_MEMBER và chia n640/s640/n960, chạy bằng GPU riêng rồi gửi ZIP và experiment-summary.csv để so sánh. H08/A02 còn chờ phiên GPU thật. Xem docs/TEAM_TRAINING.md và docs/COLAB_TRAINING.md trên nhánh Colab.

## 2026-11-11T21:35:00+07:00 — Phân tích kết quả huấn luyện YOLO11n lần 1 (`20261111T132200647414Z`) và đề xuất kế hoạch lần 2

- Yêu cầu: giải nén và phân tích toàn diện gói kết quả Colab `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip`, xác định nguyên nhân mô hình phát hiện 4 lớp lỗi kém, và đề xuất kế hoạch lần 2 (không train lại, không đánh giá `test`, không sửa nhãn nguồn).
- Đã giải nén vào `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts` (54 tệp, 3 thư mục con); xác nhận `git check-ignore -v` khớp `.gitignore:21:/data/*`, giữ nguyên ZIP gốc (SHA256 `b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866`).
- Đã đọc toàn bộ tệp cấu hình/số liệu (`environment.json`, `initial-weights.json`, `model-metadata.json`, `requested-config.json`, `requirements-frozen.txt`, `split-check.json`, `train-val.yaml`, `training-status.json`, `validation-metrics.json`, `train/args.yaml`, `train/results.csv`) và xem trực tiếp toàn bộ đồ thị/ảnh (`train/results.png`, `train/labels.jpg`, `validation/confusion_matrix*.png`, `validation/Box*_curve.png`, `validation/val_batch0..2_labels.jpg`, `validation/val_batch0..2_pred.jpg`, `train/train_batch0.jpg`, `train/train_batch1440.jpg`, cùng 5 ảnh kiểm tra cặp `dHash <= 10`).
- Đã tạo script phân tích tái lập `scripts/analyze_colab_run.py` và báo cáo `docs/COLAB_RUN1_ANALYSIS.md`.
- Kết quả chính có bằng chứng:
  1. `optimizer='AdamW'` đặt tường minh nhưng không truyền `lr0` làm Ultralytics `8.4.208` dùng `lr0=0.01` (gấp ~9 lần mức `0,001111` của `auto`), gây `val_loss = NaN` ở epochs `1..8`, `10` và `val/cls_loss = 587,034` ở epoch `9`. Mô hình đạt đỉnh `mAP50 = 17,44%` ở epoch `82`, đỉnh `fitness (mAP50-95) = 9,85%` ở epoch `97` (`best.pt`), và đã plateau ở 18 epoch cuối.
  2. Điểm `Precision = 100%, Recall = 0%` của `Notch`, `Spot`, `Wornout` là hệ quả của việc chấm tại ngưỡng chung `conf = 0.350` (theo đỉnh F1 của `Barcode`), nơi 3 lớp này có `0` dự đoán (`conf` cực đại lần lượt `< 0.055`, `< 0.215`, `< 0.320`).
  3. Tại `imgsz=640`, `73,85%` hộp `Spot` (trung vị `24×20 px`), `49,06%` hộp `Notch` và `46,21%` hộp `Wornout` trên `val` nhỏ hơn `32×32 px`, bị `erasing=0.4` và `mosaic=1.0` (`scale=0.5`) làm suy giảm mạnh.
  4. Đối chiếu ảnh `val_batch0..2` và Confusion Matrix cho thấy `30,8%` `Ripped` bị đoán nhầm sang `Wornout`, nhãn giữa các ảnh của cùng cuốn sách không nhất quán (`test__IMG_7` vs `train__IMG_1316`, `IMG_1490` vs `IMG_1534`), có `37` hộp `train` và `12` hộp `val` dẹt `> 10:1` (tới `40,5:1`), 4 ảnh `val` thiếu nhãn mã vạch ISBN làm phạt oan FP, và 3 nhóm sách chiếm `56,88%` tổng số hộp `val`. Giữa `train` và `val` không có rò rỉ nhóm hay ảnh trùng (`SHA256` và kiểm tra trực quan `dHash`).
- Đúng một việc tiếp theo: kiểm chứng giả thuyết G1 trên Colab (`30–50` epochs với `lr0=0.001`, `cos_lr=True`, `erasing=0.0`, `auto_augment=None`, `scale=0.25`) và quyết định phương án gộp lớp lỗi / tách `Barcode` trước khi chạy huấn luyện chính thức lần 2.

## 2026-11-11T21:38:23+07:00 — Đối chiếu độc lập run1 và tiếp tục sau xác nhận phối hợp

- Người dùng xác nhận tiếp tục, giữ nguyên thay đổi của Antigravity; chỉ hoàn thiện báo cáo và tiến độ của phần phân tích độc lập. Đã đọc lại trạng thái Git, PROGRESS và cuối nhật ký trước khi bổ sung; không sửa `scripts/README.md`, `scripts/analyze_colab_run.py`, `docs/COLAB_RUN1_ANALYSIS.md` hoặc nội dung lịch sử của tác giả khác.
- Tạo `scripts/analyze_damaged_books_run.py`, `docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md`, `docs/DAMAGED_BOOKS_RUN1_TABLES.md`; cập nhật đầu PROGRESS. Giải nén riêng54 tệp vào `data/local/damaged_books_v1/codex-analysis-20261111/artifacts`; danh sách ở `inventory.txt`, kết quả đầy đủ ở `analysis.json` cùng thư mục cha. ZIP nguồn SHA256 `b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866` không đổi, `git check-ignore -v` PASS qua `.gitignore:21:/data/*`.
- Script đọc trực tiếp nhãn253train/54val, kiểm614 hash với manifest, bảng lớp, ảnh/nhãn tương ứng, box bất thường, ảnh âm, phân vị chuẩn hóa/pixel, giao nhóm/hash/pixel và pHash13.662 cặp. PASS về cấu trúc/hash;0 ứng viên pHash Hamming≤8 chỉ là sàng lọc, không thay kiểm nhóm khác góc. Không mở ảnh/nhãn test. Chạy lại cho kết quả JSON và bảng trùng nội dung, không ghi đè artifacts.
- Đã mở `validation/val_batch0/1/2_labels.jpg` và `_pred.jpg`, sáu đồ thị validation, `train/results.png`, `train/train_batch0.jpg`, cùng ảnh gốc val IMG_1174/1359/1446/1201/1129/1736. Bằng chứng và quan sát cụ thể có trong báo cáo; chưa rà trực quan toàn bộtrain hoặc6ảnhval cuối.
- Kết luận: AP50 macro riêng lỗi3,209%, recall macro lỗi0,641%; val loss NaN ởepoch1–8,10 và cls587,034 tại9. LR cao/AMP chỉ là giả thuyết, chưa thể nói chắc gâyNaN. Phân vị cạnh ngắnval Spot/Wornout18px; xác nhận thiếu nhãn Barcode ởIMG_1174/1359; các lớp Spot/Wornout còn nghi vấn cần rà, không tự sửa nhãn.
- Đối chiếu mã Ultralytics8.4.208: detection gọi `v8_transforms`, không đọc `erasing`/`auto_augment` (classification mới dùng). P=1/R=0 được giải thích bằng nội suy `left=1` và ngưỡng F1 chung; không diễn giải là độ chính xác100% hay phép chia0/0 trực tiếp. Confusion matrix và ảnhpred khác ngưỡng; không lấy số ma trận áp cho confidence0.35. Bổ sung này giữ nguyên mục phân tích trước để bảo toàn lịch sử.
- Lệnh đã chạy: `git status --short`; `git check-ignore -v data/local/damaged_books_v1/codex-analysis-20261111/artifacts`; môi trường `.venv-ai` chạy `scripts/analyze_damaged_books_run.py --archive data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip --dataset data/local/damaged_books_v1/split-reviewed-v1 --output data/local/damaged_books_v1/codex-analysis-20261111 --tables docs/DAMAGED_BOOKS_RUN1_TABLES.md`; `.venv/Scripts/python.exe scripts/check_repository.py`; `git diff --check`. Phân tích tái lập, checker và diff PASS; chưa train lại/inference/test/camera/hardware. Cấu hình, giả thuyết, phép thử rẻ nhất và kế hoạchv2 được lưu trong báo cáo, chưa thực hiện.
- Git vẫn ởmain với thay đổi có sẵn và các tệp phân tích của hai bên; không stage/commit/push/merge, không đưa ZIP/ảnh/weights vàoGit. Dữ liệu untracked nguồn tại root được giữ nguyên.
- Đúng một việc tiếp theo ưu tiên của bản đối chiếu: hai người audit chung20 ảnh train/val, chốt quy tắc và danh sách sửa ở phiên bản dữ liệu mới trước pilot train lần2. Chưa thay đổi hợp đồng5 lớp hay triển khai ứng dụng.

## 2026-11-11T21:43:14+07:00 — Đối chiếu bản bàn giao Antigravity theo yêu cầu bổ sung

- Đã đọc bản người dùng gửi và báo cáo/script Antigravity; bổ sung mục đối chiếu trong `docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md`, cập nhật mục hiện tại của PROGRESS. Không sửa tệp của Antigravity.
- Gọi `analyze_dataset_split` của `scripts/analyze_colab_run.py` trong môi trườngAI và so vớiJSON của script độc lập: PASS về ảnh/instance từng lớp, sốboxdiện tích<1024px². Đếm trực tiếp nhãn/manifest xác nhận37boxtrain/12boxval cóaspect>10 và3nhómval chiếm186/327box (56,88%).
- Các điểm cần sửa trong bản Antigravity: erasing/randaugment không nằm trongpipeline detectionchuẩn; LR→NaN/pretrainedhỏng chưa có đối chứng; mAPkhông phải metric tại mộtconf0.35; đề xuấtcrop630×888/hai lớp cũ không khớp yêu cầuROI gốc/năm lớp/A-B-C; thay quá nhiều tham số không xác định nguyên nhân.
- dHash scriptAntigravity tái lập5cặp khác danh sách3cặp trongbáo cáo. Đã mở7ảnh gốc thêm để đối chiếu vớiảnhIMG_1736đã xem; ghi rõ giới hạn ảnhcrop và danh tính cuốn, không khẳng định không có rò rỉ từhash. Bảng ứng viên, môi trường và quan sát được lưu trongbáo cáo; không sửa nhãn.
- Chạy lại `scripts/analyze_damaged_books_run.py` với cùngarchive/dataset/output/tables PASS sau khi bổ sungassert bảnglớp/versionmetadata; logcục bộ `data/local/damaged_books_v1/codex-analysis-20261111/final-validation.log`. Khôngtrain/inference/test. Bước tiếp theo vẫn audit20ảnh và chốt quy tắc trước pilot cóđối chứng.

## 2026-11-11T22:18:00+07:00 — Đồng bộ báo cáo phân tích lần 1 và chuẩn bị bảng rà chung 20 ảnh (`12 val + 8 train`)

- Yêu cầu: sửa các điểm sai lệch trong kế hoạch và báo cáo theo phản hồi đối chiếu, sinh lại danh sách 20 ảnh từ `split_manifest.json` và tệp nhãn `.txt` thực tế (dùng đúng `relative_path` và `group_id`), mở xem trực tiếp từng ảnh trước khi ghi quan sát, cập nhật báo cáo và chuẩn bị bảng rà (chưa train, chưa sửa nhãn nguồn, chưa gộp lớp). Giữ nguyên toàn bộ tệp của Codex Astra 6 (`docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md`, `docs/DAMAGED_BOOKS_RUN1_TABLES.md`, `scripts/analyze_damaged_books_run.py`).
- Đã mở xem trực tiếp toàn bộ 20 ảnh gốc `.jpg` trong danh sách rà chung (`12 val + 8 train`) cùng 20 tệp nhãn `.txt` tương ứng và 7 ảnh gốc bổ sung của 5 cặp ứng viên `dHash <= 10`.
- Cập nhật `scripts/analyze_colab_run.py` để kiểm chứng tự động danh sách 20 ảnh với `split_manifest.json` và nhãn `.txt` (`audit_20_manifest_verified = true`), bổ sung phân rã `extreme_aspect_gt_10_by_class` (`train`: `37` hộp gồm `25 Wornout, 10 Notch, 2 Ripped`; `val`: `12` hộp gồm `11 Wornout, 1 Ripped`), tỷ trọng 3 nhóm sách lớn nhất ở `val` (`17/54` ảnh = `31,48%`, `186/327` hộp = `56,88%`) và phiên bản `opencv_version`. Chạy lại `.venv\Scripts\python.exe scripts/analyze_colab_run.py --output-json data/local/damaged_books_v1/colab-results/run1-analysis.json` PASS.
- Cập nhật `docs/COLAB_RUN1_ANALYSIS.md` và kế hoạch thực hiện:
  1. Bảng rà 20 ảnh (`12 val + 8 train`) ghi đúng `relative_path`, `group_id`, số hộp từng lớp theo nhãn thực tế và quan sát trực quan sau khi mở ảnh (ví dụ `IMG_1174` thuộc `visual_group_087` có `3` hộp `2 Notch, 1 Wornout`; `IMG_1359` thuộc `visual_group_076` có `0` hộp / nhãn rỗng). Ghi rõ rà 20 ảnh để chốt quy tắc 1 trang, chưa chứng minh toàn bộ nhãn còn lại đã sạch.
  2. Chuẩn hóa số liệu: `Notch` có `250` hộp `train` (`97` ảnh, `45` nhóm) / `53` hộp `val` (`22` ảnh, `10` nhóm); 3 nhóm lớn nhất ở `val` chiếm `17/54` ảnh và `186/327` hộp; giao nhau nhóm `train`/`val` bằng `0`; 3 lớp có `Recall = 0,000%` tại ngưỡng tổng hợp là `Notch`, `Spot`, `Wornout`, còn `Ripped` có `Recall = 2,564%` (`1/39`).
  3. Ghi rõ `erasing=0.4` và `auto_augment=randaugment` không hoạt động trong `v8_transforms` của detection Ultralytics `8.4.208`; tách bạch bằng chứng `NaN`/spike với giả thuyết `lr0=0.01`/`amp=True` trên `AdamW`; bám sát hợp đồng `D20–D24` (ROI sách gốc + lề 5%, 5 lớp, `Ripped` luôn ưu tiên Khay A); tách các lượt thử **đơn biến** khỏi **nhóm cấu hình** và quy định chấm lại trên cùng bộ `val v2` khi so sánh các model.
- Kiểm chứng: `.venv\Scripts\python.exe scripts/check_repository.py` PASS; `git diff --check` PASS. Không train lại, không đụng `test`, không sửa nhãn nguồn, không gộp lớp.
- Đúng một việc tiếp theo: hai bên duyệt bảng rà 20 ảnh tại Mục 6 của `docs/COLAB_RUN1_ANALYSIS.md` để chốt quy tắc nhãn 1 trang trước khi tạo `split-reviewed-v2` hoặc chạy `Pilot 2A-1`.

## 2026-11-11T22:58:19+07:00 — Rà độc lập20 ảnh và lưu đề xuất nhãn riêng

- Người dùng yêu cầu thực hiện kế hoạch đã duyệt, giới hạn20 ảnh; đã đọc AGENTS/README/PROGRESS/nhật ký/PLAN/DECISIONS và trạng thái Git, giữ các thay đổi đồng thời. D20–D24 tham chiếu nhánh Colab; thêm D25 quy tắc rà ở checkout chính, không đổi collector legacy.
- Đã xem ảnh gốc và overlay20 ảnh, ghi đầy đủ từng dòng nguồn trong `docs/reviews/damaged_books_review20.json`: dataset version/manifest hash, ảnh/nhãn hash, split/group, kích thước, sốbox, quan sát, lý do, câu hỏi. Không dùng model prediction làm đáp án.32 thao tác sửa được đề xuất;71 hộp giữ,86 hộp chưa rõ.17/20 ảnh có câu hỏi,9 ảnh ưu tiên phân biệt rách. Không ép nhãn sạch cho ảnh rỗng; có4 đề xuất bổ sung barcode bị sót.
- Tạo `scripts/build_damaged_books_review20.py`, `docs/DAMAGED_BOOKS_ANNOTATION_RULES.md`, `tests/test_damaged_books_review20.py`; sinh `data/local/damaged_books_v1/run2-review20/review.html`, `review-summary.csv`, `proposals.json`. JSON before/after truy vết tới dòng nhãn gốc, proposal chưa phê duyệt; không xuất labeltrainable. Generator từ chối nguồn đổi/sai tọa độ/sót hộp; từ chối ghi đè đầu ra bị sửa tay.
- Sửa hẹp `docs/COLAB_RUN1_ANALYSIS.md`: bỏ cấm mọi hộp lồng, giải thích audit field là list, cảnh báo pilot15 epoch đổi lịchLR/mosaic và #20 âm chưa xác định. Thêm quy tắc D25 ở DECISIONS và cập nhật PLAN; không sửa scripts/README, analyze_colab_run hoặc ba tệp phân tích độc lập trước đó.
- Lệnh: `.venv/Scripts/python.exe scripts/build_damaged_books_review20.py` và `--check` PASS; `.venv/Scripts/python.exe -m unittest discover -s tests -p test_damaged_books_review20.py -v` PASS7/7; `.venv/Scripts/python.exe scripts/check_repository.py` PASS25 nguồn; `git diff --check` PASS (chỉ cảnh báoCRLF). `git check-ignore -v` xác nhận đầu ra qua `.gitignore:21:/data/*`.
- Node `verify_review_ui.mjs` kiểm20 thẻ/60 ảnh, UTF8, các bộ lọc20/9/17/3/0 và phóng to PASS. `verify_browser.mjs` chạy Edge headless/CDP:20 thẻ60 ảnh, bộ lọc thật20/9/17/3, phóng to PASS; xem `browser-utf8.png`, `browser-image14-cdp.png`, `browser-image20-cdp.png`. CUA kernel lỗi sandbox refresh nên không dùng bằng chứng tương tác Windows thông thường. Screenshot headless đầu phát hiện ghi chú mất dấu do PowerShell stdin encoding; đã phục hồi UTF8 và kiểm lại. Screenshot dùng fragment đầu tiên rỗng do thời điểm render; CDP đợi tải/paint rồi chụp lại PASS, không lấy ảnh rỗng làm bằng chứng.
- `validation.json`:617 checksum (614 ảnh/nhãntrain-val + manifest/data.yaml/CSVduyệt cũ) không đổi; ZIPartifacts SHA256 b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866 không đổi. Checksum các tệp phân tích khác giữ nguyên ngoại trừ báo cáo được sửa hẹp theo kế hoạch. Trường xác minh script không đại diện operatorapproval hoặc chất lượngAI.
- Chưa train/inference/test/camera/hardware, chưa v2 hoặc rà rộng. Không stage/commit/push/merge. Git còn sửa có sẵn và untracked dataset ở root; không dùng git add. Cập nhật PROGRESS theo kết quả thật.
- Đúng một việc tiếp theo: xem bộ lọc câu hỏi A/B và xử lý9 ảnh ưu tiên; ảnh không đủ rõ giữneeds_review hoặc cần ảnh cận/góc khác, không tự duyệt âm.

## 2026-11-12T14:44:58+07:00 — Tạo file test độc lập ESP32/BTS7960, không upload

- Yêu cầu hiện tại ưu tiên: một file nguồn riêng cho ESP32 thường 38 chân, không sửa firmware chính, không tự nạp. Đã đối chiếu README/PROGRESS/nhật ký/PLAN/DECISIONS, Git và mã thực tế; project hiện nằm ở `firmware/esp32`, khác đường dẫn `firmware/esp32-test` trong ghi chú lịch sử. Giữ toàn bộ thay đổi Git có sẵn; không stage/commit/push.
- Tạo `firmware/manual-tests/bts7960_button_ramp.cpp`: RPWM GPIO18, LPWM nối GND, nút NO GPIO23 xuống GND/PULLUP; giữ VCC/R_EN/L_EN 3V3 theo cấu hình người dùng cung cấp, chưa xác minh điện trên module thật. PWM khởi tạo 0, đảo đích 0/100% theo mỗi cạnh nhấn đã lọc 35 ms. Mỗi đích mới ramp 2 giây từ duty hiện tại; không nhảy mức khi đảo giữa ramp, không gọi delay, giữ nút không lặp, xử lý unsigned millis wrap. PWM 20 kHz/10 bit; API core2/core3 tách bằng version macro.
- Lệnh `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project>` PASS: Espressif32 8.0.0 / Arduino-ESP32 3.3.12 / esp32dev; 32,86 giây; RAM22344 B, flash301991 B. Không chạy target upload/monitor, không mở cổng serial. Core2 chưa build; hành vi nút và động cơ chưa kiểm trên thiết bị.
- SHA256 main.cpp gốc `3807e1458d840c390da18bd385ad8623da514bf923311cc42ba6ce7c85a6322d`, platformio.ini gốc `0561ad57631b44c7346b16126738eef9cbc13b464869553865e34a450f6f2bc7` khớp trước/sau; `git diff --check` PASS, chỉ cảnh báo chuẩn hóa CRLF của các hồ sơ đã có. Chỉ thêm một tệp nguồn test và cập nhật hai hồ sơ tiến độ/nhật ký; không đổi PLAN/DECISIONS cho thử nghiệm tách rời này.
- Shell/Node mặc định lỗi `helper_unknown_error: setup refresh had errors`; chuyển sang exec ngoài sandbox được bộ duyệt tự động cho phép để đọc/build. Không có bằng chứng phần cứng, không đánh DONE-HW hoặc hoàn tất mốc chính.
- Đúng một việc tiếp theo: người dùng nạp thủ công bằng project PlatformIO mới trong VS Code và thử các thao tác nút; xem log115200, đối chiếu PWM/motor thực tế. Hướng dẫn thao tác có trong đầu tệp test; PROGRESS ghi trạng thái và giới hạn bằng chứng.

## 2026-11-12T14:50:02+07:00 — Nạp test BTS7960 theo yêu cầu mới, Serial READY

- Người dùng chủ động yêu cầu nạp luôn, thay giới hạn không tự nạp ở lượt tạo file. Kiểm tra lại Git/hồ sơ, hash nguồn test và cấu hình gốc; giữ mọi thay đổi có sẵn. Không sửa mã nguồn test hay firmware chính.
- `~/.platformio/penv/Scripts/platformio.exe device list`: COM5 CP210x là cổng USB; các COM khác là Bluetooth. Không thấy monitor riêng giữ cổng. Mã nguồn bản build tạm khớp tệp test (SHA256 ceadabb5b13f78b07ec41f4eb82b01995d2c6a63d52df3d98f5fa7d09c463172).
- Chạy `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project> -t upload --upload-port COM5`: PASS/SUCCESS9,58 giây. Nhận chip ESP32-D0WD-V3 revision3.1; flash và xác minh hash bốn vùng bootloader/partitions/boot_app0/application; hard reset hoàn tất.
- Đọc Serial COM5/115200 bằng pyserial, reset ngắn qua RTS và không gửi lệnh chạy; nhận `[READY] PWM=0. Press/release GPIO23 button to toggle 2 s ramp.`. Lưu log gốc `data/local/bts7960-upload-20261112/serial-startup.log`; đóng cổng sau kiểm tra. Không điều khiển nút hoặc thử chạy động cơ từ máy tính.
- SHA256 main.cpp/chương trình chính vẫn3807e1458d840c390da18bd385ad8623da514bf923311cc42ba6ce7c85a6322d; platformio.ini vẫn0561ad57631b44c7346b16126738eef9cbc13b464869553865e34a450f6f2bc7. Chỉ cập nhật PROGRESS/SESSION_LOG và log cục bộ; không đổi PLAN/DECISIONS, không commit/push.
- Firmware upload và Serial startup PASS; kiểm chứng nút/PWM đo thực tế/motor NOT_RUN. Đúng một việc tiếp theo: người dùng thử thao tác nút và quan sát tăng/giảm, nhấn giữa ramp, giữ nút; chưa đánh DONE cho mốc phần cứng.

## 2026-11-13T09:38:00+07:00 — Nâng cấp test độc lập ESP32: thêm cảm biến hồng ngoại vật cản 3 chân và Servo MG995

- Yêu cầu trực tiếp của người dùng: đấu thêm cảm biến hồng ngoại vật cản 3 chân và Servo MG995 3 chân; nâng cấp code để khi bấm nút thì băng tải chạy, bấm lần nữa thì tắt như cũ, nhưng khi đang chạy mà cảm biến nhận vật cản thì băng tải dừng, servo gạt 180 độ, khi servo gạt xong thì băng chuyền chạy tiếp.
- Cập nhật `firmware/manual-tests/bts7960_button_ramp.cpp` (SHA256 mới `c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc`; bản 2026-11-12 trước đó có SHA256 `ceadabb5b13f78b07ec41f4eb82b01995d2c6a63d52df3d98f5fa7d09c463172`):
  - Giữ `RPWM_PIN = 18` (`20 kHz`, `10 bit`), `BUTTON_PIN = 23` (`INPUT_PULLUP`, chống dội `35 ms`).
  - Thêm `IR_SENSOR_PIN = 19` (`INPUT_PULLUP`, `IR_ACTIVE_LEVEL = LOW`, lọc `30 ms`, khóa `irArmed` cho tới khi vật rời cảm biến).
  - Thêm `SERVO_PIN = 22` cho Servo MG995 dùng LEDC `50 Hz`, `14 bit` (`500..2400 us`), tách kênh/timer riêng ở core 2.x (`SERVO_PWM_CHANNEL = 2`) và hỗ trợ core 3.x, không cần thư viện ngoài.
  - Chu trình state machine không dùng `delay()`: phát hiện vật cản khi `requestedOn == true` -> dừng ngay băng tải (`PWM = 0`) -> Servo quay `180°` trong `700 ms` -> thu về `0°` trong `700 ms` -> băng tải tự ramp `0 -> 1023` trong `2.000 ms`. Hỗ trợ hủy chu trình và đưa servo về `0°` nếu bấm nút tắt giữa chừng.
- Không sửa `firmware/esp32/src/main.cpp` (SHA256 `3807e1458d840c390da18bd385ad8623da514bf923311cc42ba6ce7c85a6322d`) hay `firmware/esp32/platformio.ini` (SHA256 `0561ad57631b44c7346b16126738eef9cbc13b464869553865e34a450f6f2bc7`).
- Kiểm chứng: `data\local\python311\python.exe scripts/check_repository.py` PASS (25 nguồn Python); `git diff --check` PASS.
- Theo yêu cầu tiếp theo của người dùng ("nạp cho tôi luôn"), đã kiểm tra SHA256 bản sao nguồn tại `<temporary-project>/src/main.cpp` khớp `c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc` và chạy `~/.platformio/penv/Scripts/platformio.exe run --project-dir <temporary-project> -t upload --upload-port COM5`: **PASS / SUCCESS** (41,90 giây; RAM `22.360 B`, Flash `303.359 B`; `ESP32-D0WD-V3 revision v3.1` trên `COM5`; xác minh hash cả 4 vùng flash và hard reset qua RTS).
- Đúng một việc tiếp theo: người dùng kiểm tra đấu dây cảm biến hồng ngoại (`GPIO19`, nguồn `3V3`) và Servo MG995 (`GPIO22`, nguồn ngoài `5V–6V` chung `GND`), sau đó thử thực tế chu trình bấm nút chạy – gặp vật cản dừng băng tải – servo gạt 180° rồi về 0° – băng tải tự chạy tiếp. Thử nghiệm cơ khí thực tế hiện vẫn `NOT_RUN`.

## 2026-11-15T16:32:17+07:00 — Đối chiếu chức năng và chân nối ESP32

- Đọc README, PROGRESS, nhật ký, PLAN/DECISIONS và hai tệp C++; kiểm tra Git bằng `git status --short`, giữ các thay đổi có sẵn.
- `Get-FileHash firmware/manual-tests/bts7960_button_ramp.cpp` PASS: SHA256 `c16b2689956ebf01a485d82f83b25dd7fdcaf800a26c798fc0f8d7bd6eb6bdfc`, khớp nguồn được ghi đã nạp ngày 13/11. Firmware chính vẫn là mẫu cộng hai số, loop rỗng.
- Giải thích chân GPIO18/19/22/23, nguồn và chu trình theo nguồn hiện tại. Làm rõ PWM=0 là lệnh dừng; servo chỉ chờ 700 ms mỗi bước, chưa đo góc; băng tải tự chạy lại kể cả vật chưa rời cảm biến, nhưng không gạt lặp khi cảm biến bị che liên tục. Cảm biến bị che sẵn lúc bật cần được nhả rồi kích lại.
- Không sửa/nạp firmware, không mở Serial; build/upload/thiết bị trong phiên này NOT_RUN. Shell sandbox lỗi khởi tạo; các lệnh đọc ngoài sandbox được bộ duyệt tự động cho phép.
- Đúng một việc tiếp theo: người dùng thử chu trình nút → cảm biến → servo → băng tải và báo hành vi thực tế. Không thay trạng thái nghiệm thu phần cứng.

## 2026-11-15T16:41:01+07:00 — Chuẩn bị test nút với điện trở kéo lên ngoài

- Người dùng yêu cầu sửa và nạp ngay, mô tả GPIO23 được kéo lên 5V qua 10k. Đã giải thích cần chuyển đầu điện trở sang 3V3 vì GPIO ESP32 không chịu mức 5V; người dùng chưa hiểu/chưa xác nhận sửa dây. Chỉ chuẩn bị nguồn/build, chưa upload hoặc mở Serial.
- Sao lưu nguồn cũ tại `data/local/bts7960-button-only-20261115/before.cpp`. Sửa hẹp nguồn test: `BUTTON_ONLY_TEST=true`, nút INPUT ngoài 10k lên 3V3, nhấn bật ramp 2 s, nhấn tắt PWM=0; giữ debounce/khóa giữ nút, vô hiệu chu trình IR và PWM servo. Giữ firmware chính và các thay đổi có sẵn.
- `~/.platformio/penv/Scripts/platformio.exe device list`: COM5 CP210x. `~/.platformio/penv/Scripts/platformio.exe run --project-dir data/local/bts7960-button-only-20261115/pio`: PASS 33,03 s, Arduino-ESP32 3.3.12, RAM 22352 B, flash 302499 B. SHA256 nguồn `63d7660743be1e3f684af7bebfe11216beaa8888a388e61089656c70643f96da`.
- Build PASS; upload/Serial/nút/động cơ bản mới NOT_RUN. Đúng một việc tiếp theo: người dùng ngắt nguồn, chuyển đầu điện trở 5V sang 3V3 rồi nối USB; khi xác nhận thì tiếp tục nạp theo ủy quyền hiện tại.

## 2026-11-15T16:45:34+07:00 — Nạp bản test nút sau xác nhận đổi dây sang 3V3

- Người dùng xác nhận đã đổi dây; đối chiếu nguồn và bản build SHA256 `63d7660743be1e3f684af7bebfe11216beaa8888a388e61089656c70643f96da`, kiểm tra lại COM5 CP210x và trạng thái Git.
- `~/.platformio/penv/Scripts/platformio.exe run --project-dir data/local/bts7960-button-only-20261115/pio -t upload --upload-port COM5`: PASS/SUCCESS 9,81 s; ESP32-D0WD-V3 rev3.1, hash bốn vùng flash được xác minh, hard reset. Log: `data/local/bts7960-button-only-20261115/upload.log`.
- Đọc COM5/115200 bằng pyserial sau reset: `[READY] BUTTON_ONLY. PWM=0. GPIO23=HIGH (released), external 10k to 3V3. IR/servo disabled.`, rồi `[BUTTON] ON: ramp to 100% in 2000 ms.` và `[DONE] PWM=1023/1023`. Log: `data/local/bts7960-button-only-20261115/serial-startup.log`. Không gửi lệnh chạy động cơ; tín hiệu nhấn được firmware ghi nhận, chưa xác minh nguồn tín hiệu/thao tác nút vật lý hoặc chuyển động. Cổng Serial đã đóng.
- Upload/khởi động bản mới PASS; cơ khí và nhấn dừng chưa được xác nhận. Đúng một việc tiếp theo: người dùng bấm thêm lần nữa và kiểm tra băng tải dừng.

## 2026-11-15T17:12:10+07:00 — Thêm IR dừng băng tải và tự chạy sau 2 giây hết vật

- Người dùng báo test nút ổn; yêu cầu thêm và nạp ngay cảm biến OUT GPIO19. Giữ nút bật/tắt, ramp tăng 2 s và servo tắt; bổ sung ngắt PWM khi đọc LOW, yêu cầu HIGH liên tục 2000 ms trước khi bắt đầu ramp lại. Tái xuất hiện vật hủy thời gian chờ; nút OFF ngăn tự chạy; vật có sẵn lúc bật vẫn giữ dừng. Không dùng delay trong loop.
- Sao lưu bản nút vào `data/local/bts7960-ir-20261115/before.cpp`. SHA256 nguồn mới và bản sao build `c8e0d9b5d360c0d1e0522d827e30cf7aa3c8ea7d02b0783419d4594e5a73004c`. Giữ hash firmware chính/cấu hình; giữ các thay đổi Git có sẵn.
- `~/.platformio/penv/Scripts/platformio.exe run --project-dir data/local/bts7960-button-only-20261115/pio -t upload --upload-port COM5`: PASS 27,66 s, RAM 22360 B/flash 303175 B, Arduino-ESP32 3.3.12, ESP32-D0WD-V3 rev3.1; hash cả bốn vùng flash được xác minh. Project build tạm này hiện chứa bản IR. Log tại `data/local/bts7960-ir-20261115/build-upload.log`.
- Serial COM5/115200 sau reset: `[READY] BUTTON_IR. PWM=0. GPIO23=LOW (release before pressing). GPIO19=HIGH (clear). Clear wait=2000 ms. Servo disabled.` Lưu `data/local/bts7960-ir-20261115/serial-startup.log`, đóng Serial, không gửi lệnh chạy. Đã nhắc người dùng nhả nút rồi bấm lại; mức LOW lúc boot chưa xác định do giữ nút hay dây nối.
- Build/upload/khởi động PASS; chu trình IR/cơ khí thực tế NOT_RUN. Đúng một việc tiếp theo: nhả/bấm bật rồi che/bỏ vật để kiểm tra dừng và chờ 2 giây trước khi chạy tiếp.

## 2026-11-15T17:30:59+07:00 — Thêm servo MG995 và nạp COM5

- Người dùng xác nhận bản IR ổn; yêu cầu thêm servo gạt 180° rồi trở về và nạp. Sao lưu bản IR ở `data/local/bts7960-servo-20261115/before.cpp`. Sửa đúng file test, giữ firmware chính và thay đổi Git có sẵn.
- Tái dùng hàm PWM/góc và chu trình servo đã có: GPIO22 50 Hz/14 bit, 500–2400 us; kênh motor 0/servo 2. Trên core3 dùng ledcAttachChannel, core2 dùng ledcSetup/AttachPin. Đọc implementation core3.3.12 xác nhận chọn timer theo tần số/độ phân giải, khác tần số thì timer riêng. Chỉ build core3 trong phiên này.
- IR LOW khi ON ngắt PWM motor và gạt một lượt 180°/700 ms → 0°/700 ms; chỉ rearm sau IR HIGH liên tục 2 s và servo hết thời gian về. Nút OFF ngắt PWM ngay, hủy gạt, ra lệnh về 0°; bật lại trong thời gian về không cho motor chạy. Khởi động ra lệnh về 0°, hệ thống tắt. Không có cảm biến góc nên thời gian chờ không chứng minh vị trí thực.
- Lệnh `~/.platformio/penv/Scripts/platformio.exe run --project-dir data/local/bts7960-button-only-20261115/pio`: PASS 9,70 s. Cùng lệnh thêm `-t upload --upload-port COM5`: PASS 9,68 s, ESP32-D0WD-V3 rev3.1, hash bốn vùng flash xác minh; RAM 22368 B/flash 303587 B. SHA256 nguồn/bản build `5138b7c64814ce90f4c69c43265e4d95d4b24143ca81a77c32a99cfcf99661c4`.
- Serial COM5/115200: `[READY] BUTTON_IR_SERVO`, GPIO23 HIGH/released, GPIO19 HIGH/clear, servo home command 0°, chờ về kết thúc, clear confirmed và motor stays stopped vì nút OFF. Đã đóng cổng; không gửi lệnh bật motor. Bằng chứng `data/local/bts7960-servo-20261115/build-upload.log`, `serial-startup.log`. Hash main.cpp và platformio.ini chính giữ nguyên.
- Build/upload/boot PASS; servo và chu trình cơ khí NOT_RUN. Đúng một việc tiếp theo: người dùng bấm bật, đưa vật vào để thử dừng → gạt → về → hết vật đủ 2 giây thì chạy lại.

## 2026-11-18 — Phiên 1 — Đối chiếu bản ESP32 và chân cắm

- Đọc firmware/manual-tests/bts7960_button_ramp.cpp, firmware chính và cấu hình PlatformIO. Xác nhận bản test dùng GPIO18 RPWM, GPIO19 IR, GPIO22 MG995 và GPIO23 nút nhấn. Đấu dây và luồng xử lý được mô tả trong nguồn test.
- Get-FileHash SHA256 (PASS): nguồn test và bản sao dùng để build trùng hash 5138b7c64814ce90f4c69c43265e4d95d4b24143ca81a77c32a99cfcf99661c4 của bản nạp ghi ngày 15/11. Đối chiếu log upload và serial-startup tại data/local/bts7960-servo-20261115/ (PASS). Build, upload, Serial trực tiếp và cơ khí phiên này NOT_RUN.
- Đúng một việc tiếp theo: chạy thử một chu trình băng tải, IR và servo trên cơ cấu thật để xác nhận hành vi.

## 2026-11-18 — Phiên 2 — Triển khai trạm OK/NG một vị trí

- Theo lựa chọn của người dùng, giữ GPIO18/19/22/23, dùng MG996R hồi theo thời gian, HMI FastAPI trên Windows và kết nối WebSocket nội bộ. Thêm ghép mạng khi motor tắt, mã phiên/lượt, lưu ảnh và dữ liệu theo ca. Model cục bộ đã đối chiếu SHA256 với tệp được cung cấp. Để dành thao tác nạp board cho lần kết nối USB sau.
- `.venv-inspection/Scripts/python.exe -B -m unittest discover -s tests -v` chạy 42 test PASS. Đã sửa nhịp phát frame của fixture collector cho đồng hồ Windows Python 3.11. Test C++ trên PC dùng cùng header với ESP32 PASS. Edge thực hiện một lượt OK và reset ca PASS. Chế độ mô phỏng dùng cơ sở dữ liệu riêng.
- `platformio run --project-dir firmware/esp32` build PASS bằng espressif32 8.0.0, Arduino-ESP32 3.3.12. Không nạp firmware. Nguồn, hành trình, Wi-Fi tới board thật và khay thực chưa nghiệm thu. Marker COMPLETE ghi hoàn tất chu trình điều khiển.
- Chạy inference CPU với chính checkpoint trên một ảnh có sẵn, PASS. Driver DroidCam mở được ở 640×480. Lượt cuối phát hiện ảnh lặp, hệ thống giữ dừng. Accuracy trên sách tại băng tải N/A vì chưa có tập ảnh thật gán nhãn tại trạm. Log build, test, ảnh HMI mô phỏng và `pc-smoke.json` nằm trong `data/local/station/validation/`.
- Đúng một việc tiếp theo: kết nối điện thoại trong DroidCam Client và xác nhận ảnh động tại vị trí sách sẽ dừng.

## 2026-11-18 — Phiên 3 — Nạp firmware vận hành và xác nhận Wi-Fi cấu hình

- `platformio device list --json-output` tìm thấy Silicon Labs CP210x trên COM5. `platformio run --project-dir firmware/esp32 -e esp32dev -t upload --upload-port COM5` PASS trong 24,60 giây. esptool nhận ESP32-D0WD-V3 rev3.1, xác minh hash cả bốn vùng và reset qua RTS. Bằng chứng tại `data/local/station/validation/upload-COM5-20261118T112826Z.log`.
- `netsh wlan show networks mode=bssid` thấy SSID PBL5-Setup sau reset. Ghép LAN, điều khiển băng tải và servo thực tế NOT_RUN.
- Đúng một việc tiếp theo: dùng điện thoại kết nối PBL5-Setup và mở trang cấu hình ở `http://192.168.4.1`.

## 2026-11-18 — Phiên 4 — Kiểm tra LAN trước khi ghép mã

- netsh wlan show interfaces xác nhận PC ở BEAN HONG COFFEE - 2.4Ghz. Khởi chạy HMI thật và đọc /api/status thành công. Chưa có kết nối điều khiển đã ghép mã.
- Tên pbl5-sorter.local chưa phân giải. Không xác định được IP trạm qua COM5 khi đọc thụ động. WlanScan rồi netsh wlan show networks mode=bssid vẫn thấy PBL5-Setup khớp BSSID của board. Không gửi lệnh vận hành.
- Đúng một việc tiếp theo: kiểm tra phản hồi khi người dùng bấm lưu trang cấu hình trên điện thoại.

## 2026-11-19 — Hoàn tất ghép Wi-Fi và kiểm tra trạng thái trạm thật

- Kiểm tra lại log sau khi phiên bị ngắt. Bản bổ sung kéo lên nội GPIO23 và chẩn đoán khởi động đã nạp thành công qua COM5. Serial 115200 ghi `PBL5 boot: settings=found button=released` và `PBL5 IP: 192.168.5.91`. PC chuyển về Wi-Fi 2,4 GHz, đối chiếu IP/MAC rồi ghép mã cục bộ qua HMI.
- HMI nhận bản tin có mã phiên, trạng thái OFF, PWM=0. Kết nối thỉnh thoảng timeout. Đã tắt Wi-Fi modem sleep trên ESP32, giữ watchdog hiện có. `platformio run --project-dir firmware/esp32 -e esp32dev -t upload --upload-port COM5` PASS 50,30 giây, hash flash xác minh. Quan sát HMI sau lần nạp cuối trong 31,9 giây từ lần nhận bản tin đầu: 48/63 lần lấy mẫu có trạng thái board, cùng một phiên khởi động. HMI tự kết nối lại. Đã lưu bằng chứng ở `data/local/station/validation/pair-check.json`.
- DroidCam Client đang chạy, HMI báo khung hình lặp. Chưa gửi lệnh chạy cơ cấu. Đúng một việc tiếp theo: kết nối DroidCam trên điện thoại và thử hình động trước khi hiệu chỉnh.

## 2026-11-19 — Phiên 2 — Xác nhận hình camera tại HMI

- Người dùng xác nhận camera hoạt động, ESP32 chưa đấu hệ thống thật. Đọc `GET /api/status` và `GET /api/live.jpg` ba lần trên HMI đang chạy: hardware, HTTP 200 và ba hash JPEG khác nhau. HMI báo cần lưu ảnh băng tải trống. Chưa lưu nền, chưa thử AI trên sách và chưa điều khiển cơ cấu trong lượt này.
- Đúng một việc tiếp theo: cố định camera trước vùng đặt sách trống rồi lưu nền trong HMI.

## 2026-11-19 14:08 +07:00 — Giải thích cảnh báo nút vật lý

- Đọc `GET /api/status` hai lần. ESP32 báo `phase=OFF`, `pwm=0`. HMI báo DroidCam lặp khung hình. `Runtime.require_idle()` dùng chung câu cảnh báo khi PC bận, có lượt sách hoặc trạng thái trạm khác OFF/FAULT. Chưa xác định nhánh nào đã phát cảnh báo trước đó.
- Chờ người dùng đưa tay qua trước điện thoại và quan sát hình trên HMI. Thử băng tải và servo thật vẫn ở trạng thái `NOT_RUN`.

## 2026-11-19 14:51 +07:00 — Màn hình thử DroidCam và mô hình trên PC

- Thêm `--camera-test` và [TestCameraAI.cmd](../scripts/windows/TestCameraAI.cmd). Mỗi lần bấm chụp dùng một khung camera, giữ trọn khung khi đưa vào bộ phân loại 448 px, trả nhãn và hiển thị ảnh gốc. Chế độ này khởi tạo camera riêng và không khởi tạo controller hoặc cơ sở dữ liệu trạm.
- `.venv-inspection/Scripts/python.exe -m unittest discover -s tests -p "test_station*.py"` đạt 15/15. `node --check software/web/static/camera.js` đạt. SHA-256 của weights cục bộ khớp tệp người dùng cung cấp. Dùng ảnh từ `test/images` thay cho khung camera trong TestClient và gọi `POST /api/capture` với mô hình thật, nhận OK (0,9990) cùng JPEG 640×640. Đây là kết quả chạy một ảnh tệp, chưa đo độ chính xác.
- Đã chuyển HMI trên 127.0.0.1:8765 sang `camera-test`. Lúc kiểm tra, bốn lần đọc preview và một lần chụp trực tiếp trả 409 do khung hình lặp. Kết nối TCP đến địa chỉ và cổng điện thoại đã cấu hình hết thời gian chờ. Chờ người dùng mở DroidCam trên điện thoại và nối lại đúng IP trong client để thử một cuốn sách.

## 2026-11-19 14:59 +07:00 — Trang băng tải cũ và camera trực tiếp

- Ảnh người dùng gửi hiện trang giám sát cũ. Sửa JS của trang trạm để chuyển khi API trả `camera-test`. Trình mở camera dùng URL riêng theo chế độ. Đã chạy TestCameraAI.cmd, kiểm tra HTML HTTP 200 có nút chụp, kiểm tra JS bằng Node với trạng thái camera-test.
- Ba lần đọc `GET /api/live.jpg` cho ba JPEG khác nhau. `POST /api/capture` trả 200, JPEG và dự đoán OK (0,996). Chưa có nhãn thực cho ảnh camera. Bước tiếp theo là thử một bìa sách đã biết tình trạng.

## 2026-11-19 15:13 +07:00 — Đổi mô hình thử DroidCam

- Mục `camera_test_model` dùng `weights/best (1).pt` với ba nhãn gốc và ảnh 640 px. Cấu hình vận hành vẫn dùng `weights/best.pt` 448 px. Tên lớp đi kèm kết quả OK/NG cho mỗi lượt chụp thủ công.
- `.venv-inspection/Scripts/python.exe -m unittest discover -s tests -p "test_station*.py"` đạt 15/15. Sau khi khởi động lại dịch vụ, một lượt `POST /api/capture` từ DroidCam trả JPEG, `ok`, độ tin cậy 71,7% và SHA-256 khớp tệp nguồn (`2761f66e138b59af6180edc0e638ce1fb87768a75d5e3e5cf79a2b65641bdead`). Chưa đo độ chính xác trên sách có nhãn thực.

## 2026-11-19 15:29 +07:00 — Khôi phục best.pt và dọn dung lượng

- Gỡ cấu hình thử ba lớp và khởi động lại dịch vụ camera. Ảnh tệp qua FastAPI TestClient, bộ phân loại thật ở 448 px, trả OK, JPEG và SHA-256 `662e543e1d29538f799a444583682d9f80bce7ad7e5c5f0e4fb67aa42bf0c357`, khớp bản gốc. Lệnh `.venv-inspection/Scripts/python.exe -B -m unittest discover -s tests -p "test_station*.py"` đạt 15/15. Dịch vụ thật báo lặp khung hình khi thử camera.
- Tổng số byte của các tệp trong workspace lúc đo trước/sau lần lượt là 4.250.858.999 và 2.899.300.747. Đã xóa môi trường Python 3.11.9 ở `data/local/worktrees/damaged-books-abc/.venv-ai` theo lựa chọn của người dùng. Danh sách 40 gói trùng kết quả `pip freeze` được lưu ở requirements-damaged-books-ai.txt (hồ sơ cục bộ). Khi cần tái tạo, tạo môi trường ở vị trí cũ bằng `data/local/python311/python.exe -m venv data/local/worktrees/damaged-books-abc/.venv-ai`, rồi dùng Python trong môi trường đó chạy `-m pip install -r data/local/requirements-damaged-books-ai.txt` từ gốc dự án.
- Dọn cache build PlatformIO và Zig, 5.102 tệp bytecode có nguồn Python tương ứng và bản sao mô hình ba lớp trong workspace sau khi đối chiếu với bản trong thư mục tải xuống. Đã kiểm tra lại danh sách worktree, môi trường chạy DroidCam và tệp khôi phục. Chờ ảnh mới từ điện thoại.

## 2026-11-19 16:02 +07:00 — Thay kết nối trạm bằng USB 115200

- Đối chiếu `firmware/esp32/src/main.cpp` và `include/station.h`. Gỡ Wi-Fi/AP/WebSocket khỏi firmware vận hành, giữ pin map, PWM, logic nút/IR/gạt và đọc lại cấu hình hành trình NVS. Firmware dùng bộ đệm Serial hữu hạn, CAPTURE/RESULT/ACK mang cùng ID, kiểm tra heartbeat 1 giây và hạn chờ AI 10 giây. Bản tin sai hoặc đến sau khi dừng không được phép kích hoạt băng tải.
- Thay adapter Python bằng pyserial 3.5, thêm chọn COM vào HMI. Bản thử camera riêng vẫn độc lập với ESP32. Chế độ trạm tự dò một CP210x hoặc dùng cổng người vận hành chọn. Giao thức và quy trình vận hành đã ghi tại [INSPECTION_STATION.md](INSPECTION_STATION.md).
- `python -B -m unittest discover -s tests -v` trong venv trạm đạt 53/53. Chạy `zig c++ -std=c++11 -O1 firmware/esp32/test/host/station_test.cpp` rồi chạy chương trình host đạt. Kiểm tra C++ gồm ID sai, khung tràn, ACK, kết quả lặp/xung đột, dừng thủ công và mất heartbeat. `pio run --project-dir firmware/esp32 -e esp32dev` đạt, flash 314.915 B, RAM 23.640 B.
- Thử liên thông trên PC bằng `SerialController` và `UsbStation/Station` nối qua tiến trình C++ tạm, giả lập thời gian, IR, nút và đường truyền. Hai lượt PASS và FAIL đạt, đúng chu trình đẩy–thu–chờ và ngắt liên kết giữ dừng. Thử riêng luồng CAPTURE trong Runtime với mô hình thật và ảnh tổng hợp đã trả HOLD khi thiếu ngưỡng.
- `python -m serial.tools.list_ports -v` nhận Silicon Labs CP210x trên COM5. Chưa mở cổng để gửi lệnh cho board, chưa flash, chưa thử phần cứng. Đã đóng tiến trình camera-test cũ, kiểm tra cổng web không còn dịch vụ đáp ứng. Bước tiếp theo là người dùng nạp firmware và kiểm tra bắt tay COM với nguồn tải đã ngắt.

## 2026-11-19 16:08 +07:00 — Nạp và thử USB với ESP32 thật

- CP210x xuất hiện trên COM5. Trước khi nạp, bắt tay USB của trạm hết thời gian chờ. `platformio.exe run --project-dir firmware/esp32 -e esp32dev -t upload --upload-port COM5` nhận ESP32-D0WD-V3, ghi và xác minh hash firmware, hard reset và báo SUCCESS.
- Dùng `SerialController.exchange` ở 115200 với cờ sẵn sàng bằng 0. Ba lần đọc đều trả OFF, PWM 0, job 0 và STARTUP. Mở HMI ở chế độ hardware, đọc `/api/status` xác nhận connected_port COM5, OFF, PWM 0 và IR trống. HMI còn báo cần hiệu chỉnh ngưỡng AI. Người dùng xác nhận ESP32 chỉ cắm USB vào máy tính.
- Chưa thử tải, cảm biến thực hoặc chu trình có sách. Bài tiếp theo là kéo GPIO19 xuống GND khi OFF rồi nhả để quan sát trạng thái IR đổi trên HMI.

## 2026-11-19 16:12 +07:00 — Trước khi đấu cảm biến IR

- Đọc `GET /api/status` sau phản hồi của người dùng: COM5, OFF, PWM 0, IR trống. Chưa quan sát trực tiếp cả hai cạnh tín hiệu jumper. Chờ ảnh hoặc mã cảm biến IR trước khi hướng dẫn đấu nguồn và ngõ ra.

## 2026-11-19 16:16 +07:00 — Đối chiếu nguồn và điều kiện thử tích hợp

- Người dùng xác nhận nguồn motor 12 V, servo 5 V, cảm biến tiệm cận ba chân và cụm phần cứng đã hoạt động ở lần thử độc lập trước. Chưa có mã cảm biến hoặc số đo điện áp OUT. Pin map và dây logic BTS7960 đối chiếu với phần đầu `firmware/manual-tests/bts7960_button_ramp.cpp` và firmware USB đang nạp.
- Ba lần đọc API cho COM5, OFF, PWM 0, lệnh servo 0°, IR báo có vật, DroidCam lặp hình. Preview không có ảnh mới và thử kết nối cổng điện thoại đã lưu bị timeout. SQLite đọc ở chế độ chỉ đọc có 0 mẫu cho model hiện tại; chưa có `thresholds.json`. Chưa cấp lệnh chạy, lấy mẫu hay ghi kết quả phân loại. Chờ lắp hệ thống và khôi phục camera tại đúng vị trí.

## 2026-11-19 17:18 +07:00 — Chờ kết nối USB sau khi đấu dây

- Người dùng báo đã đấu dây. `GET /api/status` ở chế độ hardware báo chưa tìm thấy ESP32, trường connected_port rỗng. `serial.tools.list_ports` lọc VID/PID 10C4:EA60 cũng chưa thấy thiết bị. Chờ cắm lại board qua USB với nguồn tải tắt rồi xác nhận trạng thái OFF/PWM 0.

## 2026-11-19 17:20 +07:00 — Xác nhận USB sau khi cắm lại

- Windows đã nhận CP210x ở COM5. HMI phần cứng báo OFF, PWM 0, job 0. Chỉ đọc `/api/status` trong 32 giây, cả 128 mẫu báo IR có sách. Chưa thấy cạnh chuyển IR, chưa xác minh thao tác thực tế trong cửa sổ quan sát. DroidCam báo lặp cùng khung hình. Chưa thử tải; chờ xác nhận IR thay đổi khi đưa sách vào và lấy ra.

## 2026-11-19 17:28 +07:00 — Nạp firmware trạm đầy đủ trên COM5

- Trước khi nạp, đọc 104 mẫu từ `GET /api/status`. Lúc 17:25:37 board chuyển lý do từ STARTUP sang PC_NOT_READY. Trạng thái OFF, IR báo có vật, PWM cao nhất bằng 0.
- Tạm nhả cổng COM5 khi trạm OFF. Chạy `platformio run --project-dir firmware/esp32 --environment esp32dev --target upload --upload-port COM5`. esptool nhận ESP32-D0WD-V3, ghi firmware, kiểm tra hash và reset thành công.
- Khởi động lại trạm Python. API chế độ hardware trả COM5 với mã khởi động mới, OFF, PWM 0, IR báo có vật, lệnh servo 0°, job 0. Nạp và kết nối USB **PASS**. Thử chuyển động và phân loại sách **NOT_RUN**. DroidCam đang lặp hình, chưa có `data/local/station/thresholds.json`. Bước tiếp theo là khôi phục hình trực tiếp từ điện thoại.

## 2026-11-19 17:40 +07:00 — Phục hồi bản chạy phần cứng độc lập

- Đối chiếu SHA-256 của `firmware/manual-tests/bts7960_button_ramp.cpp` và `src/main.cpp` trong thư mục build độc lập, hai tệp trùng nhau. Dừng dịch vụ trạm Python và để COM5 trống sau kiểm tra.
- Lần nạp đầu gặp lỗi đồng bộ bộ nạp. Sau khi người dùng xác nhận ESP32 chỉ nối USB, chạy lại `platformio run --project-dir data/local/bts7960-button-only-20261115/pio --environment esp32dev --target upload --upload-port COM5`. Ghi 308336 byte firmware và xác minh hash **PASS**.
- Đọc log khởi động 115200 baud, thấy `[READY] BUTTON_IR_SERVO. PWM=0.` và `[IR] Clear confirmed; button is OFF, motor stays stopped.`. GPIO23 LOW, GPIO19 HIGH khi tách mạch. Đã đóng cổng sau khi đọc. Thử nút, IR, chuyển động motor và servo trên cụm cơ khí **NOT_RUN**. Việc tiếp theo là lắp lại khi ngắt điện rồi thử bật và tắt băng trống bằng nút.

## 2026-11-20 18:21 +07:00 — Xuất bản bản thử ESP32 lên GitHub

- Tạo nhánh `firmware/esp32-standalone-20261120-181721` từ main `d431f10` trong worktree riêng. Sao chép nguyên tệp `firmware/manual-tests/bts7960_button_ramp.cpp`, đối chiếu SHA-256 với tệp đã dùng để build và nạp trước đó.
- Bổ sung cấu hình PlatformIO cho bản thử và hướng dẫn công khai về tác dụng, ngày giờ, GPIO, chu trình, cách build/nạp và các mức kiểm chứng. Chạy `platformio run --project-dir firmware/manual-tests --environment esp32dev` trong worktree, kết quả **PASS**. Commit `43b2c580e935b40601065e7d5df83859693a5e7a` có bốn tệp.
- Auto-review chặn lần push đầu do yêu cầu xác minh repository đích. GitHub API xác nhận kho origin công khai và tài khoản trong Git Credential Manager trùng chủ kho. Push lại cùng nhánh thành công sau khi có bằng chứng.
- `git ls-remote` trả đúng SHA commit. Đọc lại bốn tệp từ raw GitHub ở commit đó, từng tệp trùng nội dung đã commit. Xuất bản **PASS**, thử lại chuyển động cơ khí **NOT_RUN**. Tiếp tục kiểm tra IR OUT đổi trạng thái trên cụm thật.

## 2026-11-20 21:51 +07:00 — Manual commissioning and offline image inspection

- Added a manual USB operator mode, real classifier input from JPG/PNG in simulation, validated station settings, persistent stop diagnostics, and calibration tied to model, background, settings and a known damaged reference. Automatic and manual decisions have independent histories. See the [one-page operator quick start](STATION_QUICKSTART.html).
- PC checks **PASS**: `python -B -m unittest discover -s tests -q` ran 71 tests; `FlashInspection.cmd --build-only` built the USB firmware; the native C++ station suite passed. The temporary integration fixture used real Python SerialController and host-compiled Station/UsbStation with simulated USB and physical inputs. It observed one release for OK, one push for NG, and one HOLD with zero PWM after the operator decision window expired. Duplicate and stale clicks were rejected.
- The real weights gave OK at 0.999027 on the torn IMG_7 reference. With representative synthetic calibration rows in a temporary database and default confidence floors, the actual reference check refused to activate a hardware profile. The file-image simulation reported the same prediction after the image-quality checks. These checks demonstrate a known false OK and its rejection, not the model's accuracy on the conveyor.
- Browser controls were checked using Edge and mocked station responses; the real local simulation entry point, guide, same-mode reuse and conflicting-mode rejection were also verified. The final operator guide printed to one A4 page. Physical station testing for this version **NOT_RUN**. Next: with motor and servo power off, flash the USB firmware and verify IR toggles, then run the first manual OK/NG pair with power restored.

## 2026-11-20 22:20 +07:00 — Station console verification and fixes

- A failed known-book check now returns its structured diagnosis in the same response. The console displays it beside the validation button. A fresh API check loaded the real weights with synthetic calibration rows in a temporary database. IMG_7 was predicted OK at 0.999027 against a 0.85 OK threshold. The request returned HTTP 409 with the manual recovery instructions and the profile remained disarmed.
- Manual decisions now display the active book ID, queued verdict and matching board acknowledgement. In an API integration check with a delayed simulated controller, OK released one book and NG pushed one book. While the acknowledgement was pending, a duplicate submission returned HTTP 409.
- Stop records now keep the controller reason and measurements for the associated stop. A dark uploaded image in the Edge simulation produced HOLD, brightness 0 and a 35–235 limit. The browser also showed the blocked-start explanation when IR was covered. The main preview uses the activated server image. The console asks the operator to finish loading a selected file before inserting a simulated book.
- PC checks **PASS**: `python -B -m unittest discover -s tests -q` (78 tests), `node --test tests/web/station_ui.test.js` (six tests), `node --check software/web/static/app.js` and `python -B scripts/check_repository.py`. Firmware was left at its immediate-stop behavior. Physical verification **NOT_RUN**. Next: follow the operator guide for the first manual OK and NG cycle.

## 2026-11-21 — Session 1 — USB firmware upload and board readback

- Windows reported one CP210x USB bridge at COM5. With the ESP32 detached from the conveyor, ran `platformio run --project-dir firmware/esp32 --environment esp32dev --target upload --upload-port COM5`. esptool identified an ESP32-D0WD-V3 revision 3.1, verified the written images including the 320704-byte application, and reset the board. Upload **PASS**.
- Read three replies with the project SerialController at 115200 baud with readiness held false. All reported OFF, STARTUP, job 0, PWM 0, IR clear and servo command 0°. Released COM5. Board communication **PASS**. Installed sensor transitions and loaded motion **NOT_RUN**. Next: check Clear → Blocked → Clear in Manual Mechanics with the installed sensor and motor/servo power off.

## 2026-11-21 — Session 2 — Before installation on the real conveyor

- Pyserial enumerated the CP210x on COM5. Ran StationVision in camera-test mode for eight seconds and closed it. Across 42 distinct sampled frame sequences, the changing-frame test **FAIL** reported a frozen image. No automatic threshold file was present. To recheck the feed, move a book in the phone camera view with DroidCam connected.
- The operator confirmed that external 5 V had been disconnected from VIN and that the ESP32 was still detached from the conveyor. Installed mechanics **NOT_RUN**. No motion command was issued. Next: reinstall with supplies and USB disconnected, then check the installed IR over USB.

## 2026-11-21 — Session 3 — Installed station communication

- With the board installed and motor and servo power off, the SerialController handshake timed out on COM5. After the operator powered the loads, pyserial found one CP210x and opened COM5 at 115200. Passive read and eight valid handshake queries with readiness disabled returned zero bytes. Installed telemetry **FAIL**. No motion command was issued, and the port was released. Belt, IR transitions and servo acceptance **NOT_RUN**.
- A six-second StationVision camera check sampled 36 distinct frame sequences and reported frozen content. The automatic threshold profile was absent. Next: turn off motor and servo power, keep USB connected, and capture the installed board's reset log.

## 2026-11-21 — Session 4 — Installed board reset and ROM probe

- With the loads off, two RTS resets each delivered a 304-byte ROM boot log at 115200 baud ending at entry 0x4008059c. The PC received boot output. The six application handshake queries across the two resets returned zero bytes.
- Between resets, ran `esptool --chip esp32 --port COM5 --baud 115200 --no-stub --connect-attempts 2 read-mac`. It detected download mode but received no sync reply and reported a possible fault on the host transmit path. Returned to flash boot and closed the port. No flash writes or motion commands. Next: inspect the installed base at RX0/GPIO3 with power disconnected.

## 2026-11-21 09:04 +07:00 — Detached-board comparison

- After the operator removed the ESP32 from the base, enumerated the CP210x at COM5 again and performed five consecutive SerialController exchanges at 115200 baud with readiness false. All five returned OFF, STARTUP, job 0, PWM 0, IR clear and servo command 0°. Released COM5. USB communication with the detached board **PASS**. No reflash or motion commands. Installed mechanics **NOT_RUN**. Next: inspect the disconnected base socket and RX0/GPIO3 wiring to locate the difference.

## 2026-11-21 — Session 6 — External power retest

- Windows again identified one CP210x at COM5. With external power reported on, five sequence-tagged PING requests at 115200 baud with readiness zero received zero bytes. The probe closed COM5 without issuing a reset, motion command or flash operation. Installed telemetry **FAIL**, mechanical acceptance **NOT_RUN**. Exact base wiring was not observed. Next: compare the bare base with the detached ESP32 using USB-only power.

## 2026-11-21 — Session 7 — Restore the standalone mechanism test

- The operator confirmed the target was detached and powered only by USB. The PlatformIO build source matched Git blob `345ec00bd68016a627fc9193d91833aea3097072` from the standalone commit `43b2c58`. Ran `platformio run --project-dir data/local/bts7960-button-only-20261115/pio --environment esp32dev --target upload --upload-port COM5`. The application was 308336 bytes. The flash hash verified and PlatformIO reported SUCCESS.
- Reset and read COM5 at 115200. Observed BUTTON_IR_SERVO, PWM 0, GPIO23 LOW on the detached board, GPIO19 HIGH, servo home command 0 degrees and motor off after the clear interval. Closed COM5. Standalone boot **PASS**. Loaded motion **NOT_RUN**. Next: test one book from button start through push, return and conveyor restart on the assembled mechanism.

## 2026-11-21 — Session 8 — PC-side wireless bridge

- Identified the detached USB bridge target using esptool read-mac on COM5. The new ESP32-D0WD-V3 was <bridge-mac>. Provisioned an encrypted channel-1 peer for the conveyor at <receiver-mac>. Git ignores the local pair header.
- Ran PlatformIO for firmware/espnow-bridge, environment esp32dev, upload on COM5. Verified the 938112-byte application hash and reset. Flash **PASS**. At 115200 baud, BRIDGE? returned the expected identity and RADIO_READY. A disabled PING advanced TX_QUEUE from 0 to 1, RX stayed at 0, and no station reply was emitted. Released COM5. Local bridge **PASS**. End-to-end radio and physical sorting **NOT_RUN**. Next: equip the old conveyor controller with its receiver and check a real readiness-disabled reply before enabling loads.

## 2026-11-21 — Session 9 — Commission the installed wireless receiver

- Built both PlatformIO environments in firmware/esp32, esp32dev and espnow_receiver. Native station tests and the repository check passed. Uploaded espnow_receiver on COM5 with the old controller detached. The tool verified the flash hash. Boot readback identified the expected receiver ending AC:5C on channel 1, OFF with PWM 0.
- With the old controller installed under external power and the bridge ending 2A:E4 on COM5, used SerialController.exchange at 115200 with readiness false. All six responses reported OFF, IR clear, PWM 0, servo command 0 and no active job. End-to-end radio **PASS**. Started software.web --manual and verified the hardware-manual API had COM5 connected.
- Observed RUN and PWM ramping to 1023. Manual inspection job 1 ended in HOLD after 8.078 s against an 8 s decision window. At readback the receiver reported FAULT, INSPECTION_HOLD, IR clear, PWM 0 and zero completed jobs. Timeout handling **PASS**. Physical tray routing and servo travel require observation at the conveyor. An independent StationVision camera check sampled 56 sequences and detected a frozen DroidCam image. Live camera change **FAIL**. Next: use the manual controls for a supervised OK/NG pair and observe both routes.
- Follow-up on the same boot: job 2 (OK) and job 3 (NG) both reached COMPLETE. For job 3 the receiver reported PUSH (180 degrees), RETRACT (0), SETTLE with PWM 0, then RUN. Job 4 was decided NG and ended in NG_NOT_CLEAR; subsequent status showed FAULT, IR clear, PWM 0 and completed ID 3. No mechanical endpoint or camera-based route feedback was available. Next: observe where the fourth book stopped relative to the sensor.

## 2026-11-21 — Session 10 — Clean the checkout for the field demo

- Compared each archived entry with its extracted file by SHA-256, including duplicate ZIP names. Preserved the original Roboflow ZIP under `data/local/damaged_books_v1/` (SHA-256 `dc2a81293b0f841b0fd187a410b869a1fc9021077ffc6221f9f33621ff978197`). Removed the matching 1,243-file export from the root and 54 duplicate Colab files from the analysis extraction. The Colab ZIP, canonical extraction and unique reports remain. Removed generated PlatformIO builds, Zig test build products/cache and project Python bytecode. Total file length removed: 584,527,068 bytes.
- Updated station entry points in the documentation and workspace, aligned CI dependencies with the station and added a field checklist. Local commands: `python -B -m unittest discover -s tests -q` (78 passed), `node --test tests/web/station_ui.test.js` (six passed), `python -B scripts/check_repository.py` (43 sources and links passed), `git diff --check` (passed). Remote CI was not run. The real model and reference loaded locally after cleanup. `inspect_reference` returned truth NG, prediction OK, confidence 0.999027. No hardware operation in this session. Next: observe the physical reject route using Manual Mechanics.

## 2026-11-23 — Phiên 1 — Quét servo độc lập trên GPIO22

- `esptool --port COM5 read-mac` nhận dạng ESP32 băng tải đuôi AC:5C. Chạy `platformio run -d firmware/manual-tests/servo-sweep -t upload --upload-port COM5`. Bản đầu cho chu kỳ lệnh 10,016 s. Đã đổi sang tính góc theo thời gian đã trôi và nạp lại thành công, hash flash khớp.
- Đọc COM5 bằng pySerial ở 115200 baud. Board báo 0° ở 36 ms, 180° ở 2560 ms, 0° ở 5044 ms và 180° ở 7568 ms. Chu kỳ lệnh **PASS**. Góc trục thực **NOT_RUN**. Tiếp theo là quan sát một chu kỳ không tải.


## 2026-11-23 — Phiên 2 — Đối chiếu MAC trước khi nạp lại receiver

- `esptool.exe --chip esp32 --port COM5 read-mac` (**PASS**) nhận ESP32-D0WD-V3 rev 3.1, MAC `<other-board-mac>`. So với StationMac trong header ghép cặp và điều kiện khởi tạo trong radio_receiver.h, bản receiver hiện tại yêu cầu `<receiver-mac>`. Nạp **NOT_RUN**. Tiếp theo là xác nhận board thay thế.


## 2026-11-23 — Phiên 3 — Nạp lại receiver sau khi đổi board trên COM5

- `esptool.exe --chip esp32 --port COM5 read-mac` nhận `<receiver-mac>`, khớp StationMac. Dùng lại cấu hình ghép cặp hiện có.
- `platformio run -d firmware/esp32 -e espnow_receiver -t upload --upload-port COM5` **PASS**, esptool xác minh hash flash. Đọc bằng pySerial ở 115200 baud sau reset **PASS**: `PBL5_RECEIVER,1,RADIO_READY,<receiver-mac>,CH=1,PHASE=OFF,PWM=0,HOME=0,OUTPUTS=READY`.
- Kiểm tra liên lạc hai board và cơ cấu **NOT_RUN**. Tiếp theo là gửi PING qua bridge với readiness tắt và tải tắt.


## 2026-11-23 — Phiên 4 — Kiểm tra liên lạc sau khi cấp nguồn hai board

- pySerial COM5 115200: gửi BRIDGE? và bốn PING có mã riêng với readiness 0. Bridge đuôi 2A:E4, RADIO_READY, kênh 1; TX_QUEUE và RX từ 0 lên 4. Cả bốn phản hồi đúng mã và cùng phiên khởi động: phase OFF, ir false, pwm 0, servo 0, job 0, reason PC_NOT_READY. Kết nối hai chiều **PASS**. Chưa thử chuyển trạng thái IR hoặc vận hành cơ cấu. Tiếp theo là đặt sách che IR trong lúc băng tải dừng.


## 2026-11-23 — Phiên 5 — Mở Manual Mechanics

- Chạy scripts/windows/ManualMechanics.cmd. GET / trả 200. GET /api/status trả hardware-manual, connected_port trống và báo ESP32 không phản hồi qua COM5 ở 115200 baud trong 5 lần đọc liên tiếp. Chưa xác định nguyên nhân. Tiếp theo là kiểm tra lại kết nối của bridge trên COM5.


## 2026-11-23 — Phiên 6 — Kiểm tra ESP-NOW trên bàn và khôi phục HMI

- pySerial, 115200 baud: COM5 báo PBL5_BRIDGE đuôi 2A:E4 và COM9 báo PBL5_RECEIVER đuôi AC:5C, cùng RADIO_READY trên kênh 1. COM9 đã đóng trước phép thử. Gửi 12 PING riêng qua COM5 với readiness 0. Có 12/12 phản hồi đúng seq, cùng boot, bộ đếm TX_QUEUE/RX tăng từ 0/0 lên 12/12. Trung vị khứ hồi qua PC 31,0 ms. Tất cả phản hồi OFF, PWM 0, IR false.
- Khởi động lại hardware-manual rồi POST /api/connect với COM5. GET /api/status trả connected_port COM5, link_error trống, phase OFF và PWM 0. Liên lạc và HMI **PASS** trên bàn. Nguyên nhân lỗi trước đó khi ở trên mạch chưa xác định. Tiếp theo là kiểm tra lại liên lạc sau khi lắp receiver vào đế.


## 2026-11-23 — Phiên 7 — Mở chế độ AI và kiểm tra DroidCam

- Chạy InspectBooks.cmd và DroidCam Client, đọc GET /api/status: hardware, COM5, FAULT/BOOK_MOVED, PWM 0, IR false. Chạy inspect_reference(Classifier(cfg)) bằng Python của trạm: ảnh NG IMG_7 trả ảnh bình thường, confidence 0,999027. Model SHA-256 662e543e1d29538f799a444583682d9f80bce7ad7e5c5f0e4fb67aa42bf0c357. Inference PASS, phân loại đúng ảnh chuẩn FAIL.
- DroidCam ghi nhận 0/2 nguồn đã lưu kết nối. Hai phép thử TCP cổng 4747 đều timeout, HMI báo FRAME_FROZEN. Kiểm tra luồng hình FAIL, phân loại sách tự động NOT_RUN. Tiếp theo là xác nhận địa chỉ hiện tại trong DroidCam trên điện thoại.


- Tiếp phiên 7 sau khi người dùng kết nối DroidCam: GET /api/live.jpg 8 lần cách nhau 0,33 s, 8 JPEG khác SHA-256, kích thước 640×480. predict(square_cover(frame, 448)) bằng weights/best.pt trên ảnh xem trước trả OK 0,99973, không có ground truth. Luồng camera và suy luận PASS, độ đúng trên cảnh N/A. GET /api/status báo hardware, COM5, camera trống lỗi, health yêu cầu hiệu chỉnh ngưỡng AI, board FAULT/BOOK_MOVED, PWM 0, IR false. Chưa chạy job tự động. Tiếp theo là lưu ảnh băng trống với camera cố định.

## 2026-11-23 — Phiên 8 — Đổi camera trạm sang A4tech USB

- enumerate_cameras(CAP_MSMF) trả A4tech HD 720P PC Camera bên cạnh DroidCam. Chọn đúng tên A4tech trong configs/station.json, giữ lại ảnh nền cũ và dùng đường dẫn nền riêng cho nguồn mới. Hai trang HMI dùng /api/live.mjpg, endpoint ảnh tĩnh vẫn dùng được.
- Chạy .venv-inspection/Scripts/python.exe -B -m unittest discover -s tests -q: 78 PASS; node --test tests/web/station_ui.test.js: 6 PASS. Đọc stream thật 90 JPEG 640×480 trong khoảng 3,22 s, 27,65 khung/s. Chrome headless lấy mẫu ảnh đang hiển thị bằng canvas: 81 hình khác nhau trong 3,002 s. Kiểm tra preview PASS.
- GET /api/status ở chế độ hardware báo camera có hình, cần ảnh nền mới. ESP32 chưa trả lời trên COM5 trong lần kiểm tra này; chưa chạy sách. Tiếp theo là cố định camera và lưu ảnh nền trống.


## 2026-11-23 — Phiên 9 — Test trực tiếp hệ thống và model với sách thật

- GET /api/status và /api/live.jpg: 8 seq khác nhau cùng boot, COM5, 8 ảnh JPEG khác nhau. Kiểm tra ảnh nền và ảnh trực tiếp thấy nền cũ nhìn ra phòng. Sau khi người dùng lấy sách ra, xác minh băng trống, IR false, PWM 0 và POST /api/background thành công.
- POST /api/pilot với cuốn Bài tập Cơ học trước và sau khi lấy nền: HTTP 409, NO_COVER. Không lưu mẫu. Không có mẫu trong bảng samples trước phép thử. Dùng predict(square_cover(frame,448)) trên ảnh webcam thấy cuốn sách thật: nhãn ảnh lỗi, 0,67362964. inspect_reference trên IMG_7 nhãn thật NG: model ra OK 0,99902713. Kết nối và chạy inference PASS; ảnh chuẩn phân loại FAIL.
- TestClient của create_app(simulation=True) với SQLite tạm hoàn tất hai lượt OK/NG, counts 1/1. Trạm thật ở OFF, PWM 0, không có chu kỳ phân loại được kích hoạt. Tiếp theo nếu thử tự động: kiểm tra tìm bốn mép của cuốn sách trên ảnh/nền thực tế.

## 2026-11-23 — Phiên 10 — Chế độ phân loại trực tiếp theo IR

- Mở scripts/windows/DirectSorting.cmd với --direct. Chế độ dùng toàn khung A4tech mới sau khi nhận CAPTURE từ ESP32 và chờ stabilize_s. Chỉ nhận nhãn đã ánh xạ; giữ thời hạn, kiểm tra phiên camera, mã job, ACK, dừng vật lý, mất liên lạc và chống kẹt. Lần sau có thể chọn InspectBooks.cmd để dùng lại hiệu chỉnh.
- Chạy unittest discover -s tests -q: 79 PASS, có bài test OK và NG ở độ tin cậy 0,55 cùng xử lý khung đóng băng. node --test tests/web/station_ui.test.js: 6 PASS. scripts/check_repository.py: PASS.
- Khi receiver chưa trả lời, ba PING readiness=0 tăng TX_QUEUE từ 10615 lên 10618, RX đứng ở 9813. Sau khi người vận hành bật nguồn, GET /api/status báo direct_routing=true, connected_port=COM5, health trống, OFF, IR trống, PWM 0. Bắt đầu quan sát lượt chạy thật.

- Chạy băng thật sau nút Start: receiver cùng boot, lượt 1 và 2 trả OK (0,996097 và 0,952383), ghi ACK/RELEASE, IR trống rồi COMPLETE. Lượt 3 trả NG 0,845615, có ACK, sau đó FAULT/NG_NOT_CLEAR. Lượt 5 OK 0,972829 hoàn tất; lượt 4 và 6 dừng BOOK_MOVED. COM5 và ảnh vẫn hợp lệ. Chưa xác nhận sách NG đến khay. Tiếp theo là quan sát cơ cấu và IR trong lượt NG.

- Lượt 7 quan sát trực tiếp qua API: WAIT_AI, PUSH 180°, RETRACT 0°, SETTLE, rồi FAULT/NG_NOT_CLEAR. IR còn báo có sách khi SETTLE; lần đọc sau khi vào FAULT đã báo trống. Đây là các lệnh servo từ receiver, chưa đo góc trục hoặc vị trí khay.

## 2026-11-23 — Phiên 11 — HMI theo ca, quyết định và chu kỳ

- Triển khai bảng lịch sử theo ca, ảnh quyết định ghim theo job, giao diện Manual và mô phỏng, cảnh báo trạm, tách cài đặt Direct. Bản tin chẩn đoán bridge chỉ gửi ở cổng được cấu hình khi mở cổng, trước heartbeat. Quan sát phản hồi receiver tách biệt với tình trạng bridge.
- Chạy .venv-inspection/Scripts/python.exe -B -m unittest discover -s tests -q (81 PASS), node --test tests/web/station_ui.test.js (7 PASS), scripts/check_repository.py (PASS). Dùng SQLite backup sao chép DB hardware sang thư mục tạm: migration đọc đủ 24 lượt; thay đổi cài đặt Direct giữ nguyên tệp ngưỡng hiệu chuẩn trong bài kiểm tra.
- Chrome headless đo innerWidth × innerHeight tại 1536×710, 1280×570, 1366×625. Chiều cao trang bằng chiều cao viewport ở cả ba kích thước. Tại 850×475, nội dung cuộn được. Mở drawer cài đặt thành công.
- Khởi động lại dịch vụ local Direct. API trả hardware, direct_routing=true, ca 29. Không mở được COM5 và không tìm thấy camera USB A4tech. Lượt OK/NG thật trong phiên: NOT_RUN. Tiếp theo: sau khi kết nối lại, kiểm tra sách OK đi tiếp và sách NG tới khay, đối chiếu với lịch sử.

## 2026-11-23 — Phiên 12 — Thiết kế và Việt hóa giao diện vận hành

- Kiểm tra HTML thực do 127.0.0.1:8765 phục vụ, mở trang mới với chuỗi phiên bản cho CSS/JS. Nền giấy sáng, thanh điều hướng than chì, khu vực camera tối và tổng quan ca có điểm nhấn xanh non. Sơ đồ chỉ hiện trong vùng camera đang chờ tín hiệu.
- Việt hóa các thông báo thao tác, lý do dừng, cài đặt, mô phỏng và trang hướng dẫn. Giữ nguyên mã giao tiếp của API/controller và các nhãn kỹ thuật OK, NG, IR, PWM. Không thay đổi firmware.
- .venv-inspection/Scripts/python.exe -B -m unittest discover -s tests -q: 81 PASS. node --test tests/web/station_ui.test.js: 9 PASS.
- Chrome headless trên dịch vụ thật: 1536×710, 1280×570 và 1024×600 vừa viewport. 850×475 và 390×780 cuộn nội dung theo chiều dọc. Kiểm tra nút cài đặt, giá trị 0,35 giây, chuyển qua lịch sử và quay lại vận hành. Ảnh chụp cục bộ: data/local/station/hmi-van-hanh.png.
- Trên Chrome headless với dữ liệu thử, trang camera xử lý mất hình, khôi phục, OK/NG, lưu ảnh và nhấn chụp hai lần. Hướng dẫn hiển thị trên điện thoại và in vừa một trang A4.
- Trạm chưa nhận hình và phản hồi board tại lúc chụp; không chạy lệnh cơ khí. Bước tiếp theo: nghiệm thu luồng OK/NG trên sách khi trạm có đủ thiết bị.

## 2026-11-25 — Phiên 1 — Mở lại giao diện vận hành

- Chạy python -m software.web --direct --no-browser và mở trình duyệt tại http://127.0.0.1:8765/?giao-dien=van-hanh. GET / và /api/status trả đúng trang và đúng chế độ.
- API báo chưa nhận camera A4tech và không mở được COM5. Thử lượt sách thật: NOT_RUN. Tiếp theo là kiểm tra kết nối thiết bị khi cần chạy sách.

## 2026-11-25 — Phiên 2 — Notebook huấn luyện book-defect-v23

- Đã đọc ZIP bằng Python `zipfile.ZipFile.testzip()` và giải mã 195 JPEG. SHA-256 của ZIP là `91e6cbcef0c8208a0a6607f53749f1cbcaa2110578f9ec298f791eb77f998cb7`. Train có 76 NG và 61 OK, validation 19 NG và 20 OK, test 15 NG và 4 OK. Không có file ảnh trùng SHA-256. dHash tìm thấy một cặp train/val cần rà ở khoảng cách ≤ 4. ZIP thiếu mã cuốn.
- [Notebook](../vision/yolo/train_book_defect_v23_colab.ipynb) dùng YOLO11n-cls, xuất xác suất OK/NG và cả hai hướng phân loại nhầm. Mặc định giữ split nguồn. Khi có CSV mã cuốn đã duyệt, notebook gom toàn bộ ảnh cùng mã vào một tập và giữ riêng ảnh test nguồn. Kiểm tra nhánh CSV bằng dữ liệu kiểm thử có nhóm đi qua cả ba tập và CSV lặp dòng **PASS**.
- Chạy `nbformat.validate` và `compile` cho cả 7 ô code **PASS**. Dùng Python của trạm chạy các ô với ZIP thật, CPU, 448 px, `EPOCHS=1`, `BATCH=8` và checkpoint pretrained. Đối chiếu mảng pixel với `vision.yolo.station.square_cover` trên ảnh dọc và ngang **PASS**. Nạp lại best.pt, suy luận 19/19 ảnh, kiểm tra CRC gói ZIP và hash checkpoint đã đóng gói **PASS**. Phần chọn file và tải xuống của Colab dùng hàm thay thế khi kiểm thử trên Windows.
- Chạy đủ lịch huấn luyện trên Colab và đánh giá camera bằng model mới **NOT_RUN**. Việc tiếp theo là mở notebook trên Colab GPU và chạy với ZIP gốc.

## 2026-11-25 — Phiên 3 — Bàn giao mã nguồn

- Chuẩn bị nhánh `feature/pbl5-station` cho repo nhóm. Tài liệu chạy Windows có lệnh cài Python, cách mở mô phỏng và hash của mô hình vận hành.
- Tệp ghép cặp ESP-NOW, cơ sở dữ liệu, ảnh camera, môi trường Python và trọng số được lưu riêng.

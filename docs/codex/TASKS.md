# Task ledger

Nguồn sự thật duy nhất về tiến độ từ phiên thiết lập 2026-11-07. Không suy trạng thái từ file tồn tại, bảng cũ hoặc roadmap. ID ổn định; không tái sử dụng. Who: CODEX, USER-HW, USER-DATA, DECISION, REVIEW. Status: TODO, IN_PROGRESS, BLOCKED, DONE, DONE-SIM, DONE-HW. DONE dùng cho đầu ra không đòi simulator/hardware; DONE-SIM cần hành vi simulator; DONE-HW cần bằng chứng thiết bị do người dùng cung cấp. Evidence phải được người thực hiện đọc/kiểm, validator chỉ kiểm cấu trúc.

BLOCKED ghi đầu vào bên ngoài thiết yếu còn thiếu; TODO có thể chờ dependency nội bộ chưa làm. Chỉ chọn CODEX khi mọi Depends đã hoàn thành và không còn đầu vào thiếu. Không đánh IN_PROGRESS cho người thật khi họ chưa xác nhận đang làm.

Kế hoạch trực tiếp 2026-11-10 ưu tiên A05 → H14/A01 → Colab → app barcode/AI → policy/simulator → camera. Yêu cầu tiếp nối 2026-11-11 cho phép chuẩn bị/xuất bản công cụ Colab để team thử song song; GPU train vẫn cần bằng chứng H08/A02. Task FastAPI/HMI/firmware/phần cứng bên dưới giữ lộ trình dài hạn, không thuộc bước đồng bộ công cụ hiện tại.

## Cách đọc nhanh

Nhìn ký hiệu ngay trước tên việc trong cột **Task**:

- ⬜ **Chưa làm** — TODO.
- 🟡 **Đang làm** — IN_PROGRESS.
- ⛔ **Đang chờ / bị chặn** — BLOCKED; xem Evidence để biết đang chờ gì, không có nghĩa là test thất bại.
- ✅ **Đã hoàn thành** — DONE; đạt điều kiện của task, không tự suy thành đã thử phần cứng.
- 🧪 **Đã đạt mô phỏng** — DONE-SIM; chưa thay thế kiểm chứng thiết bị thật.
- ✅🔌 **Đã đạt trên thiết bị thật** — DONE-HW; đã có bằng chứng người dùng cung cấp.

Cột **Who**: CODEX là AI làm; USER-HW/USER-DATA là phần bạn cung cấp hoặc thử thực tế; DECISION cần bạn xác nhận; REVIEW cần người kiểm tra. Bạn xem **Acceptance** để biết thử thế nào mới đạt, **Evidence** để biết kết quả đã kiểm chứng.

Ký hiệu chỉ minh họa cho **Status**, không tạo trạng thái riêng. Khi AI đổi Status, phải đổi ký hiệu cùng lúc theo chú giải này. Có thể mở Markdown Preview trong VS Code bằng Ctrl+Shift+V để nhìn bảng rõ hơn.

## Tasks

| ID | Task | Who | Depends | Acceptance | Status | Evidence |
|---|---|---|---|---|---|---|
| H01 | ✅ Thiết lập harness, audit và PR nền | CODEX | - | Đọc inventory tracked/issues; tài liệu nhất quán; validator và fixture unittest PASS; diff đúng allowlist; nhánh được push và có PR vào main, không merge | DONE | Commit 37d98d2; SESSION_LOG phiên 2: checker/validator và 54 tests PASS trên commit sạch; PR https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/5 mở vào main, remote SHA đã xác minh |
| H02 | ⬜ Review PR harness | REVIEW | H01 | Người review xác nhận phạm vi, bằng chứng và khả năng tiếp tục bằng review trên PR | TODO | - |
| H03 | ⛔ Cung cấp và xác nhận danh sách phần cứng/IO | USER-HW | - | Gửi model/ảnh board, sensor, driver, nguồn/điện áp/tải, cơ cấu/hành trình, feedback, giao tiếp; xác nhận bảng IO trước mã điều khiển | BLOCKED | Chờ người dùng cung cấp Q2; issue #3 chưa có bảng IO |
| H04 | ⛔ Cung cấp mẫu bìa hồi quy có nguồn gốc | USER-DATA | - | Gửi raw/crop/debug B08 và nhiều bìa kèm mã sách, điều kiện chụp, quyền dùng nội bộ và vị trí lưu ngoài Git; xác nhận đâu là mép đúng | BLOCKED | Chờ bộ mẫu được xác nhận Q8; ảnh không có trong clean checkout |
| H05 | ✅ Chốt bảng lớp phương án mới | DECISION | - | Người dùng duyệt Barcode/Notch/Ripped/Spot/Wornout, loại Tag, giữ Barcode ngoài lỗi; nhãn nghi vấn và mẫu âm phải rà riêng H14 | DONE | Kế hoạch trực tiếp 2026-11-10; D20 thay phạm vi hai lớp cũ, không tự xác nhận mọi annotation đúng |
| H06 | ✅ Chốt bảng định tuyến A/B/C/STOP | DECISION | - | Ripped ưu tiên A; lỗi khác B; hợp lệ không thấy lỗi C; camera/ảnh/model/AI lỗi STOP, barcode thiếu vẫn phân AI; không khay HOLD | DONE | Kế hoạch trực tiếp 2026-11-10; D21; phần code policy/simulator chưa thực hiện ở bước dữ liệu |
| H07 | ⛔ Duyệt tiêu chí nghiệm thu và bộ thử | DECISION | - | Xác nhận chỉ số, mục tiêu, cỡ mẫu/điều kiện đo cho vision/AI/cơ khí/tích hợp; đề xuất chưa duyệt không thành gate chính thức | BLOCKED | Chờ phản hồi Q4 |
| H08 | ⛔ Xác minh phiên Colab GPU huấn luyện | USER-DATA | - | Phiên GPU thật ghi thư viện,config,seed,hash và artifacts | BLOCKED | Notebook và split sẵn; người dùng cần chạy Colab GPU; docs/COLAB_TRAINING.md |
| H09 | ⛔ Cung cấp nguồn danh mục sách | USER-DATA | - | Có mẫu schema và dữ liệu được phép dùng: copy_id, title/category, tính duy nhất, cập nhật và nguồn; không commit dữ liệu thật | BLOCKED | Chờ thông tin Q7 |
| H10 | ⛔ Xác nhận phân công và reviewer | DECISION | - | Có người phụ trách từng module và reviewer ngoài tác giả theo CONTRIBUTING; xác nhận bằng phản hồi người dùng | BLOCKED | Chờ thông tin Q5 |
| H11 | ⛔ Xác nhận hạn và phạm vi demo | DECISION | - | Người dùng cung cấp ngày hoặc xác nhận chưa có hạn; thống nhất demo simulator hay hardware và giới hạn | BLOCKED | Chờ thông tin Q3 |
| H12 | ⛔ Thống nhất hợp đồng trạng thái QR | DECISION | - | Quyết định giữ trạng thái kỹ thuật nội bộ hay mở rộng hợp đồng cho PENDING/DECODE_ERROR, có mapping rõ | BLOCKED | Chờ phản hồi Q9; CODEBASE_MAP C1 |
| H13 | ✅ Đánh dấu trực quan tiến độ task | CODEX | H01 | Mỗi task có ký hiệu đúng Status; có chú giải phân biệt chưa làm/đang làm/chờ/xong/mô phỏng/thiết bị; giữ bảy cột và enum; checker, validator, diff PASS | DONE | docs/SESSION_LOG.md phiên 3; checker và validator PASS; đối chiếu ký hiệu/enum và git diff --check PASS |
| H14 | ✅ Rà nhóm và nhãn phần dữ liệu sử dụng | USER-DATA | A05 | Ảnh dùng có nhóm và nhãn duyệt; nghi vấn giữ cách ly | DONE | Báo cáo Gemini vòng4:361 ảnh duyệt/121 nhóm,259 cách ly; split manifest thực tế đã đối chiếu; không khẳng định rà ảnh độc lập lần nữa |
| V01 | ⛔ Sửa chọn mép bìa bằng hồi quy | CODEX | H04 | Test ảnh được chia sẻ riêng tái hiện lỗi rồi PASS với mép ngoài đúng; test tổng hợp chống chạm biên; không đổi parser/bundle; HW nghiệm thu ở V03 | BLOCKED | Chờ H04; issue #1 |
| V02 | ✅ Tách preview khỏi geometry/QR | CODEX | H01 | Test QR chậm/lỗi, frame cũ, đóng cửa sổ và mất camera; preview nhận frame mới độc lập; save liên kết đúng frame; đo latency trước/sau bằng fixture; không đặt ngưỡng HW | DONE | Commit 6a0e1bb; PR https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/6; docs/PREVIEW_VALIDATION.md; 71 tests PASS, GUI synthetic PASS; fixture median preview 211.040→10.774 ms; webcam NOT_RUN, gate riêng V03 |
| V08 | ✅ Việt hóa giao diện thu ảnh bìa | CODEX | V02,V07 | Chữ Việt có dấu trên Windows; trạng thái, thông số, phím và lỗi dễ hiểu; không đổi enum/parser/bundle; hồi quy unittest và GUI synthetic có bằng chứng, không suy nghiệm thu HW | DONE | Commit ef4e898; PR https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/10; SESSION_LOG phiên 8; checker/validator PASS; 93 tests PASS (0 failure/error/skip); GUI synthetic có dấu và các ca QR/cảnh báo đã xem; chưa nghiệm thu camera |
| V03 | ⛔ Kiểm chứng camera và crop thực tế | USER-HW | V01,V02,H03,H07 | Người dùng gửi video/log/raw/crop/debug, resolution/FPS, thử mất camera và bộ bìa theo gate đã duyệt; đạt gate mới DONE-HW | BLOCKED | Chờ các đầu vào và thực nghiệm người dùng |
| V04 | ⛔ Chuẩn hóa trạng thái QR tại biên module | CODEX | H12 | Test mọi enum/mapping và nhiều QR/QR lỗi; không dùng VALID_FORMAT làm identity VALID | BLOCKED | Chờ quyết định H12 |
| V05 | ⬜ Kiểm tra bundle và báo cáo pilot | CODEX | H01 | Lệnh kiểm manifest, hash, nguồn ảnh, accepted/review, thống kê theo cuốn; fixtures lỗi/thiếu file; giữ raw bất biến | TODO | - |
| V06 | ⛔ Thu và xác nhận pilot thật | USER-DATA | V03,V05,H05 | Cung cấp manifest/checksum ngoài Git, số ảnh/cuốn và ca loại; nhãn mẫu được duyệt; không dùng synthetic thay dữ liệu thật | BLOCKED | Chờ mẫu/nhãn/camera đạt gate |
| V07 | ✅ Tối ưu bìa sáng/tối và nhiều loại nền | CODEX | H01,V02 | Ma trận synthetic kiểm góc/crop, nhiễu nền/ron/viền in và quality bìa sáng; giữ API/config cũ/QR/bundle/worker; toàn bộ tests/checker/validator, benchmark và GUI synthetic PASS; kiểm webcam do người dùng cung cấp riêng | DONE | Commit cd8b48c; PR https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/9; docs/COLOR_BACKGROUND_VALIDATION.md; SESSION_LOG phiên 6; ma trận 50/50 góc <10px và crop; checker/validator, 88 tests và GUI synthetic PASS; chưa thử webcam, không DONE-HW |
| B01 | ⬜ Schema SQLite và migration ban đầu | CODEX | H01 | PR schema tối thiểu copy/title/category và migration/reopen/uniqueness test bằng DB tạm; mẫu dữ liệu fake được đánh dấu; không chốt mapping A/B | TODO | - |
| B02 | ⛔ Import danh mục và lookup QR | CODEX | B01,H09 | Test import hợp lệ/trùng/lỗi và lookup VALID/UNKNOWN_ID trên fixture theo schema nguồn đã duyệt | BLOCKED | Chờ H09 |
| B03 | ⬜ Lưu job và truy vết kết quả | CODEX | B01 | Test UUID, transaction/rollback/reopen và truy vết image/model/policy, expected/actual route, simulation/hardware tách biệt | TODO | - |
| A01 | ✅ Chia Damaged Books đã duyệt theo nhóm | CODEX | A05,H14 | Xấp xỉ70/15/15 seed42, đủ năm lớp, không trùng nhóm; cách ly nghi vấn, giữ test cuối | DONE | Split-reviewed-v1:253/54/54 ảnh,83/18/20 nhóm;checksum và giao nhau nhóm/ID/ảnh PASS; version077edf4cdcbd; SESSION_LOG Colab |
| A05 | ✅ Chuẩn hóa Damaged Books năm nhãn và kiểm split cũ | CODEX | H01,H05 | Giữ nguồn/ZIP; bỏ ID4, remap5→4; giữ620 ảnh/3610 hộp/34 nhãn rỗng; báo51 ứng viên âm, checksum/license và công cụ review/split có test | DONE | Commit10b5a22; PR https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/pull/11; CI nguồn success; DAMAGED_BOOKS_DATASET và SESSION_LOG 2026-11-10 phiên2; audit620 bản ghi khớp ZIP; không nghiệm thu A01 từ fixture |
| A02 | ⛔ Pipeline train YOLO11n tái lập | CODEX | A01,H08 | Chạy train thật, ghi config/seed/split/model version và artifact; không báo chất lượng từ smoke test | BLOCKED | Đã có notebook độc lập,6 test cổng dữ liệu PASS;GPU train NOT_RUN; chờ H08 |
| A06 | ✅ Đồng bộ bộ thí nghiệm cho team | CODEX | A01 | Công cụ và dataset tải được từ GitHub; cấu hình/tên lượt riêng, cùng split/seed, báo cáo validation; giữ test cuối | DONE | Commit b310c53; dataset Release damaged-books-reviewed-v1 tải lại SHA PASS;111 tests,repository/state PASS;TEAM_TRAINING.md;GPU train chưa chạy |
| A03 | ⛔ Đánh giá validation và chọn threshold | CODEX | A02,H07 | Báo cáo per-class precision/recall, confusion, latency và REVIEW; chọn ngưỡng chỉ trên validation theo gate duyệt | BLOCKED | Chờ model và tiêu chí |
| A04 | ⬜ Adapter inference có version | CODEX | A03 | Test đầu vào lỗi, ảnh không đủ chất lượng, bbox/class/score/version; chạy model thật và đo latency, không GPIO | TODO | - |
| S01 | ⬜ DecisionPolicy A/B/C/STOP thuần dữ liệu | CODEX | H06 | Unit test Ripped ưu tiên A, lỗi khác B, valid không thấy lỗi C; ảnh/camera/model/AI lỗi STOP; barcode không phải lỗi và thiếu mã không chặn AI; không serial/GPIO | TODO | H06 đã duyệt; chưa bắt đầu theo thứ tự kế hoạch |
| S02 | ⬜ FastAPI lifecycle một job | CODEX | B02,B03,S01 | Integration test nhận một job, từ chối job chồng, status/error/persistence và adapter AI fake có nhãn; chưa coi là end-to-end model thật | TODO | - |
| S03 | ⬜ Web HMI HTML/CSS/JS | CODEX | S02,S04 | Browser test ảnh/QR/identity/AI/route/history/fault và START/STOP/RESET/HOME qua API; hiển thị mode; không GPIO | TODO | - |
| S04 | ⬜ Controller simulator và transport contract | CODEX | H01 | Test sequence, ACK so với completion, timeout/duplicate và UNCONFIRMED bằng fake clock; config chọn simulator; đạt hành vi mới DONE-SIM | TODO | - |
| S05 | ⛔ Đặc tả và codec giao thức PC–ESP32 | CODEX | H03,S04 | Review framing/checksum/seq/timeout/retry với người phụ trách, golden vectors và test gói lỗi/trùng; chưa giả định loại kết nối | BLOCKED | Chờ đặc tính giao tiếp H03 |
| S06 | ⬜ Adapter serial theo hợp đồng | CODEX | S05 | Test stream giả lập phân mảnh, reconnect/timeout và đổi adapter bằng config; không suy actual_route từ send/ACK | TODO | - |
| F01 | ⛔ Firmware state machine/protocol | CODEX | H03,S05 | Build board được xác nhận; test parser/state/interlock qua harness host hoặc simulator; không nghiệm thu cơ cấu từ build | BLOCKED | Chờ IO/board/giao thức |
| F02 | ⛔ Xác minh firmware trên board chưa gắn tải | USER-HW | F01,H07 | Người dùng gửi board/firmware SHA, lệnh nạp, serial trace và bài thử timeout/reset; đạt gate mới DONE-HW | BLOCKED | Chờ board và firmware |
| F03 | ⬜ Điều khiển băng tải theo IO duyệt | CODEX | F02 | PR riêng driver/interlock băng tải; build và test điều kiện dừng qua mock; không tự chốt tải/pin | TODO | - |
| F04 | ⛔ Thử băng tải thật | USER-HW | F03,H07 | Video/log người dùng về chạy/dừng/interlock theo tải và gate được duyệt; đạt mới DONE-HW | BLOCKED | Chờ cơ cấu thật |
| F05 | ⬜ Điều khiển pusher A | CODEX | F04 | PR riêng state/timeout/homing pusher A theo hành trình duyệt; build và mock test | TODO | - |
| F06 | ⛔ Thử pusher A thật | USER-HW | F05,H07 | Video/log vị trí đầu/cuối, timeout và số lần đạt/lỗi theo gate; đạt mới DONE-HW | BLOCKED | Chờ pusher A thật |
| F07 | ⬜ Điều khiển pusher B | CODEX | F06 | PR riêng pusher B, test độc lập và interlock không kích đồng thời sai điều kiện | TODO | - |
| F08 | ⛔ Thử pusher B thật | USER-HW | F07,H07 | Bằng chứng người dùng về hành trình/khay B và lỗi theo gate; đạt mới DONE-HW | BLOCKED | Chờ pusher B thật |
| F09 | ⬜ Xác nhận đầu ra bằng sensor | CODEX | F08,H03 | Test event sensor đúng job, timeout/duplicate, UNCONFIRMED; actual_route chỉ từ feedback | TODO | - |
| F10 | ⛔ Thử feedback và mất xác nhận thật | USER-HW | F09,H07 | Video/log đồng bộ sensor và sách tới khay, thiếu/xung sai feedback theo gate; đạt mới DONE-HW | BLOCKED | Chờ feedback thiết bị thật |
| I01 | ⬜ Tích hợp end-to-end simulator | CODEX | V04,B02,B03,A04,S01,S02,S03,S04 | Chạy ảnh → QR → DB → model → policy → lưu → simulator → feedback với job trace; tách synthetic fixtures/model thật; đạt mới DONE-SIM | TODO | - |
| I02 | ⬜ Fault/recovery simulator | CODEX | I01 | Kịch bản camera/QR/DB/AI/controller lỗi, retry/restart/duplicate không hoàn tất giả; báo cáo trace; đạt mới DONE-SIM | TODO | - |
| I03 | ⬜ Nối transport thật trong orchestrator | CODEX | I02,S06,F10 | PR đổi adapter bằng config; regression simulator vẫn đạt, log mode rõ; chưa suy thành HW PASS | TODO | - |
| I04 | ⛔ End-to-end và recovery thiết bị thật | USER-HW | I03,H07 | Người dùng gửi video/log job UUID, ảnh, route mong đợi/thực và fault/recovery; đạt gate mới DONE-HW | BLOCKED | Chờ tích hợp và bằng chứng thực |
| E01 | ⬜ Báo cáo KPI AI trên test độc lập | CODEX | A04,H07 | Không tune trên test; ghi per-class precision/recall, confusion, REVIEW, latency, split/model hash và hạn chế | TODO | - |
| E02 | ⛔ Đo QR trên bộ thử thật | USER-DATA | V03,V04,H07 | Người dùng cung cấp ảnh/log điều kiện và ground truth; báo tỷ lệ đọc/đúng ID/sai ID/không đọc, cỡ mẫu; không suy từ B08 đơn lẻ | BLOCKED | Chờ bộ thử và ngưỡng duyệt |
| E03 | ⛔ Đo cơ khí trên thiết bị thật | USER-HW | F10,H07 | Người dùng gửi số lần thử/đúng khay/kẹt/mất feedback và chu kỳ theo gate; đạt mới DONE-HW | BLOCKED | Chờ bài đo thiết bị |
| E04 | ⬜ Tổng hợp KPI tích hợp | CODEX | I04,E01,E02,E03 | Báo cáo truy nguồn log, tỷ lệ đúng khay/hoàn tất/fault, median và p95 cycle time; so gate duyệt, không điền số đo giả | TODO | - |
| R01 | ⬜ Freeze phiên bản và checklist release | CODEX | E04 | Chốt manifest code/config/model/data version, test report, known limitations và quy trình rollback trong một PR | TODO | - |
| R02 | ⛔ Hướng dẫn vận hành và demo | CODEX | R01,H11 | Lệnh cài/chạy/reset/recovery, kịch bản demo theo phạm vi duyệt, điều kiện chờ người thật rõ | BLOCKED | Chờ phạm vi/hạn demo H11 |
| R03 | ⬜ Diễn tập demo và review nghiệm thu | REVIEW | R02,H10 | Reviewer và người dùng đối chiếu gate/bằng chứng, ghi lỗi còn lại và phản hồi; không tự duyệt thay người | TODO | - |
| R04 | ⬜ Gói bàn giao tái lập | CODEX | R03 | Hướng dẫn người mới dựng/chạy từ bản freeze, sơ đồ/IO/schema/protocol tham chiếu, dữ liệu/weights ngoài Git có checksum và quyền truy cập | TODO | - |

## Thứ tự đề xuất

**H08/A02** là bước hiện tại: người dùng chạy notebook Colab GPU với split-reviewed-v1.zip. Chưa tích hợp AI/app hoặc chạy test cuối. Các bước collector/camera khác giữ backlog.

## Backlog

Tham chiếu các ID trong bảng: V01/V04/V05; B01–B03; A01–A04; S01–S06; F01–F10; I01–I04; E01–E04; R01–R04. Ý tưởng mới chỉ thêm task nhỏ với ID mới khi đủ phạm vi/acceptance; không biến mô tả module tương lai thành trạng thái hoàn thành.

## Ánh xạ M01–M27

Nguồn được version control: [PLAN](../PLAN.md). Số M bám Bước trong roadmap local gốc; các đường dẫn gợi ý cũ không phải yêu cầu tạo stub. Không đặt trạng thái mốc thứ hai ở đây.

- M01 → V02, V03; M02 → V01, V03, V07; M03 → V04, E02.
- M04 → B01, B02; M05 → V05, V06, V08.
- M06 → H05, A01; M07 → A02; M08 → A03; M09 → H06, S01.
- M10 → B03, S02; M11 → S03; M12 → S04; M13 → S05, S06.
- M14 → F01, F02; M15 → F03, F04; M16 → F05, F06; M17 → F07, F08; M18 → F09, F10.
- M19 → I01, I03, I04; M20 → I02, I04.
- M21 → E01; M22 → E02; M23 → E03; M24 → E04.
- M25 → R01; M26 → R02, R03; M27 → R04.

## Ánh xạ issue mở

Kiểm kê GitHub API lúc 2026-11-07T08:53:36+07:00: endpoint issues state=open, per_page=100, page=1 trả 4 issue và không có trang tiếp; từng endpoint comments page=1 trả 0. Đã đọc toàn bộ body; không có trao đổi để đọc thêm. Endpoint pulls state=open trả 0 trước PR harness. Không tạo/sửa/đóng issue.

- [#1 — Mép bìa/đường ron](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/issues/1) → H04, V01, V03, V07. V07 chỉ có hồi quy synthetic; cần dữ liệu riêng và kiểm camera theo acceptance của issue.
- [#2 — Preview độc lập QR](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/issues/2) → V02, V03. Sửa phần mềm và bằng chứng camera tách riêng.
- [#3 — Board và IO](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/issues/3) → H03, F01, F02; không lấy esp32dev scaffold làm board đã xác nhận.
- [#4 — Pilot/nhãn](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/issues/4) → H04, H05, V05, V06, A01.

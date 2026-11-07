# Roadmap từ baseline đến bàn giao

Kế hoạch, không phải sổ trạng thái. Xem [TASKS](TASKS.md) để biết tiến độ, [STATE](STATE.md) để tiếp tục. Nguồn M01–M27: [PLAN](../PLAN.md); giữ nguyên phạm vi [ARCHITECTURE](../ARCHITECTURE.md) và quyết định đã có. Baseline hiện là collector và scaffold firmware, chưa có luồng phân loại trọn vẹn.

## Prefix và ba luồng

- H: harness, đầu vào con người và quyết định; V: vision/QR/capture; B: book database; A: AI/dataset.
- S: software core/HMI/controller simulator/transport; F: firmware/cơ cấu; I: tích hợp; E: đánh giá; R: release/demo/bàn giao.
- Luồng vision/AI: H04/H05 → V01/V02/V04/V05 → V03/V06 → A01–A04 → E01/E02.
- Luồng phần mềm và simulator: B01/B03 và S04 có thể bắt đầu độc lập ảnh thật → B02/S01/S02 → S03/S05/S06 → I01/I02.
- Luồng firmware/cơ cấu: H03 thu sớm → F01/F02 → F03/F04 → F05/F06 → F07/F08 → F09/F10. I03/I04 chỉ nối thiết bị sau gate từng cơ cấu.

Ba luồng là khả năng phân công nhóm, không cho phép một phiên tự mở nhiều task CODEX IN_PROGRESS. AI/HMI không gọi GPIO; một sách/job, actual_route chỉ từ feedback; mode simulation/hardware riêng. DONE-SIM không thay thế bất kỳ gate phần cứng nào.

## Phase và gate

| Phase | Đầu vào | Đầu ra và task | Gate kiểm chứng | Rủi ro và cách xử lý | Công Codex ước lượng |
|---|---|---|---|---|---|
| P0 Quy trình/đầu vào | Source/issue được audit, quyết định hiện có | H01/H02; yêu cầu H03–H12 đưa lên sớm | Validator/fixture PASS, PR review; người dùng xác nhận đầu vào riêng | Thiếu người/dữ liệu không chặn V02/B01/S04/V05 độc lập | 1–2 phiên harness; quyết định cần người không tính công code |
| P1 Vision/capture | Collector, mẫu H04, label H05, gate H07 | V01–V06; camera/QR/crop và pilot truy nguồn | Synthetic regression + video/log/ảnh thật V03; manifest/nhãn V06; đánh giá QR riêng E02 | Mép hình in/ron, QR chậm, frame cũ: regression, preview độc lập, cố định ánh sáng, provenance | 4–7 phiên |
| P2 Book database/core contract | D04/D07/D10/D16, danh mục H09, route H06 | B01–B03, S01; lookup/policy/persistence | DB tạm migration/rollback/reopen; bảng policy có test đủ nhánh | Category chưa rõ: schema không tự map route, chờ H06; dữ liệu thật ngoài Git | 4–6 phiên |
| P3 Dataset/AI | Pilot/nhãn đã duyệt, máy H08, gate H07 | A01–A04; split/model/threshold/inference | Không leakage theo cuốn/thiết kế; train thật có version; validation khác test cuối | Ít mẫu/lệch lớp, GPU thiếu: thu bổ sung có nguồn, báo giới hạn, không dùng fake làm KPI | 4–8 phiên, chưa tính thời gian train máy |
| P4 API/HMI/simulator/protocol | Core contract, quyết định giao tiếp H03 | S02–S06; API một job, UI, simulator, codec/adapter | Integration/browser/fake clock/error traces; S04 chỉ DONE-SIM khi chạy; codec golden vectors | ACK bị hiểu là tới khay, duplicate/restart: tách completion và actual_route, UNCONFIRMED | 5–9 phiên |
| P5 Firmware và từng cơ cấu | IO/nguồn/tải/hành trình được xác nhận, protocol S05 | F01–F10; board, băng tải, pusher A/B, feedback | Mỗi CODEX PR build/mock riêng; mỗi USER-HW task cần bằng chứng thiết bị thật do người dùng gửi và gate đã duyệt | Pin/điện áp/hành trình chưa rõ: BLOCKED, không thử đoán; kiểm từng cơ cấu trước ghép | 5–10 phiên code, thời gian lắp/thử riêng |
| P6 Tích hợp/phục hồi | Module đạt gate; simulator và model; feedback thật cho hardware | I01–I04 | I01/I02 end-to-end/fault trace DONE-SIM; I04 bằng chứng thật mới DONE-HW | Sai job/frame, mất điện/link/feedback: UUID, replay/idempotency, không hoàn tất giả | 3–6 phiên code |
| P7 Đánh giá/freeze/bàn giao | Bộ thử và ngưỡng H07, người review H10, demo H11 | E01–E04, R01–R04 | KPI truy nguồn, so ngưỡng đã duyệt, release manifest và người dùng/reviewer nghiệm thu | Đổi test để chạy đẹp, không tái lập: freeze split/model/config, ghi lỗi, giữ test cuối độc lập | 5–8 phiên code/docs |

Tổng công Codex dự kiến **31–56 phiên tập trung**, không phải lịch cam kết và không cộng số ngày từ các luồng song song. Giả định một PR nhỏ/phiên, có review kịp thời, không thay kiến trúc/phần cứng lớn, dependency đã được cho phép; gặp lỗi phải chia task nhỏ và điều chỉnh ước lượng có căn cứ. Số phiên không là tỷ lệ phần trăm hoàn thành.

Thời gian chờ người/dữ liệu/thiết bị/train/review: **N/A, chưa có thông tin để ước lượng**. Theo dõi riêng H03–H12 và các gate USER-HW/USER-DATA; không gộp vào thời gian code. Hạn demo: chưa được cung cấp (Q3). Việc mẫu ảnh/nhãn, BOM/IO, nguồn danh mục, máy train và phân công review phải được yêu cầu ngay P0 để ba luồng không cùng dừng về sau.

## Kế hoạch đo

Tất cả giá trị mục tiêu/cỡ mẫu mới chưa có nguồn duyệt đều là **đề xuất, chờ tôi xác nhận** (H07). Không biến default config như sharpness=65, stable_frames=4 hoặc max_frame_age_seconds=1.5 thành tiêu chí nghiệm thu. Đề xuất cách đo dưới đây cần được xác nhận trước khi dùng làm gate kết luận; hiện giá trị kết quả N/A khi chưa đo.

| Chỉ số | Cách đo và dữ liệu | Gate/task |
|---|---|---|
| Camera/preview | FPS nhận/hiển thị, tuổi frame, median/p95 latency, số lỗi đọc/mất camera; resolution/backend và điều kiện cố định; log trước/sau V02 | V02 fixture; V03 thiết bị thật, mục tiêu đề xuất, chờ tôi xác nhận |
| Geometry | So mép/crop với góc hoặc mask chuẩn do người dùng xác nhận; tỷ lệ crop đúng, chạm biên/nhầm nền, lỗi theo bìa/ánh sáng; có raw/debug để truy xét | V01 hồi quy, V03 thật; ngưỡng IoU/sai lệch và số cuốn đề xuất, chờ tôi xác nhận |
| QR | Tách số đọc được, đúng ID, sai ID, không đọc, nhiều mã theo ground truth; ghi mẫu số và điều kiện; không lấy 5/12 B08 làm accuracy tổng quát | E02; mục tiêu đề xuất, chờ tôi xác nhận |
| Dataset | Số cuốn/thiết kế/ảnh, phân bố lớp và phiên, số loại/review; checksum, duplicate và leakage giữa split; quy tắc nhãn có ví dụ | V06/A01; cỡ mẫu/phân bố mục tiêu đề xuất, chờ tôi xác nhận |
| AI | Precision/recall từng lớp, confusion, phát hiện bỏ sót, REVIEW rate, latency; validation chọn threshold, test độc lập chỉ đánh giá cuối; model/data/config hash | A03/E01; target từng lớp và tradeoff đề xuất, chờ tôi xác nhận |
| Simulator/protocol | Trace UUID/sequence/mode, expected/actual, duplicate/timeout/restart; kiểm không COMPLETE khi chưa có completion/feedback; fake AI phải gắn nhãn | S04/I01/I02; test invariant theo D07/D09/D10, số kịch bản hiệu năng đề xuất, chờ tôi xác nhận |
| Cơ khí | Số lần tới đúng khay, kẹt, mất feedback, home/timeout; video/log đồng bộ và tải/hành trình đã duyệt | E03, các F gate; mục tiêu đề xuất, chờ tôi xác nhận; cần người dùng cung cấp |
| Toàn hệ thống | Tỷ lệ xử lý đúng/trả HOLD/fault, đúng khay theo ground truth, cycle time median/p95, recovery; tách simulator/hardware trong từng dòng dữ liệu | E04/I04; mục tiêu đề xuất, chờ tôi xác nhận |

## Định nghĩa hoàn chỉnh

Luồng camera/ảnh → OpenCV/QR → lookup → AI hai lớp → policy → persist → controller → feedback đã chạy trọn vẹn simulator; thiết bị thật đã có bằng chứng người dùng đạt các gate riêng; có đánh giá định lượng và tài liệu vận hành/bàn giao. Không gộp build, unit test hoặc mock sensor thành bằng chứng hardware. Chỉ TASKS ghi trạng thái thực tế; roadmap không tự đánh dấu tiến độ.

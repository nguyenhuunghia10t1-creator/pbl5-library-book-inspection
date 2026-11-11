# Quyết định thiết kế

Cập nhật: 2026-11-10. D20–D23 thay các quyết định hai lớp/QR/HOLD cho luồng inspect mới; collector legacy chưa đổi mã trong bước dữ liệu.

| ID | Quyết định | Cơ sở |
|---|---|---|
| D04 | OpenCV cho thu ảnh/geometry/QR; YOLO11n là hướng AI ban đầu; FastAPI và SQLite cho giai đoạn tích hợp | Tách xử lý thị giác, dữ liệu và điều phối |
| D05 | Băng tải cố định, hai nhánh A/B và tuyến HOLD | Phân tách sách theo nhóm và ngoại lệ |
| D06 | Hai lớp lỗi: cover_tear và surface_stain | Giới hạn bài toán kiểm tra bìa ban đầu |
| D07 | Một sách/job tại một thời điểm, liên kết bằng UUID | Tránh ghép ảnh và kết quả sai cuốn |
| D09 | Có trạng thái UNCONFIRMED cho lượt xử lý thiếu xác nhận | Không tự hoàn tất job khi mất liên lạc |
| D10 | Lưu riêng simulation/hardware và expected_route/actual_route | Phân biệt lệnh dự kiến với kết quả được xác nhận |
| D11 | Giữ raw bất biến; chia dataset theo cuốn/thiết kế bìa | Truy vết nguồn và tránh rò rỉ train/test |
| D16 | Collector hỗ trợ PBL5-B + 2–6 chữ số và LIB1:copy_id | Tương thích mã bìa đã in; chưa thay thế tra cứu DB |
| D17 | Crop mặc định 630×888; lưu raw/crop/debug và metadata | Chuẩn hóa ảnh nhưng bảo toàn nguồn |
| D18 | Tách firmware, vision, software, tests, scripts, examples và data | Phát triển theo module và review độc lập |
| D19 | Repository public quản lý mã và tài liệu kỹ thuật; main dùng PR/review/CI | Dữ liệu camera, weights, credentials và hồ sơ cục bộ nằm ngoài Git |
| D20 | ĐÃ DUYỆT: Damaged Books v1, Barcode/Notch/Ripped/Spot/Wornout ID0–4; bỏ Tag nguồn4, Wornout5→4; ảnh/ZIP/nhãn nguồn bất biến, CC BY4.0 | Kế hoạch người dùng 2026-11-10, thay D06 trong luồng mới; rà nhóm theo cuốn/thiết kế, cách ly nghi vấn và duyệt mẫu âm trước split70/15/15 seed42; [bằng chứng](DAMAGED_BOOKS_DATASET.md) |
| D21 | ĐÃ DUYỆT: ảnh/camera/model/AI lỗi STOP; Ripped ưu tiên A, lỗi khác B, hợp lệ không thấy lỗi trên mặt đang kiểm C đi thẳng; HOLD không là khay | Thay D05 cho phương án mới. Barcode thiếu/nhiều mã không chặn AI; UUID một job; ACK không là actual_route; STOP cần người vận hành xử lý và xác nhận |
| D22 | ĐÃ DUYỆT, CHƯA TRIỂN KHAI: Colab GPU fine-tune yolo11n.pt; validation chọn F2 Ripped/F1 lớp khác; CPU Python3.11 riêng để inference | Không thay môi trường collector. Model, threshold và dataset phải có version; chưa có kết quả train/đánh giá hay cam kết accuracy |
| D23 | ĐÃ DUYỆT, CHƯA TRIỂN KHAI: inspect barcode1D bằng zxing-cpp, ROI ảnh gốc biên5%, giữ tỉ lệ/letterbox; desktop + simulator, không bắt buộc A6/QR/SQLite lookup | Thay yêu cầu D16/D17 cho luồng mới, giữ dữ liệu QR cũ; C chỉ phản ánh một mặt. Chưa triển khai HMI/firmware/GPIO/serial thật; giao diện/preview cũ không đổi trong bước đầu |
| D24 | ĐÃ DUYỆT: đồng bộ công cụ và split-reviewed-v1 cho team huấn luyện song song; n640 là baseline, thêm s640/n960 để thử | Yêu cầu trực tiếp 2026-11-11: đưa phần chưa đồng bộ lên GitHub để team tìm model phù hợp. Dataset CC BY4.0 ở Release asset, không commit ảnh/weights; cùng split/seed, tên lượt riêng và CSV validation. Test chỉ đánh giá cuối; chưa có cấu hình thắng hoặc nghiệm thu AI. [Hướng dẫn team](TEAM_TRAINING.md) |

## Trạng thái dữ liệu

QR: VALID_FORMAT, UNREADABLE, INVALID_NAMESPACE, INVALID_FORMAT, AMBIGUOUS. VALID_FORMAT chỉ xác nhận cú pháp. Identity: NOT_CHECKED, VALID, UNKNOWN_ID; chỉ lookup DB mới xác nhận danh tính.

AI quality dự kiến: PASS, REVIEW, DEFECT; chưa inference hoặc ảnh không đủ điều kiện thì quality để null. Route: A, B, HOLD, STOP. Job dự kiến: PENDING, RUNNING, WAIT_CONTROLLER, COMPLETE, FAULT, UNCONFIRMED.

## Điều kiện kỹ thuật cần xác minh

- Camera, ánh sáng, độ phân giải và ngưỡng chất lượng trên bộ bìa pilot.
- Board thực tế, pin map, điện áp/tải, sensor và feedback cơ cấu.
- Framing serial, checksum, timeout/retry và xử lý trùng yêu cầu.
- Phiên bản dataset/model, ngưỡng AI và tiêu chí nghiệm thu.

Cấu hình PlatformIO hiện là esp32dev + Arduino cho firmware mẫu. Chưa phải xác nhận pin map hoặc thiết kế điện của hệ thống.

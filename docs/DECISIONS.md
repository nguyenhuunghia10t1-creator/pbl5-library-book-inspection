# Quyết định thiết kế

Cập nhật: 2026-10-29.

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

## Trạng thái dữ liệu

QR: VALID_FORMAT, UNREADABLE, INVALID_NAMESPACE, INVALID_FORMAT, AMBIGUOUS. VALID_FORMAT chỉ xác nhận cú pháp. Identity: NOT_CHECKED, VALID, UNKNOWN_ID; chỉ lookup DB mới xác nhận danh tính.

AI quality dự kiến: PASS, REVIEW, DEFECT; chưa inference hoặc ảnh không đủ điều kiện thì quality để null. Route: A, B, HOLD, STOP. Job dự kiến: PENDING, RUNNING, WAIT_CONTROLLER, COMPLETE, FAULT, UNCONFIRMED.

## Điều kiện kỹ thuật cần xác minh

- Camera, ánh sáng, độ phân giải và ngưỡng chất lượng trên bộ bìa pilot.
- Board thực tế, pin map, điện áp/tải, sensor và feedback cơ cấu.
- Framing serial, checksum, timeout/retry và xử lý trùng yêu cầu.
- Phiên bản dataset/model, ngưỡng AI và tiêu chí nghiệm thu.

Cấu hình PlatformIO hiện là esp32dev + Arduino cho firmware mẫu. Chưa phải xác nhận pin map hoặc thiết kế điện của hệ thống.

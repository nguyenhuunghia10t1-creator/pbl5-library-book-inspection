# Nhận diện lỗi bìa

Trạm OK/NG dùng checkpoint phân loại ảnh do người dùng cung cấp. [Bộ suy luận](station.py) đọc xác suất theo tên lớp, kiểm tra bìa qua OpenCV và giữ dừng khi ảnh hoặc confidence chưa đạt. [Hướng dẫn lấy mẫu và đổi model](../../docs/INSPECTION_STATION.md).

Nhánh nghiên cứu detection rách/bẩn vẫn có dữ liệu và tiêu chí riêng. Mỗi kết quả vận hành của bộ phân loại lưu ảnh bìa, nhãn, confidence và checksum model.

Dataset, nhãn, split, weights và runs được quản lý ngoài mã nguồn. Chia dữ liệu theo cuốn/thiết kế bìa, giữ tập test cuối độc lập. [Quy định dữ liệu](../../data/README.md) · [Kế hoạch](../../docs/PLAN.md).

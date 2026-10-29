# Nhận diện lỗi bìa

Module AI dự kiến phát triển với YOLO11n cho hai lớp cover_tear và surface_stain. Hiện chưa có code train/inference hoặc model của dự án.

Đầu vào là ảnh bìa và metadata từ OpenCV; đầu ra là detection, loại lỗi và model version. Module không điều khiển GPIO hoặc tự xác nhận tuyến phân loại.

Dataset, nhãn, split, weights và runs được quản lý ngoài mã nguồn. Chia dữ liệu theo cuốn/thiết kế bìa, giữ tập test cuối độc lập. [Quy định dữ liệu](../../data/README.md) · [Kế hoạch](../../docs/PLAN.md).

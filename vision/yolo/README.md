# Nhận diện lỗi bìa

Phương án mới dùng YOLO11n và năm lớp Barcode, Notch, Ripped, Spot, Wornout của Damaged Books v1; Barcode không phải lỗi. Tag bị bỏ khỏi bản nhãn chuyển đổi, ảnh nguồn giữ nguyên.

Hiện có công cụ `prepare` (convert/audit/split) và `review` (trang rà ảnh ngoại tuyến). [Hướng dẫn và bằng chứng dataset](../../docs/DAMAGED_BOOKS_DATASET.md). Chưa có train/inference hoặc model lỗi sách đã huấn luyện trên nhánh này. Module không điều khiển GPIO hoặc tự xác nhận tuyến phân loại.

Dataset, nhãn, split, weights và runs được quản lý ngoài mã nguồn. Chia dữ liệu theo cuốn/thiết kế bìa, giữ tập test cuối độc lập. [Quy định dữ liệu](../../data/README.md) · [Kế hoạch](../../docs/PLAN.md).

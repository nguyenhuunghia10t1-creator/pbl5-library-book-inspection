# Nhận diện lỗi bìa

Phương án mới dùng YOLO11n và năm lớp Barcode, Notch, Ripped, Spot, Wornout của Damaged Books v1; Barcode không phải lỗi. Tag bị bỏ khỏi bản nhãn chuyển đổi, ảnh nguồn giữ nguyên.

Hiện có công cụ `prepare` (convert/audit/split), `review` (trang rà ảnh ngoại tuyến) và [notebook Colab](../../notebooks/damaged_books_colab.ipynb) để fine-tune YOLO11n. [Cách chạy Colab](../../docs/COLAB_TRAINING.md) · [Hướng dẫn dataset](../../docs/DAMAGED_BOOKS_DATASET.md). Chưa chạy phiên GPU hoặc có model lỗi sách đã nghiệm thu trên nhánh này. Notebook chỉ train/validation; chưa chọn ngưỡng hay đánh giá test. Module không điều khiển GPIO hoặc tự xác nhận tuyến phân loại.

Dataset, nhãn, split, weights và runs được quản lý ngoài mã nguồn. Chia dữ liệu theo cuốn/thiết kế bìa, giữ tập test cuối độc lập. [Quy định dữ liệu](../../data/README.md) · [Kế hoạch](../../docs/PLAN.md).

[Team chạy song song](../../docs/TEAM_TRAINING.md): notebook tải dataset khóa SHA từ GitHub Releases, hỗ trợ n640/s640/n960, ghi mã thành viên và CSV so sánh validation. Chưa có kết quả train thực trong lần phát hành công cụ này.

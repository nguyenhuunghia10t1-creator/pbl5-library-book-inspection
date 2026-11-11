# Chạy thí nghiệm song song

Mỗi người dùng một phiên Google Colab và Google Drive riêng. Tất cả dùng cùng notebook và cùng dataset đã khóa checksum; các lượt chạy được phân biệt bằng mã thành viên, cấu hình và thời gian UTC.

- [Mở notebook trên Colab](https://colab.research.google.com/github/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/blob/feat/damaged-books-colab/notebooks/damaged_books_colab.ipynb)
- [Dataset và thông tin phát hành](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/releases/tag/damaged-books-reviewed-v1)
- [Hướng dẫn từng bước](COLAB_TRAINING.md)

## Chia việc

| Người chạy | `TEAM_MEMBER` ví dụ | `EXPERIMENT` | Model đầu vào | Kích thước |
|---|---|---|---|---|
| Người 1 | `member01` | `n640` | `yolo11n.pt` | 640 |
| Người 2 | `member02` | `s640` | `yolo11s.pt` | 640 |
| Người 3 | `member03` | `n960` | `yolo11n.pt` | 960 |

Đây là ba lượt thử ban đầu, chưa có kết quả xác định cấu hình tốt nhất. Ảnh nguồn chỉ 640×640; cấu hình 960 là thử đổi kích thước đầu vào, không tạo thêm chi tiết ảnh gốc. Nếu team hai người, chạy n640 và s640 trước. Không cần tạo nhánh Git riêng chỉ để chạy notebook.

Mở notebook, chọn GPU, sửa hai biến trên tại bước 2 rồi chạy từ trên xuống. Dataset tự tải từ GitHub Releases; không chia lại train/val/test. Các cấu hình giữ epochs=100, patience=20, batch=16, seed=42 và AdamW. Khi hết VRAM có thể đặt `BATCH_SIZE=8`; phải ghi nhận khác biệt này khi so sánh.

## Thu và so sánh kết quả

1. Mỗi người tải ZIP artifacts, giữ `best.pt`, `last.pt`, `results.csv`, confusion matrix, `validation-metrics.json`, `environment.json`, `train/args.yaml` và `experiment-summary.csv`.
2. Gửi ZIP/CSV vào thư mục chia sẻ mà team thống nhất; notebook không tự đăng kết quả hay nhắn cho thành viên khác.
3. Đối chiếu cùng dataset SHA/version, phiên bản thư viện và cấu hình thực tế. Xem precision/recall Ripped, mAP50–95 và confusion matrix; cân nhắc kích thước model. Chỉ số precision/recall Ultralytics chưa phải kết quả tại ngưỡng vận hành đã hiệu chỉnh.
4. Thu hẹp ứng viên bằng validation; chọn ngưỡng F2 cho Ripped, F1 cho lớp khác ở bước sau. Chốt model/ngưỡng trước khi đánh giá test cuối. Nếu cần chọn model chạy nhanh, đo các ứng viên trên cùng máy đích; tốc độ GPU khác nhau không so trực tiếp.

`experiment-summary.csv` ghi thành viên, cấu hình, seed, GPU, phiên bản, hash model/dataset và chỉ số validation. Không dùng test để xếp hạng mỗi lần train. Chưa có model thực hoặc kết quả camera trong lần phát hành công cụ này.

## Dữ liệu dùng chung

361 ảnh đã duyệt: train253/val54/test54,121 nhóm;259 ảnh nghi vấn/chưa rõ nhóm được giữ ngoài split. Dataset version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`, SHA256 ZIP `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`.

Nguồn: [Damaged Books v1, Roboflow user atcom21-gmail-com](https://universe.roboflow.com/atcom21-gmail-com/damaged-books/dataset/1), giấy phép [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Bản này bỏ dòng Tag, đổi Wornout5→4 và chia lại theo nhóm; ảnh vẫn giữ nội dung nguồn. Dữ liệu được phát hành dưới dạng release asset, không đưa ảnh/weights vào lịch sử Git.

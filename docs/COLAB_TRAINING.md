# Huấn luyện bản đầu trên Google Colab

Notebook độc lập: [damaged_books_colab.ipynb](../notebooks/damaged_books_colab.ipynb).
Không cần clone repository hoặc cài thêm thư viện vào môi trường collector.

## Cách chạy

1. Vào <https://colab.research.google.com/>, chọn **File → Upload notebook**, tải notebook trên.
2. Chọn **Runtime → Change runtime type → T4 GPU** (hoặc GPU khả dụng), lưu.
3. Chạy từng ô từ trên xuống. Dataset tự tải từ [GitHub Release](https://github.com/nguyenhuunghia10t1-creator/pbl5-library-book-inspection/releases/tag/damaged-books-reviewed-v1) và kiểm SHA256. Nếu cần tải thủ công, đổi `DATA_SOURCE='upload'`, chọn `split-reviewed-v1.zip`. Không dùng ZIP Roboflow gốc.
4. Tại bước 2, sửa `TEAM_MEMBER` và chọn `EXPERIMENT` (`n640`, `s640`, `n960`); xem [phân công team](TEAM_TRAINING.md). Cho phép notebook kết nối Drive để lưu checkpoint ở `MyDrive/SmartVision/damaged-books/<thành viên>-<cấu hình>-<phiên>`. Nếu không dùng Drive, đổi `USE_DRIVE=False` và tải kết quả trước khi đóng runtime.
5. Chạy ô huấn luyện, rồi ô báo cáo/tải ZIP kết quả. Gửi `validation-metrics.json` và giữ toàn bộ ZIP để tiếp tục chọn ngưỡng.

## Cấu hình và đầu ra

- Mặc định fine-tune `yolo11n.pt`/640; có thêm `yolo11s.pt`/640 và `yolo11n.pt`/960 để team thử song song. Ultralytics `8.4.208`, epochs tối đa 100, patience 20, batch 16, seed 42, AdamW. Cấu hình thực tế ở `train/args.yaml`; phiên bản Python/Torch/CUDA/GPU và `pip freeze` được lưu cùng kết quả.
- Gói được khóa bằng SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`, version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`.
- Kiểm 253/54/54 ảnh, năm lớp, checksum từng tệp, nhóm/ảnh không giao nhau và ảnh cách ly không lọt vào split. Kiểm cấu trúc không thay thế việc rà nhãn/nhận diện cùng sách bằng mắt.
- ZIP kết quả gồm `train/weights/best.pt`, checkpoint, `model-metadata.json`, `validation-metrics.json`, `experiment-summary.csv`, confusion matrix, `results.csv`, cấu hình, split manifest và phiên bản thư viện.
- Nếu hết VRAM, tạo phiên mới với batch 8. Nếu Colab mất kết nối, giữ `last.pt` trên Drive để phục hồi; không chạy lại ô tạo phiên rồi cho rằng đó là resume.
- Có notebook không đồng nghĩa đã train: GPU Colab, tải pretrained weights, kết quả AI và độ trễ máy hiện tại chưa được nghiệm thu khi chỉ kiểm tra cục bộ.

## Giới hạn của bước này

Notebook chỉ dùng train/val; YAML chạy không chứa đường dẫn test. Chưa chọn ngưỡng, metadata ghi `thresholds=null`, `threshold_status=not_calibrated`, `test_evaluated=false`, `camera_domain_accepted=false`. Không đưa model này vào ứng dụng phân tuyến ngay.

Bước sau: chọn ngưỡng trên validation (F2 cho Ripped, F1 cho các lớp khác), chốt model/cấu hình rồi đánh giá test một lần. Thử riêng sách trường dưới camera thực tế trước khi kết luận khả năng áp dụng.

Nguồn dữ liệu: [Damaged Books v1](https://universe.roboflow.com/atcom21-gmail-com/damaged-books/dataset/1), CC BY 4.0. Barcode không phải lỗi; các lớp còn lại là Notch/Ripped/Spot/Wornout. Giấy phép phần mềm Ultralytics theo nhà cung cấp (AGPL-3.0 / thương mại).

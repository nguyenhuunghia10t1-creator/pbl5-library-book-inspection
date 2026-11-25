# Báo cáo phân tích kết quả huấn luyện YOLO11n lần 1 (Colab), bảng rà 20 ảnh và kế hoạch lần 2

Ngày phân tích & cập nhật: `2026-11-11`<br>
Mã phiên huấn luyện: `20261111T132200647414Z` (`yolo11n-five-20261111T132200647414Z`)<br>
Công cụ phân tích tái lập: [analyze_colab_run.py](../scripts/analyze_colab_run.py) · [analyze_damaged_books_run.py](../scripts/analyze_damaged_books_run.py)<br>
Tài liệu đối chiếu liên quan: [DAMAGED_BOOKS_RUN1_ANALYSIS.md](DAMAGED_BOOKS_RUN1_ANALYSIS.md) · [DAMAGED_BOOKS_RUN1_TABLES.md](DAMAGED_BOOKS_RUN1_TABLES.md) · [PROGRESS.md](../PROGRESS.md) · [PLAN.md](PLAN.md) · [DECISIONS.md](DECISIONS.md)

**Bổ sung sau lượt rà độc lập 20 ảnh:** [quy tắc nhãn đã duyệt](DAMAGED_BOOKS_ANNOTATION_RULES.md) và [đề xuất từng hộp](reviews/damaged_books_review20.json) là căn cứ cho lượt rà hiện tại. Có 32 thao tác sửa được đề xuất; 17 ảnh còn câu hỏi, trong đó 9 ảnh ưu tiên phân biệt Ripped với lỗi khác. Chưa áp dụng đề xuất vào nhãn nguồn, chưa tạo v2 hoặc train. Nhận xét ở bảng Mục 6 là hồ sơ lượt trước; đặc biệt ảnh #20 không còn được coi là "mẫu âm chuẩn" vì phần giấy/lớp bọc nhô ở mép phải chưa rõ.

`audit_20_manifest_verified` trong JSON của script phân tích là **danh sách 20 bản ghi**, không phải boolean `true` hay hàm duyệt nhãn. Nó kiểm đường dẫn/nhóm/số hộp, không chứng minh quan sát trực quan hoặc phê duyệt của người vận hành.

**Lưu ý trước khi triển khai pilot:** đổi `epochs=100` thành `15` đồng thời đổi lịch learning rate và thời điểm tắt mosaic (`close_mosaic=10`); không được kết luận đây là phép thử chỉ đổi LR so với Run 1. Cần hai pilot có cùng lịch/số epoch hoặc giữ lịch 100 và quan sát cùng số epoch đầu ở lượt đối chứng. Giới hạn loss `>10` chỉ là tín hiệu cần xem log, không phải bằng chứng nguyên nhân NaN. Phần pilot bên dưới vẫn là đề xuất chưa thực hiện.

---

## 1. Giải nén và kiểm kê gói kết quả Colab

- **Tệp ZIP gốc (giữ nguyên, không sửa đổi):** `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip`
  - Kích thước: `261.671.829` bytes (`~249,55 MB`)
  - SHA256: `b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866`
- **Thư mục giải nén:** `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts`
- **Xác nhận `.gitignore`:** Lệnh `git check-ignore -v` xác nhận cả tệp ZIP, thư mục giải nén và tệp JSON phân tích đều bị bỏ qua bởi quy tắc `.gitignore:21:/data/*`.
- **Danh mục 54 tệp và 3 thư mục con đã giải nén:**

| Nhóm | Đường dẫn tương đối trong thư mục giải nén | Số tệp | Kích thước / Ghi chú |
|---|---|---:|---|
| Metadata & cấu hình gốc | `environment.json`, `initial-weights.json`, `model-metadata.json`, `requested-config.json`, `requirements-frozen.txt`, `split-check.json`, `split_manifest.json`, `train-val.yaml`, `training-status.json`, `validation-metrics.json` | 10 | Đầy đủ thông tin môi trường, SHA256 dataset/weights, kết quả `val` |
| Cấu hình & log quá trình train (`train/`) | `train/args.yaml`, `train/results.csv`, `train/results.png`, `train/labels.jpg` | 4 | `results.csv` gồm 100 dòng ứng với 100 epochs (`475,19s`) |
| Đồ thị & ma trận nhầm lẫn lúc kết thúc train (`train/`) | `train/BoxF1_curve.png`, `train/BoxPR_curve.png`, `train/BoxP_curve.png`, `train/BoxR_curve.png`, `train/confusion_matrix.png`, `train/confusion_matrix_normalized.png` | 6 | Sinh tự động ở cuối `model.train()` |
| Ảnh mẫu batch lúc train (`train/`) | `train/train_batch0.jpg`, `train/train_batch1.jpg`, `train/train_batch2.jpg`, `train/train_batch1440.jpg`, `train/train_batch1441.jpg`, `train/train_batch1442.jpg`, `train/val_batch0_labels.jpg`, `train/val_batch0_pred.jpg`, `train/val_batch1_labels.jpg`, `train/val_batch1_pred.jpg` | 10 | `train_batch0..2` có mosaic; `train_batch1440..1442` ở 10 epoch cuối (`close_mosaic=10`) |
| Trọng số mô hình (`train/weights/`) | `best.pt` (`5.516.378` B), `last.pt` (`5.516.378` B), `epoch0.pt`, `epoch10.pt`, `epoch20.pt`, `epoch30.pt`, `epoch40.pt`, `epoch50.pt`, `epoch60.pt`, `epoch70.pt`, `epoch80.pt`, `epoch90.pt` | 12 | `best.pt` SHA256: `eb76c53172f91189cb78191470f73b7efa4560a71f51616f934df74f3ac80a4f` |
| Đánh giá độc lập lại trên tập `val` (`validation/`) | `validation/BoxF1_curve.png`, `validation/BoxPR_curve.png`, `validation/BoxP_curve.png`, `validation/BoxR_curve.png`, `validation/confusion_matrix.png`, `validation/confusion_matrix_normalized.png`, `validation/val_batch0_labels.jpg`, `validation/val_batch0_pred.jpg`, `validation/val_batch1_labels.jpg`, `validation/val_batch1_pred.jpg`, `validation/val_batch2_labels.jpg`, `validation/val_batch2_pred.jpg` | 12 | Sinh từ lệnh `trained.val(..., split='val', batch=16)` (hiển thị 48/54 ảnh `val` trên 3 mosaic 4×4) |

---

## 2. Cấu hình huấn luyện và môi trường thực tế

Đọc trực tiếp từ `environment.json`, `initial-weights.json`, `requested-config.json`, `train/args.yaml` và `requirements-frozen.txt`:

| Nhóm tham số | Giá trị thực tế | Nhận xét kỹ thuật |
|---|---|---|
| Phần cứng & Hệ thống | GPU `Tesla T4`, CUDA `13.0`, Python `3.13.16` | Chạy trên Google Colab GPU |
| Thư viện chính | `ultralytics==8.4.208`, `torch==2.14.1+cu130`, `torchvision==0.29.1+cu130`, `opencv-python==5.0.0.93`, `numpy==2.4.6`, `pillow==11.3.0`, `pyyaml==6.0.3` | Đã khóa phiên bản trong `requirements-frozen.txt` |
| Dataset đầu vào | `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd` (ZIP SHA256 `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`) | Khớp 100% với gói `split-reviewed-v1` (`253` train / `54` val / `54` test; `test` không nằm trong `train-val.yaml`) |
| Trọng số khởi tạo | `yolo11n.pt` (SHA256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`, `pretrained: true`, `cls_remap: true`) | Trọng số pretrained COCO chuẩn |
| Kích thước & Batch | `imgsz: 640`, `batch: 16`, `rect: false`, `multi_scale: 0.0`, `workers: 2`, `amp: true` | Hỗn hợp độ chính xác FP16 (`amp: true`) |
| Số epoch & dừng sớm | `epochs: 100`, `patience: 20`, `save_period: 10`, `seed: 42`, `deterministic: true` | Chạy đủ 100 epochs (`475,19s`), không bị ngắt bởi `patience=20` |
| **Optimizer & Learning Rate** | `optimizer: AdamW`, `lr0: 0.01`, `lrf: 0.01`, `cos_lr: false`, `momentum: 0.937`, `weight_decay: 0.0005`, `warmup_epochs: 3.0`, `warmup_momentum: 0.8`, `warmup_bias_lr: 0.1`, `nbs: 64` | Khi đặt tường minh `optimizer='AdamW'` mà không truyền `lr0`, Ultralytics giữ `lr0=0.01` từ `default.yaml` (cao hơn mức heuristic `lr0=0.001111` của `optimizer='auto'` cho 5 lớp). Đây là ứng viên giả thuyết chính cần kiểm chứng đối với hiện tượng `NaN` đầu kỳ. |
| Trọng số hàm mục tiêu | `box: 7.5`, `cls: 0.5`, `dfl: 1.5`, `cls_pw: 0.0` | Mặc định Ultralytics |
| **Augmentation thực tế trong `detect`** | `mosaic: 1.0`, `close_mosaic: 10`, `scale: 0.5`, `translate: 0.1`, `fliplr: 0.5`, `flipud: 0.0`, `degrees: 0.0`, `shear: 0.0`, `perspective: 0.0`, `mixup: 0.0`, `cutmix: 0.0`, `copy_paste: 0.0`, `hsv_h: 0.015`, `hsv_s: 0.7`, `hsv_v: 0.4` | Trong `ultralytics 8.4.208`, pipeline detection `v8_transforms` (`ultralytics/data/dataset.py:342`, `augment.py:2835`) chỉ dùng các phép biến đổi này (cùng Albumentations nhẹ mặc định). Hai khóa `erasing: 0.4` và `auto_augment: randaugment` tuy có mặt trong `args.yaml` nhưng chỉ dùng cho `classify` (`dataset.py:1335`), **không áp dụng trong detection**. |
| Tham số `val` / NMS | `conf: null` (mặc định `0.001` khi tính mAP và confusion matrix), `iou: null` (mặc định `0.7` cho NMS), `max_det: 300`, `agnostic_nms: false` | Ngưỡng hiển thị ảnh `val_batch*_pred.jpg` mặc định là `conf > 0.25` |

### Các thông tin thiếu hoặc không được ghi trong artifacts
1. **Thiếu console log chi tiết về transfer weights, `GradScaler`/AMP và norm gradient:** Không có log cảnh báo `NaN` từng batch hay trạng thái `GradScaler` ở epoch 1–10.
2. **Thiếu lịch sử AP/Recall từng lớp theo từng epoch:** `train/results.csv` chỉ lưu trung bình cộng 5 lớp (`metrics/precision(B)`, `metrics/recall(B)`, `metrics/mAP50(B)`, `metrics/mAP50-95(B)`).
3. **Thiếu mảng số của đường cong PR/F1 và raw predictions từng ảnh:** Các đường cong `BoxPR_curve.png`, `BoxF1_curve.png`, `BoxP_curve.png`, `BoxR_curve.png` chỉ được xuất dưới dạng ảnh PNG; `model-metadata.json` ghi `"thresholds": null`, `"threshold_status": "not_calibrated"`.

---

## 3. Phân tích số liệu validation, đường cong huấn luyện và ma trận nhầm lẫn

### 3.1. Bảng kết quả từng lớp trên tập `val` (`54` ảnh, `18` nhóm, `327` instances)

Đối chiếu `validation-metrics.json` với kết quả đếm trực tiếp từ 54 tệp nhãn `val/labels/*.txt` và `split_manifest.json`:

| ID | Lớp (`names`) | Vai trò theo `D20–D21` | Số ảnh có mặt (`/54`) | Số nhóm sách (`/18`) | Số instance `val` (`/327`) | Tỷ trọng instance `val` | Precision (`P` tại điểm F1 chung `~0.350`) | Recall (`R` tại điểm F1 chung `~0.350`) | `AP@50` (tích phân PR) | `AP@50:95` (tích phân PR) |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `0` | `Barcode` | Mã vạch 1D | 25 (`46,30%`) | 11 | 25 | `7,65%` | `69,283%` | `76,000%` (`19/25`) | `68,003%` | `42,922%` |
| `1` | `Notch` | Lỗi khuyết/sứt (Khay B) | 22 (`40,74%`) | 10 | 53 | `16,21%` | `100,000%`* | `0,000%` (`0/53`) | `0,090%` | `0,027%` |
| `2` | `Ripped` | Lỗi rách (**ưu tiên Khay A**) | 25 (`46,30%`) | 9 | 39 | `11,93%` | `72,558%` | `2,564%` (`1/39`) | `5,633%` | `3,606%` |
| `3` | `Spot` | Lỗi bẩn/ố (Khay B) | 23 (`42,59%`) | 12 | 65 | `19,88%` | `100,000%`* | `0,000%` (`0/65`) | `2,587%` | `1,057%` |
| `4` | `Wornout` | Lỗi mòn/sờn (Khay B) | 42 (`77,78%`) | 16 | 145 | `44,34%` | `100,000%`* | `0,000%` (`0/145`) | `4,526%` | `1,211%` |
| — | **Tổng hợp (Macro 5 lớp)** | — | **54** (48 có hộp lỗi, 6 không lỗi) | **18** | **327** (302 hộp lỗi) | `100,00%` | **`88,368%`*** | **`15,713%`** | **`16,168%`** | **`9,765%`** |
| — | **Trung bình riêng 4 lớp lỗi** | `Notch`, `Ripped`, `Spot`, `Wornout` | **48** (`88,89%`) | **17** | **302** | `92,35%` | — | **`0,641%`** | **`3,209%`** | **`1,475%`** |

> **Phân biệt `AP@50` / `AP@50:95` và cặp `Precision`/`Recall` đơn điểm (`*`):**
> - **`AP@50` và `AP@50:95`** là diện tích dưới đường cong Precision–Recall tích phân dọc toàn bộ dải ngưỡng confidence (từ `conf=0.001`), **không phụ thuộc vào ngưỡng `0.350`**. Việc `AP@50` của 4 lớp lỗi chỉ đạt `0,090%–5,633%` chứng tỏ chất lượng phát hiện lỗi của mô hình đã rất thấp trên toàn bộ đường cong PR, không phải chỉ do chọn sai ngưỡng.
> - **Cặp `Precision` và `Recall` báo cáo trong `validation-metrics.json`** là giá trị nội suy tại **một ngưỡng confidence chung duy nhất** tối đa hóa đường cong $F_1$ trung bình 5 lớp (`smooth(f1_curve.mean(0), 0.1).argmax()`, đọc trên `validation/BoxF1_curve.png` là `all classes 0.15 at 0.350`). Tại ngưỡng `~0.350` này, ba lớp **`Notch`, `Spot`, `Wornout`** không có dự đoán nào vượt ngưỡng (`Recall = 0,000%`), trong khi **`Ripped` đạt `Recall = 2,564%` (`1/39`)** và `Barcode` đạt `76,000%`. Do `ultralytics/utils/metrics.py` nội suy đường cong precision với `left=1.0`, ba lớp có `Recall = 0%` nhận `Precision = 100,000%`, kéo `Mean Precision` lên `88,368%`.

### 3.2. Phân tích đường cong huấn luyện (`train/results.csv` và `train/results.png`)

1. **`[Bằng chứng]` Bất ổn số học đầu kỳ (Epoch 1–10):**
   - Từ epoch 1 đến epoch 8 và tại epoch 10, cả ba cột `val/box_loss`, `val/cls_loss`, `val/dfl_loss` trong `results.csv` đều là **`nan`**, `metrics/mAP50(B) = 0`.
   - Tại epoch 9 (epoch duy nhất có `val_loss` hữu hạn trong 10 epoch đầu), `val/cls_loss` vọt lên **`587,034`** (`val/box_loss = 4,4192`, `val/dfl_loss = 4,3714`).
   - **`[Giả thuyết]` về cơ chế gây `NaN`:** `AdamW` với `lr0 = 0.01`, `warmup_bias_lr = 0.1` (tạo `lr/pg2 = 0.071875` ở epoch 1) và/hoặc `amp = true` (FP16) có thể gây tràn số hoặc bước nhảy lớn ở đầu quá trình train. Cần kiểm chứng bằng pilot ngắn đổi từng biến (`lr0`, `warmup_bias_lr`, `amp`) trước khi kết luận nhân quả.
2. **`[Bằng chứng]` Giai đoạn phục hồi chậm (Epoch 11–81):**
   - Khi learning rate giảm tuyến tính từ `0,00901` (epoch 11) xuống `0,00208` (epoch 81), `val/box_loss` giảm từ `4,681` xuống `2,561`; `mAP50` tăng từ `0,004%` lên `15,72%` (chủ yếu do học được lớp `Barcode`).
3. **`[Bằng chứng]` Giai đoạn cuối (Epoch 82–100):**
   - **Đỉnh `mAP50`** trong `results.csv` đạt tại **epoch 82** với `mAP50 = 17,435%` (`0,17435`), `mAP50-95 = 9,756%`, và `val/cls_loss` đạt mức thấp nhất là `2,96224`.
   - **Đỉnh `mAP50-95`** đạt tại **epoch 97** với `mAP50-95 = 9,852%` (`mAP50 = 16,116%`, `val/box_loss` thấp nhất `2,55846`).
   - Trung bình cửa sổ epoch `81–90` so với `91–100`: `mAP50` giảm nhẹ `15,684% -> 15,402%`, trong khi `mAP50-95` nhích nhẹ `8,937% -> 9,067%` và `val/box_loss` giảm nhẹ `2,5962 -> 2,5771`. Như vậy `mAP50` đã chững lại ở 20 epoch cuối trong khi `mAP50-95` chỉ còn cải thiện rất nhỏ.

### 3.3. Đường cong PR/F1 và Ma trận nhầm lẫn (`validation/confusion_matrix*.png`)

Bảng số liệu đọc trực tiếp từ `validation/confusion_matrix.png` và `validation/confusion_matrix_normalized.png` (ghép cặp ở ngưỡng mặc định thấp của `DetectionValidator`, `conf = 0.001`, `IoU = 0.5`):

| Dự đoán (Predicted) \ Nhãn thật (True) | `Barcode` (`25` GT) | `Notch` (`53` GT) | `Ripped` (`39` GT) | `Spot` (`65` GT) | `Wornout` (`145` GT) | `background` (FP không khớp GT) |
|---|---:|---:|---:|---:|---:|---:|
| **Dự đoán là `Barcode`** | **22 (`88,0%`)** | 0 (`0,0%`) | 0 (`0,0%`) | 0 (`0,0%`) | 0 (`0,0%`) | 288 (`1,8%`) |
| **Dự đoán là `Notch`** | 0 (`0,0%`) | **3 (`5,7%`)** | 4 (`10,3%`) | 2 (`3,1%`) | 6 (`4,1%`) | 3.504 (`22,0%`) |
| **Dự đoán là `Ripped`** | 0 (`0,0%`) | 1 (`1,9%`) | **14 (`35,9%`)** | 0 (`0,0%`) | 9 (`6,2%`) | 1.848 (`11,6%`) |
| **Dự đoán là `Spot`** | 0 (`0,0%`) | 5 (`9,4%`) | 1 (`2,6%`) | **15 (`23,1%`)** | 5 (`3,4%`) | 3.822 (`24,0%`) |
| **Dự đoán là `Wornout`** | 0 (`0,0%`) | 4 (`7,5%`) | **12 (`30,8%`)** | 1 (`1,5%`) | **70 (`48,3%`)** | **6.491 (`40,7%`)** |
| **Không ghép được detection (`background` FN)** | **3 (`12,0%`)** | **40 (`75,5%`)** | **8 (`20,5%`)** | **47 (`72,3%`)** | **55 (`37,9%`)** | — |
| **Tổng cột** | **25 (`100%`)** | **53 (`100%`)** | **39 (`100%`)** | **65 (`100%`)** | **145 (`100%`)** | **15.953 (`100%`)** |

**Hai hiện tượng có bằng chứng trực tiếp từ Confusion Matrix:**
1. **`Notch` (`40/53 = 75,5%`) và `Spot` (`47/65 = 72,3%`) chủ yếu bị bỏ sót thành `background` ngay cả ở ngưỡng rất thấp**, đồng thời mô hình sinh ra `15.953` dự đoán không khớp GT (gần chạm trần `max_det = 300` × 54 ảnh) do điểm tự tin của các hộp lỗi lẫn vào nhiễu nền.
2. **Nhầm lẫn chéo mạnh giữa các lớp lỗi mép/rách (`Ripped` ↔ `Wornout` / `Notch`):** Trong `39` hộp `Ripped` của tập `val`, có `14` hộp đoán đúng là `Ripped`, nhưng có tới **`12` hộp (`30,8%`) bị đoán thành `Wornout`**, **`4` hộp (`10,3%`) thành `Notch`**, `1` hộp thành `Spot`, và chỉ `8` hộp (`20,5%`) hoàn toàn không ghép được detection.

---

## 4. Phân tích định lượng Dataset từ tệp nhãn (`train` & `val`)

Số liệu dưới đây được tính trực tiếp từ `253` tệp nhãn `train/labels/*.txt`, `54` tệp nhãn `val/labels/*.txt` và `split_manifest.json` (không đọc tập `test`).

### 4.1. Tổng quan số ảnh, số nhóm, mẫu âm và tính nhất quán `data.yaml`

- **Đối chiếu `data.yaml`, `train-val.yaml`, `model-metadata.json` và `split_manifest.json`:** Khớp tuyệt đối 5 lớp `0: Barcode`, `1: Notch`, `2: Ripped`, `3: Spot`, `4: Wornout`. Tất cả `1.399` dòng nhãn ở `train` và `327` dòng nhãn ở `val` đều hợp lệ (`invalid_class_id_count = 0`).
- **Độ phân giải ảnh:** `100%` ảnh ở `train` (`253/253`) và `val` (`54/54`) có kích thước `640×640` pixel.
- **Ảnh nhãn rỗng (`empty labels`) và ảnh không có nhãn lỗi (`no damage`, chỉ có `Barcode` hoặc rỗng):**
  - `train` (`253` ảnh, `83` nhóm): **14 ảnh nhãn rỗng** (`5,53%`) + **9 ảnh chỉ có `Barcode`** (`3,56%`) = **23 ảnh không có nhãn lỗi** (`9,09%`).
  - `val` (`54` ảnh, `18` nhóm): **4 ảnh nhãn rỗng** (`7,41%`: `train__IMG_1011`, `train__IMG_1122`, `train__IMG_1225`, `train__IMG_1359`) + **2 ảnh chỉ có `Barcode`** (`3,70%`: `train__IMG_1074`, `train__IMG_1446`) = **6 ảnh không có nhãn lỗi** (`11,11%`).

| Lớp | Ảnh `train` (`/253`) | Nhóm `train` (`/83`) | Box `train` (`/1.399`) | Tỷ lệ box `train` | Ảnh `val` (`/54`) | Nhóm `val` (`/18`) | Box `val` (`/327`) | Tỷ lệ box `val` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `0: Barcode` | 77 (`30,43%`) | 41 | 77 | `5,50%` | 25 (`46,30%`) | 11 | 25 | `7,65%` |
| `1: Notch` | 97 (`38,34%`) | 45 | 250 | `17,87%` | 22 (`40,74%`) | 10 | 53 | `16,21%` |
| `2: Ripped` | 112 (`44,27%`) | 43 | 173 | `12,37%` | 25 (`46,30%`) | 9 | 39 | `11,93%` |
| `3: Spot` | 110 (`43,48%`) | 54 | 355 | `25,38%` | 23 (`42,59%`) | 12 | 65 | `19,88%` |
| `4: Wornout` | 184 (`72,73%`) | 74 | 544 | `38,88%` | 42 (`77,78%`) | 16 | 145 | `44,34%` |
| **Tổng cộng** | **253** | **83** | **1.399** | **`100,00%`** | **54** | **18** | **327** | **`100,00%`** |

### 4.2. Phân bố kích thước Bounding Box theo lớp (chuẩn hóa & pixel tại `imgsz=640`)

*(Bảng phân vị `P05 / P50 / P95` đầy đủ được lưu tại [DAMAGED_BOOKS_RUN1_TABLES.md](DAMAGED_BOOKS_RUN1_TABLES.md); dưới đây là bảng phân vị `min / p10 / p25 / p50 / p75 / p90 / max` và tỷ lệ diện tích `< 32² px²` từ `run1-analysis.json`)*

#### Tập `train` (`1.399` boxes)

| Lớp (`train`) | Đại lượng | `min` | `p10` | `p25` | `p50 (median)` | `p75` | `p90` | `max` | `mean` | Diện tích `< 32² px²` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`Barcode`** (`n=77`) | `px_w × px_h` (px) | `34,0×43,0` | `63,6×63,6` | `78,0×78,0` | **`156,0×106,0`** | `208,0×170,0` | `236,4×203,4` | `326,0×217,0` | `150,7×120,3` | **0 / 77 (`0,00%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `56,8` (`1,02`) | `89,0` (`1,22`) | `110,8` (`1,55`) | **`123,0`** (`2,35`) | `137,0` (`3,06`) | `155,2` (`3,18`) | `208,3` (`5,45`) | `123,7` (`2,35`) | Cạnh ngắn `<16px`: `0` |
| **`Notch`** (`n=250`) | `px_w × px_h` (px) | `7,0×6,0` | `17,0×15,0` | `28,0×20,0` | **`51,2×34,0`** | `91,8×57,8` | `160,2×109,3` | `453,0×278,5` | `74,0×49,8` | **78 / 250 (`31,20%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `13,2` (`1,00`) | `19,8` (`1,20`) | `28,3` (`1,51`) | **`42,3`** (`2,12`) | `67,7` (`3,69`) | `89,6` (`6,60`) | `216,3` (`24,18`) | `51,4` (`3,25`) | Cạnh ngắn `<16px`: `45` |
| **`Ripped`** (`n=173`) | `px_w × px_h` (px) | `15,0×10,0` | `25,0×23,2` | `32,0×29,0` | **`51,0×46,0`** | `86,0×70,0` | `168,8×124,0` | `579,0×393,0` | `80,1×63,3` | **29 / 173 (`16,76%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `12,2` (`1,00`) | `27,6` (`1,12`) | `33,8` (`1,32`) | **`46,0`** (`1,69`) | `77,1` (`2,41`) | `126,6` (`3,78`) | `235,2` (`13,87`) | `63,4` (`2,31`) | Cạnh ngắn `<16px`: `4` |
| **`Spot`** (`n=355`) | `px_w × px_h` (px) | `7,0×8,0` | `13,0×12,0` | `17,5×16,0` | **`24,0×22,0`** | `39,5×32,0` | `67,2×52,0` | `162,0×160,0` | `32,5×28,7` | **251 / 355 (`70,70%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `9,2` (`1,00`) | `13,4` (`1,07`) | `16,9` (`1,17`) | **`23,2`** (`1,43`) | `34,7` (`1,89`) | `48,4` (`2,53`) | `148,1` (`7,27`) | `29,1` (`1,70`) | Cạnh ngắn `<16px`: `115` |
| **`Wornout`** (`n=544`) | `px_w × px_h` (px) | `8,0×6,5` | `15,0×13,0` | `20,0×16,0` | **`34,0×26,0`** | `70,0×55,0` | `130,7×92,4` | `482,0×409,0` | `57,1×43,6` | **237 / 544 (`43,57%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `8,9` (`1,00`) | `18,2` (`1,22`) | `24,6` (`1,70`) | **`35,2`** (`3,06`) | `49,7` (`4,74`) | `66,3` (`7,43`) | `119,6` (`24,21`) | `39,2` (`3,86`) | Cạnh ngắn `<16px`: `159` |

#### Tập `val` (`327` boxes)

| Lớp (`val`) | Đại lượng | `min` | `p10` | `p25` | `p50 (median)` | `p75` | `p90` | `max` | `mean` | Diện tích `< 32² px²` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`Barcode`** (`n=25`) | `px_w × px_h` (px) | `35,0×57,0` | `48,8×60,2` | `81,0×66,0` | **`155,0×109,0`** | `203,0×147,0` | `222,6×181,6` | `247,0×214,0` | `145,2×115,2` | **0 / 25 (`0,00%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `61,8` (`1,02`) | `87,9` (`1,31`) | `99,3` (`1,67`) | **`115,7`** (`2,44`) | `137,2` (`3,07`) | `162,0` (`3,14`) | `177,1` (`4,84`) | `118,4` (`2,47`) | Cạnh ngắn `<16px`: `0` |
| **`Notch`** (`n=53`) | `px_w × px_h` (px) | `10,0×7,0` | `14,0×14,0` | `17,0×19,0` | **`30,0×36,0`** | `54,0×68,0` | `72,0×93,8` | `114,0×277,0` | `37,9×57,3` | **26 / 53 (`49,06%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `13,7` (`1,00`) | `15,5` (`1,30`) | `24,7` (`1,50`) | **`32,9`** (`2,12`) | `50,8` (`3,56`) | `76,6` (`5,98`) | `110,0` (`9,92`) | `40,1` (`2,92`) | Cạnh ngắn `<16px`: `15` |
| **`Ripped`** (`n=39`) | `px_w × px_h` (px) | `16,0×16,0` | `20,6×25,6` | `38,0×32,5` | **`51,0×48,0`** | `107,0×81,0` | `152,2×111,4` | `233,0×194,0` | `76,4×61,3` | **6 / 39 (`15,38%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `20,0` (`1,00`) | `29,3` (`1,10`) | `37,9` (`1,30`) | **`52,6`** (`1,66`) | `68,6` (`2,64`) | `125,3` (`3,32`) | `181,3` (`10,81`) | `63,9` (`2,23`) | Cạnh ngắn `<16px`: `0` |
| **`Spot`** (`n=65`) | `px_w × px_h` (px) | `10,0×10,0` | `13,0×13,4` | `17,0×17,0` | **`24,0×20,0`** | `35,0×30,0` | `56,2×53,8` | `111,0×80,0` | `30,7×27,0` | **48 / 65 (`73,85%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `11,8` (`1,00`) | `13,7` (`1,09`) | `17,5` (`1,24`) | **`23,3`** (`1,53`) | `32,4` (`2,00`) | `47,8` (`2,49`) | `78,1` (`3,58`) | `27,5` (`1,69`) | Cạnh ngắn `<16px`: `20` |
| **`Wornout`** (`n=145`) | `px_w × px_h` (px) | `7,0×9,0` | `14,4×13,0` | `22,0×16,0` | **`44,0×21,0`** | `88,0×32,0` | `136,6×62,2` | `486,0×333,0` | `69,2×34,9` | **67 / 145 (`46,21%`)** |
| | $\sqrt{\text{area}}$ (px) / Aspect | `9,5` (`1,00`) | `15,8` (`1,23`) | `23,8` (`1,50`) | **`34,3`** (`3,00`) | `48,1` (`5,50`) | `65,4` (`8,92`) | `126,0` (`40,50`) | `38,6` (`4,33`) | Cạnh ngắn `<16px`: `47` |

### 4.3. Kiểm tra Box bất thường, Mức độ tập trung theo nhóm và Độ độc lập giữa `train` và `val`

1. **Box tràn biên (`out_of_bounds`) hoặc diện tích ~0 (`< 16 px²` hoặc cạnh `< 4 px`):** `0` trường hợp ở cả `train` và `val`.
2. **Box dẹt cực đoan (`aspect_ratio = max(w/h, h/w) > 10:1`):**
   - Tập `train`: **37 hộp** (`25 Wornout`, `10 Notch`, `2 Ripped`; cực đại `24,21:1` trên `train__IMG_1118_jpg`).
   - Tập `val`: **12 hộp** (`11 Wornout`, `1 Ripped`; cực đại **`40,50:1`** = `486×12 px` trên `val/images/train__IMG_128_jpg.rf.e8f2e585c235d04383d46d45089b203e.jpg`).
3. **Box trùng lặp và chồng lấp nội ảnh:**
   - Trùng khít (`IoU >= 0.90`): `0` trường hợp.
   - Chồng lấp đáng kể (`IoU >= 0.25` hoặc tỷ lệ nằm trong hộp khác `IoA = inter / min(area1, area2) >= 0.50`): Có **19 cặp ở `train`** và **4 cặp ở `val`**, trong đó **4 cặp ở `train` và 1 cặp ở `val` có `IoA = 1.0000`** (một hộp con nằm lọt 100% bên trong hộp lớp khác: `val` có `train__IMG_1666_jpg` `Wornout` trong `Notch`; `train` có `train__IMG_1102_jpg` `Notch` trong `Ripped`, `train__IMG_1474_jpg` `Spot` trong `Notch`, `train__IMG_1634_jpg` `Notch` trong `Spot`, và `train__IMG_204_jpg` `Spot` trong `Barcode`).
4. **Kiểm tra trùng / gần trùng giữa `train` và `val`:**
   - **Giao nhau `group_id` trong `split_manifest.json`:** **`0` nhóm** (`83` nhóm `train` và `18` nhóm `val` hoàn toàn rời nhau).
   - **Trùng nội dung byte (`SHA256`) và pixel đã giải mã:** **`0`**.
   - **Sàng lọc `pHash` DCT 63-bit (`Hamming <= 8`):** **`0` cặp**.
   - **Sàng lọc `dHash` 64-bit (`OpenCV 5.0.0`, `cv2.IMREAD_GRAYSCALE` + `cv2.INTER_AREA`, `Hamming <= 10`) trong `scripts/analyze_colab_run.py`:** Có **5 cặp ứng viên** dưới đây. Đã mở trực tiếp toàn bộ 8 tệp ảnh gốc của 5 cặp này và xác nhận không có cặp nào là cùng một bức ảnh:

| STT | Ảnh `train` (`group_id`) | Ảnh `val` (`group_id`) | `dHash` Hamming | Quan sát sau khi mở trực tiếp hai ảnh gốc |
|---:|---|---|---:|---|
| 1 | `train__IMG_1746_jpg...` (`visual_group_045`) | `train__IMG_1436_jpg...` (`visual_group_063`) | `8` | `IMG_1746` là góc bìa xanh lá đậm trên nền xám; `IMG_1436` là gáy sách xanh da trời cầm tay (*당신이 알아야 할 한국사 10*, nhãn `900`). Khác sách. |
| 2 | `train__IMG_1050_jpg...` (`visual_group_064`) | `train__IMG_1436_jpg...` (`visual_group_063`) | `9` | `IMG_1050` là sách bìa đen *나는 어쩌다 명왕성을 죽였나* (nhãn vàng `400`); `IMG_1436` là sách xanh nhãn `900`. Khác sách. |
| 3 | `train__IMG_564_jpg...` (`visual_group_027`) | `train__IMG_1736_jpg...` (`visual_group_060`) | `9` | `IMG_564` là gáy sách đỏ chữ vàng đặt ngang; `IMG_1736` là gáy sách xanh lam *교육학개론* đặt ngang. Khác sách. |
| 4 | `train__IMG_154_jpg...` (`visual_group_029`) | `train__IMG_1011_jpg...` (`visual_group_013`) | `10` | `IMG_154` là gáy sách đen *엠마뉴엘 1* (nhãn xanh lá `800`); `IMG_1011` là gáy sách xanh tím *메타버스* (nhãn xanh dương `300`). Khác sách. |
| 5 | `train__IMG_1781_jpg...` (`visual_group_040`) | `train__IMG_1011_jpg...` (`visual_group_013`) | `10` | `IMG_1781` là gáy sách cam *BRITPOP* (nhãn xám `600`); `IMG_1011` là gáy sách xanh tím *메타버스* (nhãn `300`). Khác sách. |

   *(Lưu ý: `pHash`/`dHash` chỉ sàng lọc các góc chụp có bố cục độ sáng tương tự, không tự chứng minh độc lập tuyệt đối nếu cùng một cuốn sách được chụp ở mặt khác hoặc góc khác).*
5. **Mức độ tập trung cao theo nhóm sách trong tập `val`:**
   - Trong `54` ảnh `val` (`18` nhóm), chỉ riêng **3 nhóm sách nhiều nhãn nhất** (`visual_group_023`: `6` ảnh / `74` box; `visual_group_060`: `6` ảnh / `72` box; `visually_confirmed_same_book_001`: `5` ảnh / `40` box) đã gồm **`17 / 54` ảnh (`31,48%`)** và chiếm tới **`186 / 327` box (`56,88%`)** toàn bộ tập `val`. Do đó kết quả đánh giá trên `val` phụ thuộc mạnh vào vài cuốn sách có nhiều hộp nhãn.

---

## 5. Tổng hợp nguyên nhân theo mức độ bằng chứng và phép kiểm chứng

### 5.1. Các kết luận có `[Bằng chứng]` trực tiếp

1. **`[Bằng chứng]` Mô hình hiện tại thất bại trên 4 lớp lỗi:** Trên tập `val`, `AP@50` của `Notch`, `Ripped`, `Spot`, `Wornout` lần lượt chỉ đạt `0,090%`, `5,633%`, `2,587%`, `4,526%` (trung bình 4 lớp lỗi `3,209%`). Tại ngưỡng báo cáo chung `~0.350`, `Notch`, `Spot`, `Wornout` có `Recall = 0,000%` và `Ripped` có `Recall = 2,564%` (`1/39`).
2. **`[Bằng chứng]` `Precision` tổng hợp `88,368%` bị phóng đại bởi quy ước nội suy `left=1.0` tại ngưỡng chung `~0.350`:** Ba lớp `Notch`, `Spot`, `Wornout` không có dự đoán vượt ngưỡng `~0.350` nên nhận `P = 100%`, `R = 0%`.
3. **`[Bằng chứng]` Bất ổn số học ở 10 epoch đầu:** `val/box_loss`, `val/cls_loss`, `val/dfl_loss` bị `NaN` tại các epoch `1..8` và `10`, kèm spike `val/cls_loss = 587,034` ở epoch `9`.
4. **`[Bằng chứng]` Hộp nhãn `Spot` và `Wornout` rất nhỏ ở `imgsz=640`, trong khi nhãn còn thiếu/bất nhất ở một số mẫu đã mở:**
   - Trên `val`, trung vị cạnh ngắn của `Spot` và `Wornout` đều chỉ `18 px` (`73,85%` `Spot` và `46,21%` `Wornout` có diện tích `< 32² px²`). Tuy nhiên, `Ripped` chỉ có `15,38%` (`6/39`) diện tích `< 32² px²` và `0` hộp cạnh ngắn `< 16 px` nhưng vẫn bị bỏ sót hoặc nhầm sang `Wornout` (`12/39`) / `Notch` (`4/39`).
   - Đã xác nhận trực tiếp trên ảnh gốc và tệp nhãn: thiếu nhãn `Barcode` cho mã vạch ISBN nhìn thấy rõ trên `val/images/train__IMG_1174...` (`3` box: `2 Notch, 1 Wornout`), `val/images/train__IMG_1359...` (`0` box), `val/images/train__IMG_1330...` (chỉ gán 1/2 mã vạch), `train/images/train__IMG_1081...` (chỉ gán 1/2 mã vạch); và cùng một vết hỏng mép trên của cùng cuốn sách trong tập `val` (`visually_confirmed_same_book_001`) được gán `Ripped` ở `test__IMG_7_jpg` nhưng lại gán `Wornout` ở `train__IMG_1316_jpg`.

### 5.2. Các `[Giả thuyết]` và cách kiểm chứng rẻ nhất

| Mã | Giả thuyết | Căn cứ hiện có | Phép kiểm chứng rẻ nhất (tách biến) | Kết quả kỳ vọng nếu đúng |
|---|---|---|---|---|
| **H1** | `AdamW` với `lr0 = 0.01` (và/hoặc `warmup_bias_lr = 0.1`, `amp = true`) gây ra hiện tượng `val/*_loss = NaN` ở epoch 1–10. | `results.csv` có `NaN` ở epoch `1..8, 10` và `val/cls_loss = 587,034` ở epoch 9 khi `lr0 = 0.01`. | Chạy pilot ngắn `10–15 epoch` (`seed=42`, `batch=16`, `imgsz=640`, giữ nguyên augmentation Run 1): lượt **2A-1** chỉ đổi `lr0 = 0.001`; nếu còn bất ổn mới thử **2A-2** (`warmup_bias_lr = 0.0`) và **2A-3** (`amp = False`). | Toàn bộ `val/box_loss`, `val/cls_loss`, `val/dfl_loss` hữu hạn ngay từ epoch 1–15, không còn spike `> 10`. |
| **H2** | Sự thiếu nhất quán trong quy ước gán nhãn (`Ripped` vs `Wornout` vs `Notch`, băm nhỏ vs kéo dải dài `aspect > 10:1`, hộp lồng nhau `IoA = 1.0`, sót `Barcode` ISBN) làm mô hình nhầm lẫn giữa các lớp lỗi và với nền. | Confusion matrix (`12/39 Ripped -> Wornout`, `4/39 -> Notch`), `37` box `train` / `12` box `val` có `aspect > 10:1`, `5` cặp `IoA = 1.0`, và đối chiếu 20 ảnh gốc ở Mục 6. | Rà chung 20 ảnh (`8 train + 12 val`) để chốt quy tắc 1 trang, áp dụng làm sạch trên bản dataset mới `v2`, rồi chạy cùng một cấu hình model trên `v1` và `v2` (chấm cả hai trên cùng tập `val` đã chuẩn hóa). | Giảm nhầm lẫn `Ripped -> Wornout/Notch`, tăng `AP@50` và `Recall` của 4 lớp lỗi trên cùng tập đánh giá. |
| **H3** | Nhóm augmentation biến dạng hình học/màu sắc mạnh (`mosaic=1.0`, `scale=0.5`, `hsv_s=0.7`, `hsv_v=0.4`) làm suy giảm tín hiệu của các vết `Spot`/`Wornout` nhỏ (`trung vị cạnh ngắn 18 px`). | `73,85%` `Spot` và `46,21%` `Wornout` trên `val` có diện tích `< 32² px²`. | Sau khi cố định optimizer ổn định, so sánh gói augmentation nhẹ (`mosaic=0.2, close_mosaic=20, scale=0.2, translate=0.05, fliplr=0.0, hsv_s=0.3, hsv_v=0.2`) với augmentation Run 1 trên cùng dataset. | Cải thiện `AP@50` và `Recall` của nhóm box nhỏ (`Spot`, `Wornout`, `Notch`). |
| **H4** | Dung lượng đặc trưng của `yolo11n` hoặc độ phân giải đầu vào `imgsz=640` hạn chế khả năng tách lỗi mảnh khỏi chữ in/họa tiết bìa. | Baru có 1 lượt `yolo11n` ở `640`, chưa có mốc đối chứng `yolo11s` hay `960`. | So sánh đơn biến `model=yolo11s.pt` (giữ `imgsz=640, batch=16`) và thử nghiệm `imgsz=960` với baseline đã ổn định. | `yolo11s` hoặc `imgsz=960` tăng Recall lớp lỗi tại cùng sàn Precision. |
| **H5** | Gộp 3 lớp lỗi tuyến B (`Notch`, `Spot`, `Wornout`) thành `OtherDamage` trong một bộ nhãn dẫn xuất 3 lớp (`Barcode`, `Ripped`, `OtherDamage`) giúp giảm nhầm lẫn nội bộ mà vẫn giữ nguyên quy tắc điều hướng `D21` (`Ripped -> A`, `OtherDamage -> B`). | `Notch`, `Spot`, `Wornout` đều đi về Khay B theo `D21`. | Chỉ thử trên bản nhãn dẫn xuất sau khi chủ dự án duyệt (không sửa hợp đồng 5 lớp `D20`). | Tăng độ tin cậy định tuyến Khay A / Khay B so với khi tách rời 3 lớp lỗi nhẹ. |

### 5.3. Các vấn đề `[Chưa kiểm tra]`

1. **`[Chưa kiểm tra]` Khác biệt miền ảnh (Domain Shift) giữa bộ ảnh Roboflow Damaged Books và ảnh thực tế trên line của dự án:**
   - Theo quyết định kiến trúc hiện hành `D20–D24` (DECISIONS.md (hồ sơ cục bộ)), hệ thống sử dụng **ROI cuốn sách từ ảnh gốc cộng thêm lề 5% giữ nguyên tỷ lệ khung hình (letterbox)** và mô hình **5 lớp (`Barcode`, `Notch`, `Ripped`, `Spot`, `Wornout`)** với logic phân tuyến **A/B/C/STOP** (`Ripped` luôn ưu tiên Khay A; lỗi khác về Khay B; sách hợp lệ không thấy lỗi về Khay C).
   - Ảnh trong Damaged Books v1 hiện đã bị ép vuông `640×640`, nhiều ảnh chụp gáy sách cầm tay hoặc đặt nghiêng dưới đèn phòng. Cần thu thập thêm ảnh pilot trên đúng camera và ánh sáng của hệ thống để kiểm chứng.
2. **`[Chưa kiểm tra]` Độ bất định theo nhóm sách trên tập `val`:** Với chỉ `18` nhóm sách ở `val` (riêng `Ripped` chỉ xuất hiện ở `9` nhóm và 3 nhóm đầu chiếm `56,88%` tổng số box), mỗi instance `Ripped` làm thay đổi `2,564` điểm phần trăm Recall. Cần tính bootstrap theo nhóm sách (`group_id`) khi so sánh các mô hình ở Lần 2.

---

## 6. Bảng rà chung 20 ảnh (`12 val + 8 train`) — Bước ưu tiên số 1 trước khi train Lần 2

> **Lưu ý phạm vi:**
> - Danh sách 20 ảnh dưới đây được trích xuất và kiểm chứng tự động từ `split_manifest.json` và tệp nhãn `.txt` thực tế bằng [analyze_colab_run.py](../scripts/analyze_colab_run.py) (`audit_20_manifest_verified` trong `run1-analysis.json`), sử dụng đúng đường dẫn tương đối và `group_id`.
> - Toàn bộ 20 tệp ảnh gốc `.jpg` đã được mở trực tiếp để ghi nhận xét thực tế. Không có nhóm sách nào giao nhau giữa `train` và `val` (`group_overlap_count = 0`).
> - **Mục đích của việc rà 20 ảnh là để hai bên thống nhất quy tắc gán nhãn 1 trang (annotation rubric)**; việc rà 20 ảnh **chưa chứng minh toàn bộ `307` ảnh `train + val` đã sạch nhãn**. Sau khi chốt quy tắc từ 20 ảnh này, cần áp dụng quy tắc đó để rà và tạo bản dataset mới (`v2`), tuyệt đối không sửa đè nhãn nguồn `v1`.

### 6.1. Bảng 12 ảnh tập `val` cần rà chung

| STT | Đường dẫn ảnh (`val/images/...`) | `group_id` (từ `split_manifest.json`) | Tổng số box GT & Phân lớp thực tế (`val/labels/...`) | Quan sát thực tế sau khi mở ảnh gốc `.jpg` & Câu hỏi cần chốt |
|---:|---|---|---|---|
| **1** | `val/images/train__IMG_1174_jpg.rf.150e452512bc5b0270247d17e32764e1.jpg` | `visual_group_087` | **`3` box:** `0 Barcode`, `2 Notch`, `0 Ripped`, `0 Spot`, `1 Wornout` | Bìa sau trắng (*웃는 남자*). Góc dưới phải có mã vạch ISBN-13 in sẵn rất rõ (model dự đoán `Barcode ≈ 0.5`), nhưng GT chỉ gán `1 Wornout` ở mép trên phải (`91×14 px`) và `2 Notch` ở mép trái (`12×56 px`, `16×54 px`), **thiếu nhãn `Barcode`**. **Cần chốt:** Mọi mã vạch 1D nhìn thấy rõ (gồm cả ISBN in sẵn) đều phải gán `Barcode`. |
| **2** | `val/images/train__IMG_1359_jpg.rf.21b7d1f92a68815a84681fa4f0b82e2b.jpg` | `visual_group_076` | **`0` box (nhãn rỗng):** `0` ở cả 5 lớp | Chụp nghiêng gáy và mặt sau cuốn *구르미 그린 달빛 Photo Essay* cầm trên tay. Trên dải đai trắng giữa bìa sau có mã vạch ISBN nhìn thấy rõ toàn bộ vạch sọc (kèm tem chữ số `687.04 / EM538152` ở gáy), nhưng tệp nhãn rỗng. **Cần chốt:** Ảnh không có lỗi hư hỏng (`no damage`) nhưng có mã vạch 1D nhìn thấy rõ thì vẫn phải gán hộp `Barcode`. |
| **3** | `val/images/train__IMG_1446_jpg.rf.7c5e4f5a6a8d4afd8fdf84d098dea71e.jpg` | `visual_group_013` | **`1` box (`barcode-only`):** `1 Barcode` (`44×213 px`), `0` lỗi | Bìa trước xanh tím *메타버스 / META VERSE*. Hộp GT `Barcode` nằm sát rìa cắt bên trái (`x=0.034, w=0.069`), nơi tem thư viện bị cắt mất gần hết phần vạch sọc, chỉ còn chữ `서울과학기술대학교` và vài nét vạch sát mép ảnh; trong khi chữ `META VERSE` kẻ sọc ở giữa bìa bị model đoán nhầm thành `Barcode`. **Cần chốt:** Ngưỡng phần trăm vùng vạch mã vạch tối thiểu còn nhìn thấy ở rìa ảnh để gán `Barcode`. |
| **4** | `val/images/train__IMG_1201_jpg.rf.222bf0fbb2b3e9da5bb50d95b71416d7.jpg` | `visual_group_020` | **`12` box:** `0 Barcode`, `0 Notch`, `2 Ripped`, `7 Spot`, `3 Wornout` | Góc trên trái bìa đỏ *황산 (Amélie Nothomb)* có dán băng dính dọc gáy. Mép trên chia thành `3 Wornout` nối tiếp nhau; góc trên trái và khe gáy trái gán `2 Ripped`; trên mặt bìa đỏ có `7 Spot` nhỏ (`18×12 px` tới `68×19 px`) gần vùng chữ in và băng dính phản sáng. **Cần chốt:** Ranh giới `Spot` với vết bẩn/bọt khí dưới băng dính và quy tắc gộp hay tách dải `Wornout` liên tục ở mép trên. |
| **5** | `val/images/train__IMG_1129_jpg.rf.2c673a20905717fed0cf55f4c14fd371.jpg` | `visual_group_060` *(top-2 nhóm `val`: 6 ảnh / 72 box)* | **`13` box:** `1 Barcode`, `0 Notch`, `0 Ripped`, `1 Spot`, `11 Wornout` | Bìa xanh lá *교육학개론* đặt chéo trên bàn gỗ. Tem thư viện góc trên gán `1 Barcode`. Dọc mép trái và mép dưới (vùng hình những cây bút chì màu) có các đốm tróc trắng nhỏ được tách thành `11` hộp `Wornout` rời rạc (`12×11 px` đến `83×106 px`) và `1 Spot` (`11×22 px`). **Cần chốt:** Tiêu chí gộp dải mòn hay tách từng đốm nhỏ, và phân biệt vết tróc mép với họa tiết đầu bút chì sát mép. |
| **6** | `val/images/train__IMG_1736_jpg.rf.d422877808581b2810764b2ba6d0053e.jpg` | `visual_group_060` *(top-2 nhóm `val`)* | **`5` box:** `0 Barcode`, `3 Notch`, `2 Ripped`, `0 Spot`, `0 Wornout` *(có 1 cặp `Ripped`–`Notch` chồng lấp `IoA = 0.50`)* | Cận cảnh đầu gáy xanh lam *교육학개론*. Đầu gáy bị rách toạc lộ lõi giấy trắng và bong màng xanh rất rõ (`2 Ripped`: `195×111 px` và `103×42 px`), kèm `3 Notch` dọc mép gáy và khe rách (model không có dự đoán vượt `0.25` trên ảnh vẽ). **Cần chốt:** Khi vết rách lớn ở đầu gáy đã gán `Ripped`, có gán thêm các hộp `Notch` chồng lên rìa của chính vết rách đó không. |
| **7** | `val/images/train__IMG_1330_jpg.rf.56bd3678a78279742ce541f7530b0c16.jpg` | `visual_group_023` *(top-1 nhóm `val`: 6 ảnh / 74 box)* | **`12` box:** `1 Barcode`, `2 Notch`, `3 Ripped`, `1 Spot`, `5 Wornout` *(chứa 3 hộp `Wornout` `aspect > 10:1`: `12.50`, `18.56`, `18.50`)* | Bìa nâu có **2 mã vạch**: tem thư viện giữa trái (đã gán `1 Barcode`) và mã ISBN-13 góc dưới trái (**bị sót trong GT**, model phát hiện đúng). Ngoài ra mép trên, trái, phải có 3 dải `Wornout` rất mảnh kéo dài (`200×16 px`, `16×297 px`, `18×333 px`) xen với `3 Ripped` (góc trên trái và mép phải lộ giấy trắng). **Cần chốt:** Bổ sung `Barcode` ISBN bị thiếu và quy tắc vẽ hộp dải mảnh `aspect > 10:1`. |
| **8** | `val/images/test__IMG_7_jpg.rf.b0eda460f02c08b90d5530fafd1d8fe0.jpg` | `visually_confirmed_same_book_001` *(top-3 nhóm `val`: 5 ảnh / 40 box)* | **`10` box:** `1 Barcode`, `6 Notch`, `1 Ripped`, `0 Spot`, `2 Wornout` *(1 hộp `Ripped` `173×16 px`, `aspect = 10.81`; 1 cặp `Notch`–`Notch` `IoA = 0.51`)* | Cuốn *역발상의 기술* bìa nâu đặt ngược trên bàn gỗ (tiền tố tên file là `test__` lịch sử nhưng nằm trong tập `val`). Mép trên (`y ≈ 0.20`) được gán **`1 Ripped` (`173×16 px`) + `1 Wornout` (`52×20 px`)**; các đường nếp gấp/lõm chéo trên mặt bìa nâu và rìa phải được gán `6 Notch`. Đối chiếu trực tiếp với #9 (`train__IMG_1316_jpg`). |
| **9** | `val/images/train__IMG_1316_jpg.rf.faff4976751925a381bcd15b93a6342c.jpg` | `visually_confirmed_same_book_001` *(cùng nhóm & cùng cuốn sách với #8 trong `val`)* | **`15` box:** `1 Barcode`, `5 Notch`, `0 Ripped`, `1 Spot`, `8 Wornout` *(1 hộp `Wornout` `176×16 px`, `aspect = 11.00`)* | Chụp cùng cuốn *역발상의 기술* ở gần như cùng góc máy với `test__IMG_7_jpg` (#8). Tuy nhiên, chính vết hỏng dọc mép trên (`x ≈ 0.55, y ≈ 0.20`) ở #8 được gán là **`Ripped` (Khay A)** thì ở #9 lại được gán là **`Wornout` (`176×16 px`, Khay B)** và không có hộp `Ripped` nào; đồng thời mép dưới ở #9 được tách thành 5 hộp `Wornout` + `1 Spot` (so với 1 hộp `Wornout` ở #8). **Cần chốt:** Tiêu chí phân xử dứt khoát giữa `Ripped` và `Wornout` cho vết sờn/tách mép và vết gấp trên mặt bìa (`Notch`). |
| **10** | `val/images/train__IMG_128_jpg.rf.e8f2e585c235d04383d46d45089b203e.jpg` | `visual_group_020` *(cùng cuốn *황산* với #4)* | **`12` box:** `0 Barcode`, `1 Notch`, `1 Ripped`, `7 Spot`, `3 Wornout` *(chứa hộp dẹt nhất tập `val`: `486×12 px`, `aspect = 40.50:1`)* | Chụp nửa dưới bìa đỏ *황산*. Khe gáy trái gán `1 Ripped` + `1 Wornout`; nhưng dọc mép dưới cùng của bìa sách (nơi mép giấy chỉ hơi bạc rất mảnh) lại có 1 hộp `Wornout` kéo ngang `486 px`, cao chỉ `12 px` (`aspect = 40.50:1`), cùng `7 Spot` trên nền đỏ/chữ in. **Cần chốt:** Viền mép chỉ bạc rất mảnh có gán hộp `Wornout` dẹt `40:1` suốt chiều ngang sách không. |
| **11** | `val/images/train__IMG_1666_jpg.rf.870f66f26b2a08772ee56261e4fd2b8f.jpg` | `visual_group_060` | **`8` box:** `0 Barcode`, `3 Notch`, `2 Ripped`, `1 Spot`, `2 Wornout` *(chứa cặp hộp lồng nhau `IoA = 1.0000`: `Wornout` dòng 7 nằm trọn trong `Notch` dòng 0)* | Chụp dọc gáy xanh lam *교육학개론* cầm tay. Đầu gáy dưới bị rách/bong nặng gán `2 Ripped`, `2 Notch`, `1 Wornout`, `1 Spot`; ở nửa trên gáy có 1 hộp `Notch` dài (`48×252 px`) bao trùm hoàn toàn 1 hộp `Wornout` nhỏ (`18×27 px`, `IoA = 1.0`). **Cần chốt:** Quy tắc cấm gán hai lớp lỗi lồng nhau 100% (`IoA = 1.0`) trên cùng một vết sờn mép gáy. |
| **12** | `val/images/train__IMG_1122_jpg.rf.1d6cdbb6339ffde5cd835aeffca1ff07.jpg` | `visual_group_076` *(cùng cuốn *Photo Essay* với #2)* | **`0` box (nhãn rỗng):** `0` ở cả 5 lớp | Chụp chéo gáy cuốn *Photo Essay* cầm tay (góc này chỉ thấy tem chữ số `687.04 / EM538152 / 600`, không thấy mã vạch mặt sau). Ở mép gáy ngay phía trên khung ảnh minh họa có một vết cấn/sờn nhỏ ở rìa. **Cần chốt:** Ngưỡng dung sai cho mẫu âm (`0` lỗi, Khay C) đối với vết cấn nhẹ ở mép gáy. |

### 6.2. Bảng 8 ảnh tập `train` cần rà chung

| STT | Đường dẫn ảnh (`train/images/...`) | `group_id` (từ `split_manifest.json`) | Tổng số box GT & Phân lớp thực tế (`train/labels/...`) | Quan sát thực tế sau khi mở ảnh gốc `.jpg` & Câu hỏi cần chốt |
|---:|---|---|---|---|
| **13** | `train/images/train__IMG_1654_jpg.rf.44c01b9543050b1d6f37194005a3743d.jpg` | `visual_group_010` *(top-1 nhóm `train`: 10 ảnh / 95 box)* | **`13` box:** `0 Barcode`, `8 Notch`, `2 Ripped`, `0 Spot`, `3 Wornout` *(có cặp `Notch`–`Ripped` chồng lấp `IoA = 0.7105`)* | Bìa đen có ảnh chân dung (*신 / Bernard Werber*). Mép trái bị sờn/tách lớp giấy trắng dọc suốt chiều cao sách được gán `2 Ripped` (hộp lớn `50×393 px`) chồng với nhiều hộp `Notch` nhỏ nằm ngang (`8 Notch`), đồng thời vết trầy/lõm giữa mặt chân dung cũng gán `Notch` (`140×43 px`). **Cần chốt:** Phân biệt `Ripped` (tách lớp giấy mép), `Wornout` (mòn mép) và `Notch` (có gán cho vết trầy giữa mặt phẳng bìa không). |
| **14** | `train/images/train__IMG_1081_jpg.rf.f8a5c130159a65ab4198e96038593125.jpg` | `visual_group_018` *(top-4 nhóm `train`: 4 ảnh / 68 box)* | **`25` box:** `1 Barcode`, `6 Notch`, `1 Ripped`, `5 Spot`, `12 Wornout` *(có 2 hộp `aspect > 10:1`: `Notch 11.00`, `Wornout 13.05`)* | Bìa trắng-đỏ *Automatic Control*. Trên ảnh có **2 mã vạch rõ** (tem thư viện bên phải và mã ISBN-13 bên trái), nhưng GT chỉ gán `1 Barcode` cho tem thư viện và **bỏ sót mã ISBN bên trái**. Bốn cạnh sách được chia thành 24 hộp đan xen cả 4 lớp lỗi. **Cần chốt:** Đồng bộ quy tắc gán đủ cả 2 mã vạch và quy tắc gộp hộp dọc cạnh sách. |
| **15** | `train/images/train__IMG_1118_jpg.rf.c43d7c0edde6436aa66e3e1c21d27414.jpg` | `visual_group_011` *(top-3 nhóm `train`: 8 ảnh / 94 box)* | **`19` box:** `1 Barcode`, `5 Notch`, `0 Ripped`, `8 Spot`, `5 Wornout` *(chứa 3 hộp `aspect > 10:1`, gồm hộp `Wornout` dẹt nhất tập `train`: `460×19 px`, `aspect = 24.21`)* | Bìa vàng nâu *스페인역사 (Digest 100 Series 11)*. Mép phải (`31×409 px`, `aspect = 13.19`) và mép dưới (`460×19 px`, `aspect = 24.21`) chỉ sờn rất nhẹ ở viền nhưng được kéo 2 dải `Wornout` dài hết cạnh sách; rãnh gáy trái lại gán `2 Notch` dọc dài (`17×189 px`, `17×112 px`). **Cần chốt:** Rãnh gáy/nếp gấp bìa và viền mép hơi sờn có gán dải dài `Wornout`/`Notch` không. |
| **16** | `train/images/train__IMG_1102_jpg.rf.b19e8d2ce131dbfe3f424409da4ea7e6.jpg` | `visual_r2_007` | **`7` box:** `0 Barcode`, `2 Notch`, `1 Ripped`, `0 Spot`, `4 Wornout` *(chứa hộp `Notch` nằm lọt `100%` (`IoA = 1.0000`) trong hộp `Ripped`, và `Ripped` đè `Wornout` `IoA = 0.5086`)* | Ảnh chụp cận cảnh góc dưới phải bìa sách xanh-đen (*친구들*) bị mài tróc/rách nặng ở góc. Cùng một vùng hư hỏng ở góc vừa được bao bởi 1 hộp `Ripped` lớn (`156×182 px`), vừa có 1 hộp `Notch` (`61×99 px`) nằm lọt 100% bên trong, vừa có hộp `Wornout` đè phía dưới. **Cần chốt:** Một vùng hư hỏng phức hợp chỉ gán 1 hộp theo lớp mức độ cao nhất (`Ripped`) hay gán chồng nhiều lớp. |
| **17** | `train/images/train__IMG_1474_jpg.rf.d0452b6eee2b416445b3dbb131c22be6.jpg` | `visual_group_093` | **`7` box:** `0 Barcode`, `2 Notch`, `1 Ripped`, `2 Spot`, `2 Wornout` *(chứa hộp `Spot` `10×11 px` nằm lọt `100%` (`IoA = 1.0000`) trong hộp `Notch` `17×85 px`)* | Bìa trắng *Escape from Freedom (Erich Fromm)*. Góc trên trái bị bong/rách nhỏ gán `1 Ripped` (`71×42 px`), меp trên gán `2 Wornout`; dọc mép trái có vết tróc mảnh vừa gán `Notch` dài (`17×85 px`) vừa gán `Spot` nhỏ (`10×11 px`) đè lọt bên trong. **Cần chốt:** Không gán `Spot` chồng lên chấm tróc nằm bên trong hộp `Notch`/`Wornout`. |
| **18** | `train/images/train__IMG_1634_jpg.rf.2089ffa600282ed7ddfa0de71454a74b.jpg` | `visual_group_056` | **`20` box:** `0 Barcode`, `7 Notch`, `1 Ripped`, `9 Spot`, `3 Wornout` *(chứa hộp `Notch` `53×26 px` nằm lọt `100%` (`IoA = 1.0000`) trong hộp `Spot` `162×69 px`)* | Góc trên trái bìa bạc *전쟁과 리더* bị lóa đèn mạnh trên lớp màng bóng. Ngoài vết rách nhỏ ở góc trái (`1 Ripped`), vùng mặt bìa bị lóa sáng và xước màng bóng được gán dày đặc `9 Spot` và `7 Notch` đè lên nhau. **Cần chốt:** Vết xước màng bóng/lóa đèn phản chiếu có gán là `Notch`/`Spot` không. |
| **19** | `train/images/train__IMG_204_jpg.rf.2876d2153d9ae9fd2ab452f9f8941fa1.jpg` | `visual_group_038` | **`5` box (đủ 5 lớp):** `1 Barcode`, `1 Notch`, `1 Ripped`, `1 Spot`, `1 Wornout` *(chứa hộp `Spot` `20×20 px` nằm lọt `100%` (`IoA = 1.0000`) trong hộp `Barcode` `128×101 px`)* | Chụp nghiêng gáy cuốn sách vàng *그리스 로마 신화*. Mặt bìa sau có mã vạch ISBN (`1 Barcode`), và ngay góc trên trái bên trong vùng mã vạch có một chấm nhỏ (`20×20 px`) được gán `1 Spot` đè lên hộp `Barcode`; đầu dưới gáy sách bị rách/mòn gán `1 Ripped` + `1 Wornout`. **Cần chốt:** Chấm bẩn nhỏ nằm đè trên tem `Barcode` có gán chồng lớp `Spot` không. |
| **20** | `train/images/train__IMG_1078_jpg.rf.ad6d792160e893cba0b959eddb89616f.jpg` | `visual_group_069` | **`0` box (nhãn rỗng):** `0` ở cả 5 lớp | Chụp thẳng gáy cuốn sách đen *바둑으로 읽는 인공지능* cầm trên tay. Gáy sách phẳng, sạch, chỉ có tem phân loại chữ số (`691.2 / EM52632 / 600`, không có sọc mã vạch 1D) và không có lỗi hư hỏng. Đây là mẫu âm chuẩn (`reference negative`) cho Khay C. |

---

## 7. Đề xuất Kế hoạch Cải thiện Dataset và Chiến lược Huấn luyện Lần 2

*(Chỉ đề xuất, chưa thực hiện huấn luyện, chưa sửa nhãn nguồn, chưa gộp lớp)*

### 7.1. Quy trình chuẩn hóa dữ liệu (`v2`) và bảo toàn hợp đồng `D20–D24`

1. **Giữ nguyên hợp đồng `D20–D24` hiện hành:**
   - Giữ **5 lớp (`Barcode`, `Notch`, `Ripped`, `Spot`, `Wornout`)**, tiền xử lý trên line bằng **tách ROI cuốn sách từ ảnh gốc + lề 5% giữ nguyên tỷ lệ khung hình (letterbox)**, và điều hướng **A/B/C/STOP** (`Ripped` luôn ưu tiên Khay A; `Notch`/`Spot`/`Wornout` về Khay B; sách hợp lệ không thấy lỗi về Khay C).
   - Không tự ý bỏ lớp `Barcode` khỏi dataset khi chưa có cổng nghiệm thu riêng cho `zxing-cpp` trên ảnh line thực tế. Nếu muốn thử phương án rút gọn 3 lớp (`Barcode`, `Ripped`, `OtherDamage = Notch ∪ Spot ∪ Wornout`) thì chỉ thực hiện dưới dạng **nhãn dẫn xuất (derived dataset)** sau khi được duyệt, tuyệt đối không gộp `Ripped` chung với lỗi nhẹ vì sẽ làm mất phân tuyến Khay A / Khay B.
2. **Từ bảng rà 20 ảnh → Quy tắc 1 trang → Dataset phiên bản mới (`split-reviewed-v2`):**
   - Quy tắc đã chốt: `Barcode` gồm cả ISBN; phân biệt `Ripped` / `Wornout` / `Notch` theo tổn thương nhìn rõ; cho phép hai hiện tượng thật có hộp giao/lồng nhau (ví dụ `Spot` trên `Barcode`), không gán trùng lớp cho cùng tổn thương; chuẩn hóa vùng `Wornout` liên tục; không đặt ngưỡng pixel loại bỏ lỗi rõ. Lượt hiện tại chỉ lập đề xuất cho 20 ảnh. Rà rộng và xuất `split-reviewed-v2` là bước sau, chưa thực hiện.
   - Giữ nguyên tuyệt đối `split-reviewed-v1`, tệp ZIP gốc và tập `test` (đóng kín).

### 7.2. Ma trận thực nghiệm Lần 2 — Tách rõ thực nghiệm đơn biến và gói cấu hình

Để xác định đúng nguyên nhân cải thiện, các lượt chạy được thiết kế tách biệt giữa **thực nghiệm đơn biến (single-variable ablation)** và **thử nghiệm gói cấu hình (grouped configuration bundle)**:

| Mã lượt chạy | Loại phép thử | Dataset | Cấu hình cơ sở | Thay đổi so với mốc đối chiếu ngay trước đó | Mục đích & Điều kiện kiểm chứng |
|---|---|---|---|---|---|
| **Pilot 2A-1** | **Đơn biến (`lr0`)** | `split-reviewed-v1` | `yolo11n.pt`, `imgsz=640`, `batch=16`, `seed=42`, `10–15 epochs`, giữ nguyên `warmup_bias_lr=0.1`, `cos_lr=False`, `amp=True` và toàn bộ augmentation Run 1 | **Chỉ đổi 1 biến:** `lr0: 0.01 -> 0.001` | Kiểm tra xem riêng `lr0=0.01` có phải là nguyên nhân gây `val/*_loss = NaN` ở epoch 1–10 hay không. |
| **Pilot 2A-2** *(chỉ chạy nếu 2A-1 còn spike/`NaN`)* | **Đơn biến (`warmup_bias_lr`)** | `split-reviewed-v1` | Như Pilot 2A-1 (`lr0=0.001`) | **Chỉ đổi 1 biến:** `warmup_bias_lr: 0.1 -> 0.0` | Tách riêng tác động của `warmup_bias_lr=0.1` ở 3 epoch đầu. |
| **Pilot 2A-3** *(chỉ chạy nếu 2A-2 vẫn còn `NaN`)* | **Đơn biến (`amp`)** | `split-reviewed-v1` | Như Pilot 2A-2 | **Chỉ đổi 1 biến:** `amp: True -> False` | Tách riêng tác động của mixed precision FP16 đối với `NaN`. |
| **Run 2B (Baseline v1 ổn định)** | Mở rộng số epoch của cấu hình 2A đã ổn định | `split-reviewed-v1` | Cấu hình ổn định từ 2A (`yolo11n.pt`, `imgsz=640`, `batch=16`, `seed=42`, giữ nguyên augmentation Run 1) | Chạy đủ `100–120 epochs` (`patience=25`) | Tạo mốc baseline đầy đủ trên nhãn `v1` khi không còn `NaN` đầu kỳ (chưa đổi lịch `cos_lr` hay augmentation). |
| **Run 2C (Đối chứng Nhãn `v2`)** | **Đơn biến (Dataset `v1 -> v2`)** | `split-reviewed-v2` | Y hệt cấu hình huấn luyện của Run 2B | **Chỉ đổi 1 yếu tố:** bộ nhãn huấn luyện từ `v1` sang `v2` | Đo mức cải thiện thuần túy nhờ chuẩn hóa nhãn (khi chấm cả 2B và 2C trên cùng bộ `val` chuẩn hóa). |
| **Run 2D (Ứng viên Gói Augmentation v2)** | **Nhóm cấu hình (Config Bundle)** | `split-reviewed-v2` | Như Run 2C | Thay **gói augmentation giảm co/biến màu vật nhỏ**: `mosaic=0.2, close_mosaic=20, scale=0.2, translate=0.05, fliplr=0.0, hsv_s=0.3, hsv_v=0.2` | Đánh giá tổng hiệu ứng của gói augmentation nhẹ lỗi nhỏ so với augmentation Run 1 (Run 2C). *(Nếu cần biết riêng tác động của `mosaic` hay `scale`, phải tách lượt con)*. |
| **Run 2E (Đối chứng Model `yolo11s`)** | **Đơn biến (`model`)** | `split-reviewed-v2` | Cấu hình tốt nhất giữa 2C và 2D (`imgsz=640`, `batch=16`, `seed=42`) | **Chỉ đổi 1 biến:** `model: yolo11n.pt -> yolo11s.pt` | Đo tác động thuần của dung lượng mạng (`yolo11s` vs `yolo11n`) ở cùng độ phân giải `640` và cùng `batch=16`. |
| **Run 2F (Thử nghiệm `imgsz=960`)** | **Đơn biến `imgsz` (hoặc cặp `imgsz + batch` nếu giảm batch)** | `split-reviewed-v2` | Cấu hình tốt nhất giữa 2C và 2D (`yolo11n.pt`, `seed=42`) | Đổi `imgsz: 640 -> 960` *(ghi rõ: nếu giữ `batch=16` là đơn biến; nếu phải giảm `batch=8` do VRAM thì là đổi cặp `(imgsz, batch)`)* | Kiểm tra xem phóng to đầu vào lên `960` có cải thiện Recall các hộp `Spot`/`Wornout`/`Notch` nhỏ hay không. |

### 7.3. Quy tắc đánh giá công bằng (Fair Validation Protocol) và chọn ngưỡng

1. **Nguyên tắc so sánh công bằng khi sửa nhãn validation ở `v2`:**
   - Khi tạo `split-reviewed-v2`, nếu nhãn của tập `val` được sửa (ví dụ bổ sung các hộp `Barcode` bị thiếu hoặc chuẩn hóa hộp `Ripped`/`Wornout`), **tuyệt đối không so sánh trực tiếp số metric của mô hình cũ chấm trên `val v1` với mô hình mới chấm trên `val v2`**.
   - Mọi mô hình cần so sánh (**bao gồm cả `best.pt` của Run 1 và Run 2B** đã train trên `v1`, cùng các mô hình Run 2C–2F train trên `v2`) **phải được chấm lại (`model.val()`) trên cùng một bộ `val v2` đã chuẩn hóa** (và có thể xuất song song bảng điểm trên `val v1` để truy vết).
2. **Metric ưu tiên và chọn ngưỡng từng lớp:**
   - Xuất raw predictions và mảng đường cong PR trên `val` để chọn ngưỡng confidence riêng cho từng lớp (`thresholds` theo lớp), không dùng ngưỡng chung `~0.350`.
   - Báo cáo **Recall từng lớp lỗi tại sàn Precision cố định (`P >= 0.50` và `P >= 0.80`)**; tại các ngưỡng mà một lớp không có dự đoán nào, ghi `Precision = N/A (0 pred)`, không ghi `P = 100%`.
   - Ưu tiên tối đa hóa **$F_2$-score / Recall cho `Ripped`** (đảm bảo sách rách vào Khay A) và báo cáo thêm tỷ lệ phân tuyến đúng cấp cuốn sách (`Route A / B / C`) kèm khoảng tin cậy bootstrap theo `group_id`.

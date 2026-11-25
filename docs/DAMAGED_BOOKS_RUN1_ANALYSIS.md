# Phân tích YOLO11n lần 1 và đề xuất lần 2

Ngày: 2026-11-11. Run: `20261111T132200647414Z`. Trạng thái: phân tích artifacts hoàn tất; kế hoạch lần 2 **chỉ đề xuất, chưa thực hiện**.

## Kết luận và mức bằng chứng

- **[Bằng chứng] Model hiện tại chưa đáp ứng phát hiện lỗi.** Recall tại điểm báo cáo: Notch 0%, Ripped 2,564%, Spot 0%, Wornout 0%. AP50 bốn lớp lỗi lần lượt 0,090%, 5,633%, 2,587%, 4,526%. Macro AP50 riêng lỗi = 3,209%; macro recall riêng lỗi = 0,641%. Nguồn: `validation-metrics.json`, [bảng tính trực tiếp](DAMAGED_BOOKS_RUN1_TABLES.md).
- **[Bằng chứng] Precision tổng hợp 88,368% gây hiểu nhầm khi đọc riêng.** Ba lớp có P=1 nhưng R=0 ở điểm báo cáo; đây không phải bằng chứng nhận diện hoàn hảo. Mã Ultralytics 8.4.208 nội suy precision với `left=1`, chọn một ngưỡng chung theo F1 trung bình. Ảnh F1 ghi đỉnh trung bình khoảng 0,15 tại confidence 0,350. Không dùng ngưỡng này làm ngưỡng triển khai từng lớp.
- **[Bằng chứng] Có bất thường số học đầu train:** cả ba val loss là NaN tại epoch 1–8 và 10; epoch 9 có val cls loss 587,034. **[Giả thuyết]** AdamW `lr0=0.01`, warmup bias LR 0.1 và/hoặc mixed precision có thể góp phần; chưa chứng minh nguyên nhân từ CSV. Cần đối chứng nhỏ trước khi chạy dài.
- **[Bằng chứng] Spot/Wornout có nhiều hộp nhỏ, và nhãn còn vấn đề dù đã được duyệt.** Cạnh ngắn trung vị val là 18px cho cả hai lớp; phát hiện ít nhất hai ảnh có barcode rõ nhưng thiếu lớp Barcode (IMG_1174, IMG_1359). **[Giả thuyết]** nhiễu định nghĩa và tín hiệu ảnh nhỏ làm model khó học; mức đóng góp chưa được đo.
- **[Bằng chứng] Không tìm thấy lỗi remap/geometry/hash hoặc trùng train–val theo các kiểm tra đã chạy.** Điều này loại được một số lỗi kỹ thuật đơn giản; không chứng minh toàn bộ nhãn đúng hay mọi nhóm trực quan đã độc lập.

## Phạm vi, nguồn và truy vết

**[Bằng chứng]** Đã đọc AGENTS, README, PROGRESS, mục cuối SESSION_LOG, PLAN/DECISIONS và trạng thái Git trước khi phân tích. Checkout chính là `main`; PROGRESS và SESSION_LOG đã có thay đổi từ trước. README/DECISIONS trên main vẫn mô tả hai lớp cũ, trong khi nhánh Colab có D20–D24 và luồng năm lớp. Báo cáo dùng yêu cầu năm lớp hiện tại, không tự hợp nhất các nhánh.

**[Bằng chứng]** ZIP nguồn tại `data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip`, SHA256:

`b1c6d7a8f724079d3868c74e36091f67a5f040e82ec6034115abd6de51f05866`

Giải nén **54 tệp** vào `data/local/damaged_books_v1/codex-analysis-20261111/artifacts/`. `git check-ignore -v` xác nhận quy tắc `.gitignore:21:/data/*`. Thư mục giải nén có sẵn bên cạnh ZIP không bị sửa. ZIP được băm trước/sau, kiểm CRC lúc giải nén; mọi tệp train/val được kiểm hash với manifest và kiểm lại cuối script. Không nạp checkpoint, train, inference, đánh giá test hay sửa nhãn.

Danh sách đầy đủ và kích thước: `data/local/damaged_books_v1/codex-analysis-20261111/inventory.txt`. Các nhóm nội dung đã giải nén:

| Vị trí | Nội dung |
|---|---|
| Gốc artifacts (10 tệp) | train-val.yaml, split_manifest.json, split-check.json, requested-config.json, environment.json, requirements-frozen.txt, initial-weights.json, training-status.json, validation-metrics.json, model-metadata.json |
| train (20 tệp ngoài weights) | args.yaml, labels.jpg, results.csv, results.png; train_batch0/1/2/1440/1441/1442.jpg; val_batch0/1_labels và _pred; BoxPR/BoxF1/BoxP/BoxR_curve.png; confusion_matrix.png và confusion_matrix_normalized.png |
| train/weights (12 tệp) | best.pt, last.pt, epoch0/10/20/30/40/50/60/70/80/90.pt |
| validation (12 tệp) | val_batch0/1/2_labels và _pred; BoxPR/BoxF1/BoxP/BoxR_curve.png; confusion_matrix.png và confusion_matrix_normalized.png |

Dataset đối chiếu: `data/local/damaged_books_v1/split-reviewed-v1`; manifest xuất từ Colab bằng manifest cục bộ. Dataset version `damaged-books-v1-five-8f203ddd57d4-077edf4cdcbd`; dataset ZIP SHA256 được environment ghi là `0da9c0710a22cb3260506eb003692ee12ff322db70ddbca7f6687fccbadc56c1`. Lượt này xác minh nội dung train/val theo manifest, không đọc ảnh/nhãn test. Tiền tố tên `test__IMG_7` là tên nguồn lịch sử của một ảnh hiện thuộc **val**, không phải đánh giá tập test hiện tại.

## Cấu hình và môi trường thực tế

**[Bằng chứng]** Từ `train/args.yaml`, `requested-config.json`, `environment.json`, `initial-weights.json`:

| Thông số | Giá trị |
|---|---|
| Model / pretrained / resume / freeze | yolo11n.pt / true / false / null |
| Epochs / patience / batch / imgsz | 100 / 20 / 16 / 640 |
| Optimizer / lr0 / lrf / momentum / weight_decay | AdamW / 0.01 / 0.01 / 0.937 / 0.0005 |
| Warmup epochs / momentum / bias LR | 3.0 / 0.8 / 0.1 |
| Seed / deterministic / AMP | 42 / true / true |
| Device / workers / cache / fraction | 0 / 2 / false / 1.0 |
| Mosaic / close_mosaic / scale / translate | 1.0 / 10 / 0.5 / 0.1 |
| HSV h/s/v / horizontal flip | 0.015 / 0.7 / 0.4 / 0.5 |
| Degrees / shear / perspective / flipud | đều 0 |
| Mixup / cutmix / copy_paste | đều 0 |
| Rect / multi_scale / single_cls / cls_remap | false / 0.0 / false / true |
| Box / cls / dfl loss weight | 7.5 / 0.5 / 1.5 |
| max_det / conf / NMS iou trong args | 300 / null / null |
| Python / Torch / CUDA / GPU | 3.13.16 / 2.14.1+cu130 / 13.0 / Tesla T4 |
| Ultralytics | 8.4.208 |

**[Bằng chứng]** `auto_augment=randaugment`, `erasing=0.4`, các khóa mask/pose cũng có trong args chung. Không lấy sự có mặt của khóa làm bằng chứng chúng đã áp dụng vào pipeline detection. `augment=false` không có nghĩa tắt mosaic/HSV trong training; ảnh `train/train_batch0.jpg` có mosaic, crop và lật ảnh.

**[Bằng chứng về mã thư viện]** Đã đối chiếu trực tiếp Ultralytics8.4.208 cài cục bộ: `ultralytics/data/dataset.py:342` gọi `v8_transforms` cho detection; `ultralytics/data/augment.py:2835` xây pipeline mosaic/perspective/copy-paste/mixup/cutmix/Albumentations/HSV/flip, không đọc `erasing` hay `auto_augment`. Hai khóa đó được truyền vào `classify_augmentations` tại `dataset.py:1335`. Vì vậy không có căn cứ quy lỗi detection cho `erasing=0.4` hoặc chữa nó bằng cách chỉ tắt hai khóa classification. Chưa kiểm mã thư viện có bị chỉnh riêng trong phiên Colab; không có bằng chứng về việc chỉnh đó trong artifacts. `requirements-frozen.txt` khớp environment về Torch2.14.1+cu130 và Ultralytics8.4.208, đồng thời ghi NumPy2.4.6, OpenCV5.0.0.93, PyYAML6.0.3; khác OpenCV dùng cho script phân tích cục bộ.

**[Bằng chứng]** Hash weights khởi tạo được lưu: `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`. Hash best.pt thực tế khớp metadata: `eb76c53172f91189cb78191470f73b7efa4560a71f51616f934df74f3ac80a4f`. `training-status.json` ghi completed; CSV có đủ 100 epoch. Tổng time CSV cuối là 475,187 giây, không phải thời gian toàn bộ phiên Colab.

**[Chưa kiểm tra]** Không có console log chi tiết số layer/weights được transfer, AMP scaler/gradient, cảnh báo NaN, log optimizer group hoặc tọa độ/confidence dự đoán từng ảnh. Không thể khẳng định NaN do AMP hoặc model đã mất đặc trưng pretrained. Cấu hình validation sau train không được xuất thành args riêng; chỉ có cấu hình train, notebook và mặc định của phiên bản thư viện để đối chiếu. Không tự điền NMS IoU thực tế.

## Chỉ số và diễn biến train

**[Bằng chứng]** Bảng đầy đủ P/R/AP, số ảnh/instance/nhóm val, các phân vị và loss theo cửa sổ epoch ở [RUN1_TABLES](DAMAGED_BOOKS_RUN1_TABLES.md). Chỉ số là phần trăm; số ảnh được tính trực tiếp từ nhãn, không cộng ngang vì một ảnh có nhiều lớp.

| Lớp | P (%) | R (%) | AP50 (%) | AP50–95 (%) | Ảnh / instance val |
|---|---:|---:|---:|---:|---:|
| Barcode | 69,283 | 76,000 | 68,003 | 42,922 | 25 / 25 |
| Notch | 100,000 | 0,000 | 0,090 | 0,027 | 22 / 53 |
| Ripped | 72,558 | 2,564 | 5,633 | 3,606 | 25 / 39 |
| Spot | 100,000 | 0,000 | 2,587 | 1,057 | 23 / 65 |
| Wornout | 100,000 | 0,000 | 4,526 | 1,211 | 42 / 145 |

**[Bằng chứng]** P/R trong JSON là điểm nội suy theo ngưỡng chung tối ưu F1 trung bình, không phải phép đo tại confidence 0.25 cố định. Đã đọc mã phiên bản 8.4.208 ở `ultralytics/utils/metrics.py` (nội suy `left=1`, chọn `smooth(f1_curve.mean(0), 0.1).argmax()`). Không suy số TP/FP nguyên từ precision nội suy. Recall Ripped 1/39 tương ứng 2,564% ở điểm này; chưa phải recall cấp cuốn/job.

**[Bằng chứng]** CSV có AP50 cao nhất ở epoch **82: 17,435%**; AP50–95 cao nhất ở epoch **97: 9,852%**. Epoch100 đạt AP50 15,791%, AP50–95 9,589%. Validation xuất riêng đạt 16,168%/9,765%, không giống hàng epoch100 và cũng không hoàn toàn giống epoch97. Không trộn hai lần đánh giá. **[Giả thuyết]** khác biệt nhỏ có thể do đánh giá lại best checkpoint với batch/precision khác; kiểm rẻ nhất là xem notebook đã chạy và log validation gốc, kỳ vọng xác định đúng checkpoint và tham số. Không cần train lại để kiểm điều này.

**[Bằng chứng]** Trung bình epoch81–90 so với91–100: AP50 giảm 15,684% →15,402%; AP50–95 tăng nhẹ 8,937% →9,067%. Train box 2,4544→2,4086; val box 2,5962→2,5771; val cls 3,0891→3,0703. Epoch100 train/val loss lần lượt: box 2,39373/2,57489; cls 2,74/3,04996; dfl 1,89256/2,05668.

**[Giả thuyết]** AP50 đang chững và dao động ở cuối, AP50–95 còn cải thiện nhỏ; chưa có dấu hiệu rõ của overfit nặng kiểu train giảm nhưng val tăng kéo dài. Không thể kết luận chắc model đã hội tụ hoàn toàn hoặc chỉ cần thêm epoch. Train/val loss không hoàn toàn so sánh trực tiếp do augmentation và cách tính; mosaic đóng 10 epoch cuối cũng thay đổi phân bố train. Kiểm rẻ nhất: sau khi xử lý NaN/nhãn, theo dõi metric riêng lỗi qua các cửa sổ 10 epoch, thay vì kéo dài ngay run này.

### PR, F1 và confusion matrix

**[Bằng chứng]** Đã mở trực tiếp `validation/BoxPR_curve.png`, `BoxF1_curve.png`, `BoxP_curve.png`, `BoxR_curve.png`, `confusion_matrix.png`, `confusion_matrix_normalized.png`, `train/results.png`. PR của bốn lớp lỗi nằm rất thấp; ở confidence thấp recall tăng nhưng precision sụt mạnh. F1 trung bình đỉnh chỉ khoảng0,15. Ảnh R ghi recall trung bình tối đa khoảng0,41 tại trục confidence0,000; đây là giới hạn đồ thị trên các prediction đã được lọc, không chứng minh model đạt recall đó ở ngưỡng vận hành khả dụng.

**[Bằng chứng]** Ma trận dưới được chép từ chữ số trên ảnh confusion matrix, không tái suy từ JSON. Hàng là dự đoán, cột là nhãn thật; tổng các cột lớp khớp327 instance val:

| Dự đoán \ Nhãn thật | Barcode | Notch | Ripped | Spot | Wornout | background |
|---|---:|---:|---:|---:|---:|---:|
| Barcode | 22 | 0 | 0 | 0 | 0 | 288 |
| Notch | 0 | 3 | 4 | 2 | 6 | 3504 |
| Ripped | 0 | 1 | 14 | 0 | 9 | 1848 |
| Spot | 0 | 5 | 1 | 15 | 5 | 3822 |
| Wornout | 0 | 4 | 12 | 1 | 70 | 6491 |
| background | 3 | 40 | 8 | 47 | 55 | 0 |

**[Bằng chứng]** Notch:40/53 (75,5%) và Spot:47/65 (72,3%) không được ghép với detection; Ripped có12/39 bị ghép thành Wornout,4/39 thành Notch,8/39 không ghép. Wornout có55/145 không ghép. Ma trận còn có **15.953 prediction không ghép GT**, tổng16.127 prediction trên54 ảnh, gần trần300/ảnh. Background ở đây là phần không ghép, không phải lớp sách tốt và không phải số ảnh âm. FP còn có thể chứa prediction đúng nhưng thiếu annotation hoặc hộp không đạt IoU.

**[Bằng chứng về mã thư viện]** DetectionValidator8.4.208 truyền `self.args.conf` vào confusion matrix; mặc định detection khi conf=null là0.001, matching IoU mặc định0.5, ghép không phân lớp để ghi nhầm lớp. Ảnh `val_batch*_pred` lại dùng mặc định vẽ conf>0.25. Vì vậy ma trận nhiều box ở confidence rất thấp không mâu thuẫn với ảnh dự đoán gần trống hay Recall tại ngưỡng F1 chung. **[Chưa kiểm tra]** artifacts không lưu args riêng của validation để xác nhận override; ngưỡng0.001 là đối chiếu đường chạy mặc định, không phải số đo trực tiếp từ ảnh. Không áp các số ma trận này cho ngưỡng0.35.

## Dataset: tính trực tiếp từ nhãn

**[Bằng chứng]** Train253 ảnh/83 nhóm/1.399 box; val54 ảnh/18 nhóm/327 box. Train có14 nhãn rỗng,23 ảnh không có nhãn lỗi1–4; val có4 nhãn rỗng,6 ảnh không có nhãn lỗi. Đây là thống kê annotation, không xác nhận ảnh thực sự không lỗi hoặc không có barcode.

**[Bằng chứng]** Barcode/Notch/Ripped/Spot/Wornout có77/250/173/355/544 box train. Wornout nhiều nhất nhưng vẫn R=0; Barcode ít nhất nhưng tốt nhất. Tỷ lệ box lớn nhất/nhỏ nhất là7,06, riêng lớp lỗi là3,14. **[Giả thuyết]** mất cân bằng có thể góp phần cho Ripped, nhưng không đủ giải thích toàn bộ thất bại; cân bằng số box đơn thuần không giải quyết định nghĩa lớp hoặc độ khó hình ảnh.

**[Bằng chứng]** Mọi ảnh train/val hiện640×640. Tính pixel bằng gain=`imgsz/max(width,height)` (letterbox), không dùng kích thước ảnh composite. Các bảng kèm chứa P05/P50/P95 của width/height/area chuẩn hóa, width/height/cạnh ngắn/area pixel. JSON cục bộ còn có min/P25/P75/max. Trung vị cạnh ngắn train→val: Barcode78→71px; Notch25,25→19px; Ripped33→37px; Spot19→18px; Wornout19→18px.

**[Bằng chứng]** Val có48/65 Spot (73,8%) và67/145 Wornout (46,2%) diện tích<32²px;20/65 Spot và47/145 Wornout cạnh ngắn<16px. Ripped chỉ6/39 diện tích<32²px, không có box cạnh ngắn<16px; vì vậy vật nhỏ không giải thích đủ việc bỏ sót Ripped. 960px làm box lớn hơn1,5 lần trên đầu vào nhưng không khôi phục chi tiết đã mất trong nguồn640px.

**[Bằng chứng]** Đã kiểm614 tệp ảnh/nhãn train+val với manifest. Không có dòng sai5 trường, NaN/Inf, class ID ngoài0–4, w/h không dương, box vượt ảnh (tolerance1e-6), area chuẩn hóa≤1e-6 hoặc area pixel<1, dòng trùng hoàn toàn, cặp box IoU≥0.9. `data.yaml`, YAML Colab, manifest và metadata cùng bảng năm lớp. Đây là tính hợp lệ kỹ thuật; không thay thế rà nội dung nhãn.

**[Bằng chứng]** Giao nhóm train/val=0; giao byte SHA256=0; giao SHA256 pixel đã decode=0. Quét **13.662 cặp train–val** bằng pHash DCT63bit, Hamming≤8:0 ứng viên. **[Chưa kiểm tra]** pHash không bảo đảm phát hiện cùng sách ở mặt khác/góc khác/crop mạnh; chưa tái rà SIFT hoặc độc lập mọi nhóm. Không tuyên bố không thể có rò rỉ chỉ từ kết quả này. Các ảnh cùng cuốn trong cùng val không phải rò rỉ, nhưng khiến số mẫu độc lập nhỏ hơn số ảnh.

## Đối chiếu ảnh đã mở

**[Bằng chứng]** Đã mở sáu ảnh `validation/val_batch{0,1,2}_{labels,pred}.jpg`, tổng48 ô ảnh val được hiển thị. Chưa xem trực quan6 ảnh cuối val không có trong các composite này. Đã mở thêm sáu ảnh gốc640px nêu dưới; đọc tệp nhãn tương ứng. Không tuyên bố đã rà toàn bộ nhãn train hoặc phê duyệt lại dataset.

| Ảnh/ô composite đã xem | Quan sát và mức kết luận |
|---|---|
| batch0 hàng3 cột4: `train__IMG_1174_jpg.rf.150e452512bc5b0270247d17e32764e1.jpg` | **[Bằng chứng]** ảnh gốc có mã vạch ở đáy phải, prediction Barcode≈0,5; nhãn chỉ có Wornout và2 Notch, không Barcode. Thiếu nhãn theo định nghĩa mọi barcode1D; không quy prediction này thành FP thực tế chỉ dựa GT. |
| batch1 hàng4 cột3: `train__IMG_1359_jpg.rf.21b7d1f92a68815a84681fa4f0b82e2b.jpg` | **[Bằng chứng]** ảnh gốc có mã vạch trên dải trắng giữa bìa, tệp nhãn rỗng. Mẫu không lỗi vẫn phải có Barcode nếu vùng mã nhìn thấy; negative về lỗi không đồng nghĩa zero-box. |
| batch1 hàng4 cột4: `train__IMG_1446_jpg.rf.7c5e4f5a6a8d4afd8fdf84d098dea71e.jpg` | **[Bằng chứng]** GT Barcode rất hẹp sát trái (x=0,034375,w=0,06875,h=0,3328125), trên phần tem chữ bị cắt; prediction còn nhận họa tiết sọc trong chữ META thành Barcode. **[Giả thuyết]** vùng GT chỉ còn tem chữ, không đủ mã vạch nhìn thấy; cần người rà xác nhận quy tắc cho mã bị cắt, không tự sửa. |
| batch1 hàng3 cột1: `train__IMG_1201_jpg.rf.222bf0fbb2b3e9da5bb50d95b71416d7.jpg` | **[Bằng chứng]** bìa đỏ có chữ in, dải băng dính và phản sáng; GT có7 Spot nhỏ,3 Wornout,2 Ripped; prediction hiển thị không có box. **[Giả thuyết]** một số Spot dễ lẫn chữ/bóng; từ640px chưa xác định từng Spot đúng/sai. Cần crop gốc và định nghĩa nhất quán, không gọi mọi Spot ở đây là nhãn sai. |
| batch0 hàng3 cột3: `train__IMG_1129_jpg.rf.2c673a20905717fed0cf55f4c14fd371.jpg` | **[Bằng chứng]** nhãn có11 Wornout,1 Spot,1 Barcode; nhiều hộp Wornout nhỏ dọc mép trên hình bút chì; ảnh gốc có mòn ở góc. **[Giả thuyết]** cách tách một dải mòn thành nhiều box và phân biệt họa tiết/mòn chưa rõ. Chưa chứng minh toàn bộ11 hộp sai. |
| batch2 hàng4 cột4: `train__IMG_1736_jpg.rf.d422877808581b2810764b2ba6d0053e.jpg` | **[Bằng chứng]** ảnh gốc có phần giấy trắng lộ ra và mép xanh bong/rách rõ; GT3 Notch+2 Ripped; ảnh prediction không hiện box. Ít nhất lỗi bỏ sót hiển thị không chỉ giới hạn ở chấm bẩn rất nhỏ. Không có box vẽ chỉ chứng minh không vượt ngưỡng vẽ, không chứng minh zero prediction ở0.001. |

**[Bằng chứng]** Cũng thấy batch0 hàng2 cột2 (IMG_1070) dự đoán thêm Barcode trên họa tiết sọc; batch2 hàng3 cột3 (IMG_1663) nhiều Barcode trên phần bìa tím phản sáng. Chỉ nhìn các ô composite, chưa mở gốc hai ảnh này. Dấu hiệu sai dương và khả năng thiếu GT phải phân biệt theo vùng cụ thể.

**[Chưa kiểm tra]** Chưa có quy tắc annotation đủ chi tiết để phân xử Spot so với in ấn/lóa, Wornout so với Ripped, Notch so với rách mất góc; chưa đo độ đồng thuận người gán. Những nhận định nghi vấn không thay đổi trạng thái approved hoặc nhãn nguồn.

## Giả thuyết và phép kiểm rẻ nhất

Các phép thử dưới đây **chưa chạy**; kỳ vọng mô tả dấu hiệu cần thấy nếu giả thuyết đúng, không phải cam kết kết quả.

| Giả thuyết | Căn cứ hiện có | Kiểm chứng rẻ nhất và kết quả kỳ vọng |
|---|---|---|
| LR/warmup quá mạnh hoặc AMP gây bất ổn | NaN9 epoch, val cls587,034, AdamW0.01 | Xin log gốc trước; sau đó pilot10–15 epoch cùng seed/batch, chỉ đổi lr0 xuống0.001 và warmup_bias_lr0.0. Kỳ vọng loss hữu hạn, không spike. Nếu vẫn lỗi, pilot riêng AMP=false; không thay đồng thời để quy nguyên nhân. |
| Nhãn thiếu/nhiễu/định nghĩa không thống nhất | Hai ví dụ thiếu Barcode và các vùng Spot/Wornout nghi vấn | Hai người rà cùng20 ảnh train/val có crop gốc, gồm ví dụ đã nêu; ghi đồng thuận về lớp và ranh giới. Kỳ vọng chỉ ra lỗi lặp lại và quy tắc có thể thống nhất; nếu đa số đồng thuận nhãn gốc, giảm ưu tiên giả thuyết nhiễu. |
| Chi tiết quá nhỏ, augmentation làm khó hơn | Spot/Wornout trung vị18px val; mosaic/scale0.5 | Kiểm crop trước/sau transform trên ảnh train, không train; kỳ vọng chi tiết lỗi bị co/khó thấy. Sau đó đối chứng640/960 cùng các tham số khác, báo recall theo nhóm kích thước. |
| Mất cân bằng, ít cuốn đa dạng | Train Ripped173box/43nhóm, Wornout544box/74nhóm | Đếm nhóm và kiểu lỗi, rà độ phủ; thử sampler theo cuốn hiếm trong train khi đã sạch. Kỳ vọng recall lớp thiếu tăng mà FP không tăng quá mức; không nhân bản ảnh trước split. |
| Ngưỡng chung thiên về Barcode | F1 chung gần0.35, AP lỗi vẫn thấp | Lần đánh giá val được phép sau này xuất raw predictions/PR arrays rồi quét ngưỡng từng lớp. Kỳ vọng tăng recall nhưng kiểm xem precision còn đạt sàn; nếu không có điểm khả dụng thì ngưỡng không cứu được model. |
| YOLO11n thiếu năng lực | Chỉ có một run n640, chưa có đối chứng | Khi pipeline ổn, s640 so với n640 cùng dữ liệu/seed/config. Kỳ vọng metric lỗi tăng rõ; nếu cả hai kém thì tiếp tục dữ liệu/định nghĩa, không tăng model vô hạn. |
| Khác miền line thực tế | Ảnh đã xem có bàn, tay giữ sách, góc chéo, lóa; chưa có bộ line | Chụp pilot sách trường trên đúng camera/ánh sáng. Kỳ vọng phát hiện khác biệt bố cục, tỷ lệ lỗi pixel và false alarms. Khác miền chưa giải thích được thất bại trên val hiện tại, nhưng là rủi ro triển khai riêng. |
| Val ít nhóm làm metric dao động | Ripped39box từ9nhóm; tất cả val18nhóm | Báo bootstrap theo nhóm sau khi có predictions, không theo box độc lập; kỳ vọng khoảng bất định rộng. Hiện một instance Ripped đã làm recall đổi2,56 điểm phần trăm. |
| Còn nhóm sách trùng khác góc giữa train/val | pHash chỉ sàng lọc cùng hình | Rà nhóm đại diện và SIFT những cặp nghi vấn, kỳ vọng xác nhận/loại rò rỉ. Không đổi split chỉ để metric đẹp hơn. |

## Kế hoạch lần 2 — đề xuất, chưa thay đổi quyết định đã duyệt

### Dữ liệu và định nghĩa

1. Ưu tiên **audit nhỏ20 ảnh đại diện cùng người thứ hai**:8 train+12 val, bao gồm sáu ảnh gốc đã nêu, chia đều rách/mòn/khuyết/bẩn, thêm barcode thiếu và mẫu âm. Đầu ra là danh sách lỗi và quy tắc annotation một trang; chưa cần rà lại620 ảnh. Đây là bước tiếp theo duy nhất được ưu tiên.
2. Khi thống nhất, tạo dataset phiên bản mới để sửa nhãn; giữ ZIP, manifest và split v1 nguyên vẹn. Barcode là mọi vùng mã1D nhìn thấy theo scope đã chọn, không chỉ tem thư viện; tem chữ không tự thành Barcode hay Spot. Notch=khuyết mất vật liệu, Ripped=rách/bong/tách lớp, Wornout=mòn/sờn, Spot=vết bẩn ngoại lai. Ranh giới giao nhau phải có ví dụ phân xử; một dải mòn liên tục không chia tùy ý thành nhiều hộp. Các định nghĩa chi tiết này cần được nhóm thống nhất trước khi áp dụng.
3. Thu pilot khoảng30–50 cuốn trường/nguồn khác dưới đúng camera, có sách sạch, chữ/họa tiết giống lỗi, bóng lóa và lỗi rõ/nhẹ. Giữ ảnh gốc độ phân giải cao, mã cuốn/thiết kế, phiên chụp, mặt sách và điều kiện sáng. Thu thêm các **cuốn** có lỗi hiếm; không cân bằng chỉ bằng thêm nhiều góc cùng cuốn. Pilot là khảo sát khả thi, không đủ chứng nhận chất lượng.
4. Khi mở rộng, giữ nhóm cuốn/thiết kế và phiên liên quan cùng tập; giữ test v1 đóng, không đưa ảnh/nhãn test vào audit hoặc tune. Nếu chỉ sửa nhãn train/val, ưu tiên giữ assignment cũ để so sánh; nếu cần chia lại do nhóm trùng/dữ liệu mới, tạo version và ghi lý do, mọi so sánh trên cùng split mới. Chọn mục tiêu70/15/15 theo nhóm trước khi xem metric. Dành nhóm ảnh line độc lập cho đánh giá cuối, không dùng đi dùng lại để chọn tham số.
5. Hướng thu thập sau pilot: tăng số nhóm val có lỗi, ưu tiên tối thiểu khoảng20 cuốn/thiết kế độc lập mỗi loại nếu khả thi. Đây là mục tiêu lấy mẫu, không phải ngưỡng đảm bảo thống kê; báo khoảng bất định và tỷ lệ lỗi trên line.

### Train có đối chứng

| Lượt đề xuất | Thay đổi | Mục đích / điều kiện |
|---|---|---|
| Pilot ổn định | yolo11n pretrained,640,batch16,seed42; AdamW lr0=0.001,warmup_bias_lr=0.0,warmup3;10–15epoch | Kiểm NaN; giữ augmentation run1 cho phép so sánh. Dừng ngay nếu loss/gradient không hữu hạn. AMP=false chỉ là phép thử riêng khi cần. |
| Baseline v2 | n640, optimizer đã ổn; mosaic0.2,scale0.2,translate0.05,hsv_s0.3,hsv_v0.2,fliplr0; không mixup/cutmix | Giảm co/cắt và biến màu của lỗi nhỏ; kiểm sample augmented trước khi chạy. Đây là ứng viên cấu hình, chưa chứng minh tốt hơn. |
| Đối chứng augmentation | n640 như baseline ổn định nhưng giữ augmentation v1 | Tách tác dụng làm sạch dữ liệu với tác dụng augmentation; tránh đổi mọi thứ rồi quy công cho model. |
| Đối chứng kích thước | n960, các tham số còn lại như baseline v2 | Cùng split, kiểm recall theo kích thước. Nguồn640 không có thêm chi tiết; batch giảm nếu OOM phải ghi và kiểm soát effective batch. |
| Đối chứng năng lực | s640, các tham số còn lại như baseline v2 | Chỉ đổi model; đo bộ nhớ, chất lượng lỗi và sau này latency trên máy đích. |

**[Đề xuất, chưa thực hiện]** Run đầy đủ tối đa150 epoch,patience25, ghi metric mỗi epoch. Không tăng tới300 mặc định; dừng khi metric ưu tiên không tăng có ý nghĩa qua25epoch hoặc có bất ổn. Early stopping mặc định Ultralytics dùng fitness AP50–95 tổng hợp; nếu muốn dừng/chọn checkpoint theo lỗi thì phải bổ sung callback hoặc đánh giá các checkpoint trên val, không giả định `patience` tự tối ưu recall lỗi. Lưu best theo tiêu chí lỗi bên cạnh best mặc định; lưu predictions/PR arrays, confusion matrix tại ngưỡng thực dùng, config validation riêng, log transfer/optimizer/NaN, seed và versions. Seed42 dùng so sánh đầu; chỉ cấu hình tốt nhất mới chạy thêm seed để đo dao động.

### Metric chọn model và ngưỡng

**[Đề xuất, chưa thực hiện]** Chọn theo **recall từng lớp lỗi tại sàn Precision đã chốt**, không theo P tổng hợp có Barcode. Báo recall ở P≥0.50 và P≥0.80 để thấy tradeoff; hai sàn này là đề xuất khảo sát, chưa là nghiệm thu của người dùng. Tại ngưỡng không có prediction, precision phải ghi N/A, không coi P=1/R=0 là đạt. Không có ngưỡng đạt sàn và recall hữu ích thì ghi không đạt.

Ưu tiên Ripped recall/F2; báo macro recall bốn lớp, lớp kém nhất, AP riêng lỗi, FP/ảnh hoặc FP/cuốn, tỷ lệ sách lỗi bị cho C và lỗi phân A/B. Mục tiêu Ripped recall≥90% chỉ là mục tiêu thiết kế cần thống nhất; không cam kết từ dataset này. Chọn ngưỡng trên val, khóa model/threshold, rồi mới đánh giá test cuối và camera độc lập. Với val chỉ9 nhóm Ripped, không dùng recall điểm để cam kết90% ngoài thực tế.

### Có nên gộp lớp hoặc đổi bài toán?

- **[Giả thuyết]** Gộp Notch/Spot/Wornout thành OtherDamage có thể giảm mơ hồ không ảnh hưởng tuyếnB; giữ Ripped riêng cho tuyếnA và Barcode riêng. Đây là phương án3 lớp để thử trên bản nhãn dẫn xuất khi audit cho thấy nhầm loại; không tự đổi hợp đồng5 lớp, không gộp Ripped vào lỗi chung khi vẫn cầnA/B. Không giải quyết được lỗi bị nhầm với background.
- **[Giả thuyết]** Phân loại cấp mặt sách OK/NG có thể hợp hơn nếu chỉ cần phát hiện có lỗi, nhưng không đủ phânA/B. Phân loại đa nhãn `has_ripped`/`has_other_damage` có thể giữ tuyến; cần nhãn cấp sách mới do người rà, không suy OK từ detector không thấy gì hoặc nhãn rỗng chưa kiểm. Phải kiểm mô hình có học bìa/nền thay vì lỗi không.
- **[Giả thuyết]** Detect sách rồi classify ROI/tile có thể giữ chi tiết và giảm nền; classifier toàn ảnh640 vẫn có thể mất lỗi nhỏ, pipeline hai tầng có thể bỏ sót ngay bước ROI. Kiểm rẻ nhất là audit crop/tile và nhãn cấp sách trước khi chọn kiến trúc. Không ưu tiên đổi bài toán trước khi giải thích NaN và chất lượng nhãn hiện tại.

## Đối chiếu bản Antigravity người dùng gửi

Đối chiếu ngày2026-11-11 với `docs/COLAB_RUN1_ANALYSIS.md`, `scripts/analyze_colab_run.py` và bản trả lời người dùng cung cấp. Không chỉnh sửa hai tệp đó. Các số dòng dưới đây theo bản được đối chiếu trong phiên; chúng có thể thay đổi nếu tác giả tiếp tục sửa.

| Mức độ | Phát hiện | Bằng chứng và cách sửa kết luận |
|---|---|---|
| Cao | Gán tác động cho augmentation không thuộc detection | **[Bằng chứng]** báo cáo Antigravity dòng44,230,276 quy `erasing=0.4`/randaugment làm mất lỗi, thậm chí mô tả xóa40%ảnh. Pipeline detection8.4.208 không dùng hai tham số này như đã đối chiếu mã ở trên. Xóa kết luận nhân quả đó; chỉ nghiên cứu mosaic/scale/HSV thực sự có dùng. Ngay trong classification, p=0.4 là xác suất áp dụng phép xóa vùng, không phải xóa40%diện tích hoặc bỏ40%ảnh. |
| Cao | Khẳng định LR gây NaN và phá hỏng pretrained vượt bằng chứng | **[Bằng chứng]** dòng213–214 khẳng định nổ gradient và trọng số pretrained bị phá hỏng. Artifacts có NaN/spike và LR0.01, không có gradient log hoặc đối chứng. Mã `engine/trainer.py:1199` đúng là tính auto AdamW `0.002*5/(4+5)=0.001111` cho lịch ngắn; đây là heuristic của auto, không phải chuẩn LR bắt buộc. Đổi nguyên nhân sang **[Giả thuyết]**, kiểm LR/warmup và AMP có kiểm soát. |
| Cao | Dùng yêu cầu hai lớp/A6 cũ trong đề xuất lần2 | **[Bằng chứng]** dòng239,256–269 giả định AI nhận630×888 và đề xuất quay về cover_tear/surface_stain. Yêu cầu mới là ảnh gốc quanh sách+biên5%, giữ tỷ lệ/letterbox, năm lớp, cóRipped luônA. Chỉ gộp Notch/Spot/Wornout vàoOtherDamage nếu chủ dự án duyệt; gộp cảRipped vào lỗi mép hoặc chỉ coi rách nặng mớiA làm mất/sai phân tuyến. Khả năng giải mã barcode riêng chưa được coi là đã nghiệm thu để tự bỏ lớpBarcode. |
| Vừa | Nhầm AP với P/R tại ngưỡng chung | **[Bằng chứng]** dòng280 gọi `mAP50-95` ởconf0.350. AP tích phân đườngPR theo mức confidence, rồi mAP50–95 trung bình theoIoU; không phải AP tại0.35. P/R summary mới lấy một điểm theoF1. Vì AP lỗi đã rất thấp, không quy toàn bộ thất bại cho ngưỡng chung. Đỉnh0.350 đọc từ ảnh đã làm tròn; không suy chính xác max-confidence hoặc TP/FP nguyên từ đường cong nội suy. |
| Vừa | Thử nhiều thay đổi cùng lúc không xác định nguyên nhân | **[Bằng chứng]** đề xuất G1 và phần bàn giao đổi LR,cosine,warmup,mosaic,scale,cls,đôi khi cả lớp/model. Nếu cải thiện sẽ chưa biết yếu tố nào gây ra. Tách pilot ổn định LR/warmup và đối chứng AMP, rồi mới augmentation/resolution/model. Không cam kết chắc loss<5 ngayepoch1 hoặc thời gian3–4phút. |
| Vừa | Kết luận dHash trong báo cáo không tái lập bằng script đi kèm | **[Bằng chứng]** dòng175 ghi3cặp; gọi trực tiếp `analyze_dataset_split` của chính script trên môi trường AI cho5cặp khác (bảng dưới). Chưa biết do phép resize/grayscale của công cụ trước khác script hay lỗi chuyển báo cáo. Cần lưu backend/version và đồng bộ danh sách. Sàng lọc hash không đủ để kết luận không có rò rỉ mọi góc chụp. |

**[Bằng chứng]** Hai script khớp toàn bộ số ảnh/instance từng lớp và sốbox diện tích<1024px². Xác minh trực tiếp thêm:37boxtrain và12boxval cóaspect>10; maxval40,5. Ba nhómval có74+72+40=186/327box (56,88%), từ6+6+5=17ảnh; đây là bổ sung hữu ích của Antigravity, hỗ trợ đánh giá bất định theo nhóm. Chạy hàm của script Antigravity cũng ra19cặptrain/4cặpval theo tiêu chíIoU≥0.25 hoặcIoA≥0.50; không mâu thuẫn với0cặpIoU≥0.90 của script này vì tiêu chí khác nhau. Hộp dẹt và chồng nhau chỉ là ứng viên rà, không tự chứng minh nhãn sai.

**[Bằng chứng]** Năm ứng viên dHash≤10 tái lập bằng OpenCV4.14.0 trong môi trườngAI:

| Train (tiền tố ảnh) | Val (tiền tố ảnh) | Hamming |
|---|---|---:|
| IMG_1746 | IMG_1436 | 8 |
| IMG_1050 | IMG_1436 | 9 |
| IMG_564 | IMG_1736 | 9 |
| IMG_154 | IMG_1011 | 10 |
| IMG_1781 | IMG_1011 | 10 |

**[Bằng chứng trực quan]** Đã mở thêm7ảnh gốc:train IMG_1746/1050/564/154/1781 vàval IMG_1436/1011; valIMG_1736 đã mở trước. Cặp1746/1436 là góc bìa xanh lá và gáy xanh da trời;1050/1436 là sách đen gáy nhãn400 và sách xanh nhãn900;564/1736 là gáy đỏ chữ vàng và gáy xanh bong mép;154/1011 là gáy đen và gáy xanh tím META;1781/1011 là gáy camBRITPOP và gáyMETA. Không thấy cùng ảnh trong5cặp này; với ảnh chỉ có góc bìa như1746, chưa xác nhận danh tính sách chỉ từ phần crop. Không mở rộng kết luận thành bảo đảm mọi nhóm độc lập.

**[Chưa kiểm tra]** Chưa xác nhận độc lập mọi ví dụ nhãn sai mà Antigravity nêu (đặc biệt mẫu âmIMG_1122/1225). Vùng khác nhau trên cùng sách hoặc góc nhìn khác không tự chứng minh mâu thuẫn nhãn; cần khớp đúng vị trí vật lý. AP50 cuối chững là quan sát hợp lý, nhưng câu “thêm epoch không giải quyết được” chưa được kiểm chứng; AP50–95 vẫn tăng nhẹ theo cửa sổ cuối.

**Hướng xử lý chung:** giữ các thống kê đã đối chiếu; điều chỉnh mức chắc chắn của kết luận; giữ hợp đồngnăm lớp/A-B-C/ROI gốc; audit20ảnh để chốt quy tắc trước pilot train có đối chứng. Không thực hiện train/remap trong phiên này.

## Tái lập và trạng thái kiểm chứng

Script dùng môi trường AI sẵn có, không cài/thay môi trường collector. Dependency phân tích đã có: PyYAML6.0.3, NumPy2.4.6, OpenCV4.14.0. Script không import Ultralytics/Torch, không mở tệp test, từ chối ghi đè đầu ra khác nội dung. Dữ liệu chi tiết ở `analysis.json` cục bộ; repo chỉ thêm script, báo cáo và bảng nhỏ.

```powershell
git -c safe.directory=D:/smart-vision-inspection status --short
git -c safe.directory=D:/smart-vision-inspection check-ignore -v data/local/damaged_books_v1/codex-analysis-20261111/artifacts
& 'data/local/worktrees/damaged-books-abc/.venv-ai/Scripts/python.exe' scripts/analyze_damaged_books_run.py --archive data/local/damaged_books_v1/colab-results/20261111T132200647414Z-artifacts.zip --dataset data/local/damaged_books_v1/split-reviewed-v1 --output data/local/damaged_books_v1/codex-analysis-20261111 --tables docs/DAMAGED_BOOKS_RUN1_TABLES.md
& '.venv/Scripts/python.exe' scripts/check_repository.py
git -c safe.directory=D:/smart-vision-inspection diff --check
```

**[Bằng chứng]** Phân tích và chạy lại trên dữ liệu thật: PASS; không đổi ZIP/614 tệp train-val; JSON kết quả chạy lại trùng nội dung. Kiểm cú pháp/liên kết repo và diff: xem kết quả cuối phiên ở PROGRESS/SESSION_LOG. Không chạy kiểm thử camera/hardware; không có đo latencyCPU. 10,44ms inference trong JSON là trên T4 Colab, không phải máy line.

**[Bằng chứng]** Tệp mới: báo cáo này, `docs/DAMAGED_BOOKS_RUN1_TABLES.md`, `scripts/analyze_damaged_books_run.py`. Cập nhật PROGRESS và thêm mục SESSION_LOG; giữ thay đổi có sẵn. Không commit/push/merge và không đưa ZIP/ảnh/weights vào Git. Trạng thái baseline đã có untracked `README.dataset.txt`, `README.roboflow.txt`, `data.yaml`, `train/`, `valid/`, `test/`; các tệp đó không bị sửa trong phân tích.

**[Bằng chứng về phối hợp]** Người dùng cho phép tiếp tục sau khi phát hiện thay đổi song song. Đã giữ nguyên `scripts/README.md`, `scripts/analyze_colab_run.py`, `docs/COLAB_RUN1_ANALYSIS.md` và các mục tiến độ/nhật ký của Antigravity. Phần bổ sung mới phân biệt lại: LR cao là giả thuyết nguyên nhân, NaN là quan sát; Precision=1/R=0 là kết quả quy ước nội suy chứ không phải phép chia0/0 trực tiếp; diện tích<32²px không tương đương cả hai cạnh<32px; pHash không chứng minh độc lập mọi góc chụp. Hai bản đề xuất khác thứ tự ưu tiên; báo cáo này đề xuất audit20 ảnh trước pilot train, chưa thay đổi kế hoạch thành hành động tự động.

**Một bước tiếp theo ưu tiên:** hai người audit chung20 ảnh theo mục dữ liệu, chốt quy tắc nhãn và danh sách sửa cho phiên bản mới trước khi train lần2.

# Quản lý dữ liệu

Repository chỉ chứa hướng dẫn quản lý dữ liệu. Ảnh camera, metadata của phiên thu, dataset, weights và backup được lưu riêng, không đưa vào Git.

| Đường dẫn cục bộ | Nội dung |
|---|---|
| data/opencv/collection | Phiên thu và bundle raw/crop/debug/metadata |
| data/opencv/validation | Ảnh và log phục vụ kiểm chứng |
| data/local | Backup và hồ sơ làm việc cục bộ |

Mỗi mẫu cần có nguồn real/imported/synthetic, session, timestamp và danh tính khi xác định được. Mẫu accepted và review được phân biệt trong metadata; ảnh đạt điều kiện thu chưa phải nhãn sách tốt.

Chia sẻ dữ liệu trong nhóm bằng kho riêng, kèm manifest/checksum và hướng dẫn khôi phục đường dẫn. Khi chuẩn bị dataset AI, chia nhóm theo cuốn/thiết kế bìa để tránh rò rỉ giữa train/validation/test.

[Hướng dẫn thu ảnh](../docs/COVER_CAPTURE.md) · [Module AI](../vision/yolo/README.md).

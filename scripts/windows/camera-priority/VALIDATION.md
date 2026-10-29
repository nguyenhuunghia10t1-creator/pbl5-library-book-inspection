# Kiểm chứng Camera Priority

Bộ kiểm thử gồm 23 ca mô phỏng policy và recovery: chọn đúng camera, thiết bị mất/kết nối lại, ownership, idempotence, lỗi cấu hình và khôi phục. Không gọi thao tác PnP, Task Scheduler hoặc ACL thật trong test.

Kết quả: 23/23 PASS. Cài đặt quản trị, Disable/Enable thiết bị, boot/sleep và chạy dài trên máy thật chưa được nghiệm thu.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/windows/camera-priority/Test-CameraPriority.ps1
```

[Hướng dẫn](README.md)

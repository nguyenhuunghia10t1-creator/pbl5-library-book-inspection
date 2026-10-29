# A4tech Camera Priority cho Windows

Công cụ độc lập cho laptop có **A4tech HD 720P PC Camera** và camera tích hợp. Không cần Python, OBS, driver camera ảo hay phần mềm trả phí. Dùng Windows PowerShell 5.1 và Task Scheduler có sẵn trên Windows 10/11; đã kiểm tra nhận dạng thiết bị trên Windows 11 build 26200 của máy này.

## Cách hoạt động và giới hạn

- Khi **một** A4tech đúng VID `09DA` / PID `2697` / camera interface đã chọn xuất hiện và PnP báo không lỗi qua hai lần kiểm tra: tạm **Disable camera laptop đã chọn**. Khi ứng dụng liệt kê camera hoạt động, A4tech là camera còn lại trên cấu hình hai camera này.
- Khi rút A4tech, tắt nó bằng Device Manager hoặc nó báo lỗi PnP: **Enable lại camera laptop nếu chính công cụ đã tắt nó**. Không tự bật camera đã bị người dùng tắt từ trước.
- Theo dõi `Win32_DeviceChangeEvent`; kiểm tra dự phòng mỗi 15 giây. Thời gian chuyển thực tế còn tùy driver; có thể cần khoảng 20 giây nếu sự kiện bị bỏ lỡ. Đây là khoảng chờ thiết kế, chưa phải độ trễ đã đo trên phần cứng.
- Chạy ẩn khi Windows khởi động, kể cả trước đăng nhập; hoạt động khi dùng pin. Không giữ/mở luồng hình ảnh, không ghi hình/âm thanh, không đụng microphone hay thiết bị khác. Chỉ một tiến trình PowerShell; RAM/CPU chưa đo trong vận hành nền.

**Đây là giải pháp thay thế bằng quản lý thiết bị.** Tài liệu Microsoft mô tả mặc định *thông số ảnh của từng camera*, không đưa ra một thiết lập chọn camera chung mà mọi ứng dụng bắt buộc tuân theo. Không dùng registry không được tài liệu hóa để giả lập một mặc định toàn hệ thống.

**Các ảnh hưởng cần biết trước khi cài:**

- Disable camera laptop ảnh hưởng mọi người dùng và mọi ứng dụng đang sử dụng chính camera đó. Cuộc gọi/phiên camera đang mở có thể bị ngắt. Nếu Windows Hello dùng chung thiết bị đó thì cũng có thể bị ảnh hưởng khi A4tech đang cắm. Bộ cài lọc tên IR/infrared/depth và yêu cầu bạn chọn camera RGB; không thể bảo đảm mọi driver đều đặt tên đầy đủ.
- Không chuyển liền mạch một luồng video đang mở. Sau cắm/rút, ứng dụng có thể tự tìm camera còn lại hoặc bạn phải tắt/bật video, mở lại ứng dụng. Ứng dụng lưu ID camera riêng, trình duyệt lưu quyền theo thiết bị, hay app dùng index cố định có thể báo mất camera thay vì tự chuyển. Không có bảo đảm chung cho mọi chương trình.
- Với OpenCV `cv2.VideoCapture(0)`: cần mở lại script sau khi danh sách thiết bị ổn định. Index do backend/driver quyết định; công cụ không sửa năm bài Python của project và không bảo đảm cùng index trên mọi backend.
- PnP báo sẵn sàng không chứng minh đọc được hình: công cụ không phát hiện A4tech bị ứng dụng khác chiếm, quyền camera bị chặn, hình đen hay driver đứng hình nhưng vẫn báo OK. Trong các trường hợp này dùng **Pause** để trả camera laptop về.
- Đổi cổng USB A4tech vẫn nhận theo VID/PID/interface, không theo số thứ tự camera. Hai A4tech cùng interface được cắm đồng thời thì không ưu tiên, trả camera laptop về. Đổi camera laptop/driver làm thay InstanceId thì gỡ và cài lại.

Nếu cần giữ cả hai camera luôn khả dụng hoặc tự đổi nguồn ngay trong cuộc gọi, cần chọn nguồn trong từng ứng dụng hoặc giải pháp camera ảo phức tạp hơn. Công cụ này ưu tiên tính gọn và khả năng hoàn tác.

## Cài đặt (một lần)

1. Cắm A4tech, đóng ứng dụng đang dùng camera. Giải nén ZIP nếu dùng bản đóng gói; giữ các tệp cạnh nhau.
2. Nhấp đúp **CameraPriority.cmd**. Chọn **2 — Install**. Chấp nhận hộp thoại **User Account Control** của Windows vì bật/tắt thiết bị cần quyền quản trị.
3. Chọn số ứng với **USB2.0 HD UVC WebCam** (camera laptop đã nhận trên máy này). Bộ cài in cả tên và InstanceId; kiểm tra đúng thiết bị.
4. Đọc phạm vi thay đổi hiển thị, gõ **INSTALL** rồi Enter để cài và chạy. Có thể hủy trước bước này, không có thay đổi hệ thống.
5. Mở lại **CameraPriority.cmd**, chọn **3 — Status**, rồi làm kiểm tra bên dưới.

Bộ cài chép công cụ vào `%ProgramFiles%\A4techCameraPriority`, tạo task `\A4techCameraPriority` chạy bằng `SYSTEM` khi khởi động. Không lưu mật khẩu. Script/config/state/log chỉ cho SYSTEM và Administrators sửa; Users được đọc/chạy. Có thể xóa thư mục giải nén sau khi cài. Về sau mở công cụ tại thư mục Program Files để quản lý.

Không thay Execution Policy toàn máy: `-ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình chạy công cụ. Chính sách cơ quan/WDAC/AppLocker có thể vẫn chặn; không tự bỏ qua chính sách đó. Bộ công cụ dạng script, chưa ký mã.

## Sử dụng

Mở **CameraPriority.cmd** ở thư mục cài đặt hoặc bản nguồn:

| Số | Tác dụng |
|---|---|
| 1 — Diagnose | Chỉ đọc Windows và danh sách camera, không cần admin. |
| 2 — Install | Cài và bật tự động; yêu cầu admin và xác nhận trong bộ cài. |
| 3 — Status | Xem camera, trạng thái task và 12 dòng log gần nhất. Nếu tài khoản thường không đọc được task SYSTEM, dùng PowerShell quản trị để chạy Status. |
| 4 — Pause + restore laptop | Dừng tự động, vô hiệu task qua cả lần khởi động sau, khôi phục camera laptop do công cụ tắt. |
| 5 — Resume | Bật lại task và chạy ngay; tự động chọn theo thiết bị đang có. |
| 6 — Uninstall | Dừng task, khôi phục camera do công cụ tắt, xóa task và thư mục cài. |

Sau cài đặt không cần chọn camera mỗi ngày. Windows vẫn phải cho phép ứng dụng truy cập camera trong **Settings → Privacy & security → Camera**.

## Kiểm tra sau cài

Thử tuần tự cùng ứng dụng bạn thường dùng; không mở nhiều ứng dụng tranh camera:

1. **A4tech cắm:** đợi tối đa khoảng 20 giây, Status phải thấy A4tech `Code 0`, laptop `Code 22`, task `Running`, log `PREFERRED`. Mở ứng dụng và che ống kính A4tech để xác minh nguồn hình thật.
2. **Rút A4tech:** đợi tương tự, Status thấy laptop `Code 0`, log `RESTORED`. Mở lại ứng dụng để xác minh hình từ laptop.
3. **Cắm lại:** laptop trở về `Code 22`; kiểm tra hình A4tech sau khi mở lại ứng dụng.
4. **Khởi động lại Windows:** kiểm tra cả hai trạng thái có/không A4tech, xác nhận task tự chạy. Thử sleep/resume, chạy bằng pin. Nếu đang mở video khi rút USB, ghi rõ ứng dụng tự chuyển hay phải mở lại.
5. **Pause:** laptop phải được bật lại, task `Disabled`; khởi động lại vẫn tạm dừng. **Resume** phải bật lại tự động. **Uninstall** phải xóa task và thư mục, camera laptop hoạt động lại.

Các thao tác thiết bị, chạy SYSTEM, boot/sleep và ứng dụng thật **chưa được nghiệm thu trên thiết bị thật**. Kết quả kiểm thử mô phỏng và chẩn đoán chỉ đọc nằm trong [VALIDATION.md](VALIDATION.md) của bộ nguồn/ZIP.

## Lỗi và khôi phục

- Có lỗi: chọn **3 — Status**, xem `%ProgramFiles%\A4techCameraPriority\camera-priority.log` (xoay vòng một bản `.1` khi quá 1 MiB). Không ghi log mỗi lần kiểm tra, chỉ lúc đổi trạng thái/khởi động/lỗi.
- Worker lỗi sẽ thử bật lại camera thuộc quyền quản lý, thoát với mã lỗi để Task Scheduler thử khởi động lại sau một phút (tối đa 999 lần). Nếu bị kill/mất điện, bản ghi ownership đã lưu trước Disable; worker sẽ xử lý lại khi được khởi động. Lỗi đọc config/state có thể cần khôi phục thủ công. Đây không phải bảo đảm phục hồi tức thời.
- **Pause/Uninstall** không xác nhận bật lại được camera thì giữ file/config để còn khôi phục; không báo gỡ thành công. Nếu laptop đang vắng khỏi PnP, khởi động lại rồi Pause lần nữa.
- Khẩn cấp: mở **Task Scheduler → Task Scheduler Library → A4techCameraPriority → Disable, rồi End**. Mở **Device Manager → Cameras → USB2.0 HD UVC WebCam → Enable device** (chỉ đúng camera laptop). Dừng task trước để tránh công cụ tắt lại. Không tắt USB controller hoặc microphone.
- Nếu cài thất bại trước khi có `config.json` và chưa tạo task, kiểm tra Status/Device Manager; thư mục cài dở có thể cần quản trị viên xóa thủ công sau khi xác nhận chỉ chứa file của công cụ.

## Gỡ bỏ

Chạy **CameraPriority.cmd → 6 — Uninstall**, chấp nhận UAC. Bộ gỡ phục hồi camera do công cụ tắt trước khi xóa task và tệp. Không chỉ xóa thư mục khi task còn hoạt động. Bản nguồn/ZIP trong project không bị xóa; bạn có thể tự xóa sau.

Lệnh PowerShell tương đương (ví dụ chẩn đoán không hỏi đóng cửa sổ):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\windows\camera-priority\CameraPriority.ps1" -Mode Diagnose -NoPause
```

Đổi `Diagnose` thành `Status`, `Pause`, `Resume`, `Install` hoặc `Uninstall` nếu cần. Những lệnh ghi hệ thống tự yêu cầu UAC.

## Nguồn kỹ thuật

- [Microsoft: camera settings và mặc định thông số ảnh từng thiết bị](https://support.microsoft.com/en-us/windows/hardware/camera/manage-cameras-with-camera-settings-in-windows-11).
- [Microsoft: Disable-PnpDevice cần tài khoản quản trị](https://learn.microsoft.com/en-us/powershell/module/pnpdevice/disable-pnpdevice).
- [Microsoft: sự kiện thiết bị Win32_DeviceChangeEvent](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-devicechangeevent).
- [Microsoft: thiết lập Scheduled Task, pin và khởi động lại](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset).

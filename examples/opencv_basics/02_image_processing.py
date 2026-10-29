import cv2  # Import thư viện OpenCV để làm việc với camera và xử lý ảnh


# ============================================================
# 1. MỞ CAMERA
# ============================================================

# VideoCapture(0) dùng để mở camera có ID = 0.
# Thông thường:
#   0 = camera mặc định / webcam tích hợp
#   1 = camera thứ hai
#   2 = camera thứ ba...
#
# Biến "cap" sẽ đại diện cho camera mà chương trình đang sử dụng.
cap = cv2.VideoCapture(0)


# ============================================================
# 2. VÒNG LẶP ĐỌC ẢNH LIÊN TỤC TỪ CAMERA
# ============================================================

# while True nghĩa là vòng lặp chạy liên tục,
# cho đến khi chúng ta chủ động dùng "break" để thoát.
while True:

    # cap.read() lấy 1 frame (1 ảnh) mới nhất từ camera.
    #
    # Hàm này trả về 2 giá trị:
    #
    # ret:
    #   True  -> đọc ảnh thành công
    #   False -> không đọc được ảnh
    #
    # frame:
    #   chính là ảnh màu vừa lấy được từ camera.
    #
    # Video thực chất là rất nhiều frame được lấy liên tục.
    ret, frame = cap.read()


    # ========================================================
    # 3. KIỂM TRA CAMERA CÓ ĐỌC ĐƯỢC ẢNH KHÔNG
    # ========================================================

    # "not ret" nghĩa là:
    # nếu ret = False -> không đọc được ảnh từ camera.
    if not ret:

        # In thông báo lỗi ra Terminal.
        print("Khong doc duoc camera")

        # Thoát khỏi vòng lặp while.
        break


    # ========================================================
    # 4. CHUYỂN ẢNH MÀU SANG ẢNH XÁM - GRAYSCALE
    # ========================================================

    # frame ban đầu là ảnh màu.
    #
    # OpenCV mặc định lưu màu theo thứ tự:
    # BGR = Blue - Green - Red
    #
    # cv2.cvtColor() dùng để chuyển đổi hệ màu.
    #
    # cv2.COLOR_BGR2GRAY nghĩa là:
    # chuyển từ ảnh màu BGR -> ảnh xám Grayscale.
    #
    # Ảnh màu:
    # mỗi pixel có 3 giá trị B, G, R.
    #
    # Ví dụ:
    # pixel = [50, 120, 200]
    #
    # Ảnh grayscale:
    # mỗi pixel chỉ còn 1 giá trị độ sáng.
    #
    # Ví dụ:
    # pixel = 135
    #
    # Kết quả được lưu vào biến "gray".
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    # ========================================================
    # 5. LÀM MỜ ẢNH ĐỂ GIẢM NHIỄU
    # ========================================================

    # GaussianBlur() sử dụng Gaussian Filter để làm mượt ảnh.
    #
    # Mục đích:
    # - giảm nhiễu nhỏ
    # - giảm các chi tiết không cần thiết
    # - giúp bước Threshold phía sau ổn định hơn
    #
    # Cú pháp:
    #
    # cv2.GaussianBlur(
    #     ảnh đầu vào,
    #     kích thước kernel,
    #     sigma
    # )
    #
    # gray:
    #   ảnh grayscale vừa tạo.
    #
    # (5, 5):
    #   kích thước kernel lọc là 5x5 pixel.
    #
    # Có thể hình dung OpenCV dùng một "cửa sổ" 5x5
    # quét qua toàn bộ ảnh để làm mượt ảnh.
    #
    # 0:
    #   để OpenCV tự tính giá trị sigma phù hợp.
    #
    # Kết quả được lưu vào "blur".
    blur = cv2.GaussianBlur(gray, (5, 5), 0)


    # ========================================================
    # 6. THRESHOLD - CHUYỂN ẢNH XÁM THÀNH ẢNH ĐEN/TRẮNG
    # ========================================================

    # threshold() dùng để biến ảnh grayscale thành ảnh nhị phân.
    #
    # Ảnh grayscale:
    #
    # pixel có giá trị từ:
    #
    # 0 ---------> 255
    # đen            trắng
    #
    # Threshold sẽ so sánh từng pixel với một giá trị ngưỡng.
    #
    # Ở đây ngưỡng = 120.
    #
    # Nếu pixel > 120:
    #       pixel mới = 255 (trắng)
    #
    # Nếu pixel <= 120:
    #       pixel mới = 0 (đen)
    #
    # Ví dụ:
    #
    # pixel gốc = 70
    # 70 <= 120
    # -> pixel mới = 0
    #
    # pixel gốc = 180
    # 180 > 120
    # -> pixel mới = 255
    #
    # cv2.threshold() trả về 2 giá trị:
    #
    # giá trị thứ nhất:
    #   threshold thực tế được sử dụng
    #
    # giá trị thứ hai:
    #   ảnh sau threshold
    #
    # Vì ở đây ta không cần giá trị thứ nhất,
    # nên dùng dấu "_" để bỏ qua nó.
    _, thresh = cv2.threshold(

        blur,               # Ảnh đầu vào

        120,                # Ngưỡng threshold

        255,                # Giá trị pixel lớn nhất sau threshold

        cv2.THRESH_BINARY   # Kiểu threshold nhị phân
    )


    # ========================================================
    # 7. HIỂN THỊ CÁC ẢNH
    # ========================================================

    # Hiển thị ảnh màu gốc từ camera.
    cv2.imshow("Original", frame)

    # Hiển thị ảnh grayscale.
    cv2.imshow("Gray", gray)

    # Hiển thị ảnh sau threshold.
    #
    # Ảnh này chỉ còn:
    # 0   = đen
    # 255 = trắng
    cv2.imshow("Threshold", thresh)


    # ========================================================
    # 8. KIỂM TRA NGƯỜI DÙNG CÓ NHẤN PHÍM "q" KHÔNG
    # ========================================================

    # cv2.waitKey(1):
    #   chờ khoảng 1 mili-giây và kiểm tra bàn phím.
    #
    # ord("q"):
    #   lấy mã số của ký tự "q".
    #
    # Nếu phím vừa nhấn là "q":
    #   điều kiện trở thành True.
    if cv2.waitKey(1) & 0xFF == ord("q"):

        # Thoát khỏi vòng lặp while.
        break


# ============================================================
# 9. GIẢI PHÓNG CAMERA
# ============================================================

# Khi chương trình kết thúc,
# cần giải phóng camera để các chương trình khác có thể sử dụng.
cap.release()


# ============================================================
# 10. ĐÓNG TẤT CẢ CỬA SỔ OPENCV
# ============================================================

cv2.destroyAllWindows()
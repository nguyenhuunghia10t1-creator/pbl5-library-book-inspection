import cv2


# ============================================================
# 1. MỞ VÀ KIỂM TRA CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

# [CẢI TIẾN 2]: Kiểm tra xem camera có thực sự mở thành công không
# Giúp phát hiện sớm lỗi cắm camera, trùng cổng hoặc quyền truy cập webcam
if not cap.isOpened():
    raise RuntimeError("Khong the mo camera! Vui long kiem tra lai ket noi hoac quyen truy cap.")

# Ngưỡng diện tích tối thiểu (pixel) để loại bỏ các hạt bụi / nhiễu nhỏ li ti
MIN_AREA = 1000


# ============================================================
# 2. VÒNG LẶP XỬ LÝ FRAME (ĐẶT TRONG TRY - FINALLY)
# ============================================================

# [CẢI TIẾN 4]: Dùng khối try...finally để đảm bảo camera LUÔN được giải phóng,
# kể cả khi chương trình bị tắt đột ngột bằng phím Ctrl+C hoặc gặp lỗi ngoại lệ (exception).
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Khong doc duoc frame tu camera")
            break


        # ========================================================
        # 3. TIỀN XỬ LÝ ẢNH & TỰ ĐỘNG PHÂN NGƯỠNG (OTSU)
        # ========================================================

        # Bước 3.1: Chuyển sang ảnh xám
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Bước 3.2: Làm mờ Gaussian để triệt tiêu nhiễu tần số cao
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # [CẢI TIẾN 1]: Áp dụng thuật toán Otsu để tự động tìm ngưỡng tối ưu.
        # - Thay vì cố định ngưỡng 120 (rất dễ sai khi ánh sáng phòng thay đổi),
        #   cv2.THRESH_OTSU sẽ phân tích biểu đồ histogram để tự tính giá trị ngưỡng tốt nhất.
        # - THRESH_BINARY_INV: Dùng cho trường hợp vật thể tối màu trên nền sáng (hoặc vật thể đặt trên bàn/giấy trắng).
        #   Quy tắc bắt buộc: VẬT THỂ PHẢI LÀ MÀU TRẮNG (255) thì findContours mới nhận diện đúng!
        #   (Nếu bạn kiểm tra vật sáng trên nền đen, chỉ cần dùng THRESH_BINARY + cv2.THRESH_OTSU)
        _, thresh = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )


        # ========================================================
        # 4. TÌM ĐƯỜNG VIỀN (CONTOURS)
        # ========================================================

        # RETR_EXTERNAL: Chỉ lấy đường bao ngoài cùng, bỏ qua cấu trúc lỗ bên trong
        # CHAIN_APPROX_SIMPLE: Nén các điểm thừa trên cạnh thẳng để tối ưu hiệu năng
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


        # ========================================================
        # 5. LỌC VÀ SẮP XẾP VẬT THỂ
        # ========================================================

        # Lọc danh sách các contour đủ điều kiện diện tích trước
        valid_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > MIN_AREA:
                valid_contours.append(cnt)

        # [CẢI TIẾN 5]: Sắp xếp thứ tự các vật thể từ TRÁI sang PHẢI theo tọa độ x.
        # Trong công nghiệp (băng chuyền), việc sắp xếp giúp đánh số cố định (#1, #2, #3...)
        # thay vì thứ tự bị nhảy lung tung giữa các frame hình.
        valid_contours = sorted(
            valid_contours,
            key=lambda c: cv2.boundingRect(c)[0]
        )


        # ========================================================
        # 6. VẼ ĐƯỜNG VIỀN, BOUNDING BOX VÀ THÔNG SỐ
        # ========================================================

        for i, cnt in enumerate(valid_contours):
            area = cv2.contourArea(cnt)

            # Vẽ đường viền thực tế của sản phẩm (màu xanh lá)
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

            # Lấy hình chữ nhật bao quanh (Bounding Box)
            x, y, w, h = cv2.boundingRect(cnt)

            # Vẽ hộp chữ nhật màu đỏ bao quanh sản phẩm
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # [CẢI TIẾN 3]: Đảm bảo vị trí chữ không bao giờ bị tràn khỏi mép trên của ảnh.
            # Nếu vật thể nằm sát viền trên (y < 25), ta đẩy chữ xuống dưới góc hộp thay vì để ngoài khung.
            text_y = y - 10 if y >= 25 else y + 20

            # Đánh số thứ tự (#1, #2...) và in diện tích, kích thước
            info_text = f"#{i + 1}: Area {int(area)} | {w}x{h}"
            cv2.putText(
                frame,
                info_text,
                (x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1
            )


        # ========================================================
        # 7. HIỂN THỊ TRẠNG THÁI TỔNG QUAN
        # ========================================================

        status_text = f"Objects detected: {len(valid_contours)}"
        cv2.putText(
            frame,
            status_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 0),  # Màu xanh dương
            2
        )


        # ========================================================
        # 8. HIỂN THỊ CÁC CỬA SỔ XỬ LÝ
        # ========================================================

        cv2.imshow("Smart Vision - Object Detection", frame)
        cv2.imshow("Threshold (Otsu)", thresh)


        # Thoát khi nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # ========================================================
    # 9. GIqqqqqqqqqqq===================================================
    # Luôn luôn được gọi dù code có gặp crash, Exception hay nhấn Ctrl+C
    cap.release()
    cv2.destroyAllWindows()


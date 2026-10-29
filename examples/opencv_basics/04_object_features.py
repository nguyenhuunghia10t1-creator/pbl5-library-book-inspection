import cv2
import math


# ============================================================
# 1. MỞ VÀ KIỂM TRA CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError(
        "Khong the mo camera! "
        "Vui long kiem tra ket noi hoac quyen truy cap."
    )


# Diện tích contour tối thiểu để loại bỏ nhiễu nhỏ
MIN_AREA = 1000

# Khoảng cách tối thiểu từ vật thể đến mép ảnh
# Nếu contour nằm trong vùng 5 pixel sát mép -> bỏ qua
BORDER_MARGIN = 5


# ============================================================
# 2. VÒNG LẶP XỬ LÝ CAMERA
# ============================================================

try:

    while True:

        # --------------------------------------------------------
        # ĐỌC FRAME TỪ CAMERA
        # --------------------------------------------------------

        ret, frame = cap.read()

        if not ret:
            print("Khong doc duoc frame tu camera")
            break


        # Lấy kích thước ảnh
        frame_height, frame_width = frame.shape[:2]


        # ========================================================
        # 3. TIỀN XỬ LÝ ẢNH
        # ========================================================

        # Chuyển ảnh màu BGR -> ảnh xám
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        # Làm mờ Gaussian để giảm nhiễu
        blur = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )


        # --------------------------------------------------------
        # THRESHOLD BẰNG OTSU
        # --------------------------------------------------------
        #
        # Otsu tự động tìm giá trị threshold phù hợp.
        #
        # THRESH_BINARY_INV:
        #
        #     vật tối    -> trắng
        #     nền sáng   -> đen
        #
        # findContours() sẽ tìm các vùng màu trắng.
        #

        _, thresh = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )


        # ========================================================
        # 4. TÌM CONTOUR
        # ========================================================

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


        # ========================================================
        # 5. LỌC CONTOUR
        # ========================================================

        valid_contours = []


        for cnt in contours:

            # ----------------------------------------------------
            # 5.1 LỌC THEO DIỆN TÍCH
            # ----------------------------------------------------

            area = cv2.contourArea(cnt)

            # Contour quá nhỏ -> coi là nhiễu
            if area < MIN_AREA:
                continue


            # ----------------------------------------------------
            # 5.2 LẤY BOUNDING BOX
            # ----------------------------------------------------

            x, y, w, h = cv2.boundingRect(cnt)


            # ----------------------------------------------------
            # 5.3 BỎ VẬT THỂ CHẠM MÉP ẢNH
            # ----------------------------------------------------
            #
            # Nếu vật thể bị cắt mất một phần bởi mép camera
            # thì Area, Perimeter, Circularity... sẽ không còn
            # phản ánh đúng toàn bộ vật thể.
            #

            if (
                x <= BORDER_MARGIN
                or y <= BORDER_MARGIN
                or x + w >= frame_width - BORDER_MARGIN
                or y + h >= frame_height - BORDER_MARGIN
            ):
                continue


            # Nếu vượt qua tất cả điều kiện trên
            # -> đây là contour hợp lệ
            valid_contours.append(cnt)


        # --------------------------------------------------------
        # SẮP XẾP VẬT THỂ TỪ TRÁI -> PHẢI
        # --------------------------------------------------------

        valid_contours = sorted(
            valid_contours,
            key=lambda c: cv2.boundingRect(c)[0]
        )


        # ========================================================
        # 6. TÍNH ĐẶC TRƯNG TỪNG VẬT THỂ
        # ========================================================

        for i, cnt in enumerate(valid_contours):


            # ====================================================
            # 6.1 AREA - DIỆN TÍCH
            # ====================================================

            area = cv2.contourArea(cnt)


            # ====================================================
            # 6.2 PERIMETER - CHU VI
            # ====================================================
            #
            # True:
            # contour được xem là một đường khép kín.
            #

            perimeter = cv2.arcLength(
                cnt,
                True
            )


            # ====================================================
            # 6.3 BOUNDING BOX
            # ====================================================

            x, y, w, h = cv2.boundingRect(cnt)


            # Vẽ hình chữ nhật bao quanh vật thể
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )


            # ====================================================
            # 6.4 ASPECT RATIO
            # ====================================================
            #
            #          Width
            # AR = -------------
            #          Height
            #
            #
            # AR = 1
            # -> rộng gần bằng cao
            #
            # AR > 1
            # -> rộng hơn cao
            #
            # AR < 1
            # -> cao hơn rộng
            #

            if h > 0:

                aspect_ratio = w / h

            else:

                aspect_ratio = 0


            # ====================================================
            # 6.5 CENTER - TÂM VẬT THỂ
            # ====================================================
            #
            # moments() tính các moment hình học của contour.
            #

            M = cv2.moments(cnt)


            if M["m00"] != 0:

                center_x = int(
                    M["m10"] / M["m00"]
                )

                center_y = int(
                    M["m01"] / M["m00"]
                )

            else:

                # Trường hợp đặc biệt nếu moment bằng 0
                # thì dùng tâm bounding box
                center_x = x + w // 2
                center_y = y + h // 2


            # Vẽ tâm vật thể
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (255, 0, 0),
                -1
            )


            # ====================================================
            # 6.6 CIRCULARITY - ĐỘ TRÒN
            # ====================================================
            #
            #                  4 × pi × Area
            #
            # Circularity = --------------------
            #
            #                   Perimeter²
            #
            #
            # Hình tròn lý tưởng:
            #
            # Circularity ≈ 1
            #
            # Hình càng méo / dài:
            #
            # Circularity càng nhỏ.
            #

            if perimeter > 0:

                circularity = (
                    4
                    * math.pi
                    * area
                    / (perimeter ** 2)
                )

            else:

                circularity = 0


            # ====================================================
            # 7. VẼ CONTOUR
            # ====================================================

            cv2.drawContours(
                frame,
                [cnt],
                -1,
                (0, 255, 0),
                2
            )


            # ====================================================
            # 8. CHUẨN BỊ THÔNG TIN HIỂN THỊ
            # ====================================================

            text1 = (
                f"#{i + 1} "
                f"Area:{int(area)} "
                f"Peri:{perimeter:.1f}"
            )


            text2 = (
                f"W:{w} H:{h} "
                f"AR:{aspect_ratio:.2f}"
            )


            text3 = (
                f"Circ:{circularity:.2f} "
                f"Center:({center_x},{center_y})"
            )


            # ----------------------------------------------------
            # TÍNH VỊ TRÍ ĐẶT CHỮ
            # ----------------------------------------------------

            text_y = y - 50


            # Nếu phía trên không đủ chỗ
            # -> đưa chữ xuống phía dưới vật thể
            if text_y < 20:

                text_y = y + h + 20


            # ====================================================
            # 9. HIỂN THỊ THÔNG TIN
            # ====================================================

            cv2.putText(
                frame,
                text1,
                (x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                1
            )


            cv2.putText(
                frame,
                text2,
                (x, text_y + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                1
            )


            cv2.putText(
                frame,
                text3,
                (x, text_y + 36),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 0, 0),
                1
            )


        # ========================================================
        # 10. HIỂN THỊ TỔNG SỐ VẬT THỂ
        # ========================================================

        status_text = (
            f"Objects: {len(valid_contours)}"
        )


        cv2.putText(
            frame,
            status_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 0),
            2
        )


        # ========================================================
        # 11. HIỂN THỊ CỬA SỔ
        # ========================================================

        cv2.imshow(
            "Object Features",
            frame
        )


        cv2.imshow(
            "Threshold",
            thresh
        )


        # ========================================================
        # 12. NHẤN Q ĐỂ THOÁT
        # ========================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ============================================================
# 13. GIẢI PHÓNG CAMERA
# ============================================================

finally:

    cap.release()

    cv2.destroyAllWindows()
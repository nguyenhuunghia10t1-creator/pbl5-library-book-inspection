import cv2


# ============================================================
# 1. MỞ CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Khong the mo camera!")


# ============================================================
# 2. THÔNG SỐ CƠ BẢN
# ============================================================

# Bỏ các contour quá nhỏ
MIN_CONTOUR_AREA = 2000

# Bỏ vật thể chạm biên
BORDER_MARGIN = 10


# ============================================================
# 3. SAI SỐ CHO PHÉP
# ============================================================
#
# Sau khi nhấn R để lấy vật chuẩn:
#
# Area được phép sai ±25%
# Aspect Ratio được phép sai ±15%
# Rectangularity được phép sai ±15%
#

AREA_TOLERANCE = 0.25

ASPECT_TOLERANCE = 0.15

RECT_TOLERANCE = 0.15


# ============================================================
# 4. BIẾN LƯU SẢN PHẨM CHUẨN
# ============================================================

reference_area = None

reference_aspect = None

reference_rectangularity = None


# ============================================================
# 5. VÒNG LẶP CAMERA
# ============================================================

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Khong doc duoc camera")
            break


        frame_height, frame_width = frame.shape[:2]


        # ========================================================
        # 6. TIỀN XỬ LÝ
        # ========================================================

        # Ảnh màu -> grayscale
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        # Làm mờ giảm nhiễu
        blur = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )


        # Otsu Threshold
        #
        # Vật tối trên nền sáng:
        #
        # vật -> trắng
        # nền -> đen
        #

        _, thresh = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )


        # ========================================================
        # 7. TÌM CONTOUR
        # ========================================================

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


        valid_contours = []


        # ========================================================
        # 8. LỌC CONTOUR
        # ========================================================

        for cnt in contours:

            area = cv2.contourArea(cnt)

            if area < MIN_CONTOUR_AREA:
                continue


            x, y, w, h = cv2.boundingRect(cnt)


            # Bỏ vật chạm mép ảnh
            if (
                x <= BORDER_MARGIN
                or y <= BORDER_MARGIN
                or x + w >= frame_width - BORDER_MARGIN
                or y + h >= frame_height - BORDER_MARGIN
            ):
                continue


            valid_contours.append(cnt)


        # ========================================================
        # 9. CHỈ LẤY VẬT THỂ LỚN NHẤT
        # ========================================================
        #
        # Như vậy bàn, tay, nhiễu nhỏ...
        # ít ảnh hưởng hơn.
        #

        current_features = None


        if len(valid_contours) > 0:

            largest_contour = max(
                valid_contours,
                key=cv2.contourArea
            )


            # ====================================================
            # 10. TÍNH ĐẶC TRƯNG
            # ====================================================

            area = cv2.contourArea(
                largest_contour
            )


            x, y, w, h = cv2.boundingRect(
                largest_contour
            )


            # ----------------------------------------------------
            # ASPECT RATIO
            # ----------------------------------------------------
            #
            # Ta lấy cạnh dài / cạnh ngắn.
            #
            # Vì vậy dù bạn xoay điện thoại ngang hay dọc,
            # Aspect Ratio vẫn gần giống nhau.
            #

            long_side = max(w, h)

            short_side = min(w, h)


            if short_side > 0:

                aspect_ratio = (
                    long_side / short_side
                )

            else:

                aspect_ratio = 0


            # ----------------------------------------------------
            # RECTANGULARITY
            # ----------------------------------------------------
            #
            #                    Area contour
            #
            # Rectangularity = ------------------
            #
            #                       w x h
            #
            #
            # Hình chữ nhật lấp đầy Bounding Box:
            #
            # Rectangularity gần 1
            #

            bounding_area = w * h


            if bounding_area > 0:

                rectangularity = (
                    area / bounding_area
                )

            else:

                rectangularity = 0


            # Lưu đặc trưng vật hiện tại
            current_features = (
                area,
                aspect_ratio,
                rectangularity
            )


            # ====================================================
            # 11. KIỂM TRA OK / NG
            # ====================================================

            # Chưa có sản phẩm chuẩn
            if reference_area is None:

                status = "PRESS R TO SET REFERENCE"

                color = (0, 255, 255)


            else:

                # ------------------------------------------------
                # AREA
                # ------------------------------------------------

                area_min = (
                    reference_area
                    * (1 - AREA_TOLERANCE)
                )

                area_max = (
                    reference_area
                    * (1 + AREA_TOLERANCE)
                )


                area_ok = (
                    area_min
                    <= area
                    <= area_max
                )


                # ------------------------------------------------
                # ASPECT RATIO
                # ------------------------------------------------

                aspect_min = (
                    reference_aspect
                    * (1 - ASPECT_TOLERANCE)
                )

                aspect_max = (
                    reference_aspect
                    * (1 + ASPECT_TOLERANCE)
                )


                aspect_ok = (
                    aspect_min
                    <= aspect_ratio
                    <= aspect_max
                )


                # ------------------------------------------------
                # RECTANGULARITY
                # ------------------------------------------------

                rect_min = (
                    reference_rectangularity
                    * (1 - RECT_TOLERANCE)
                )

                rect_max = (
                    reference_rectangularity
                    * (1 + RECT_TOLERANCE)
                )


                rectangularity_ok = (
                    rect_min
                    <= rectangularity
                    <= rect_max
                )


                # =================================================
                # QUYẾT ĐỊNH
                # =================================================

                if (
                    area_ok
                    and aspect_ok
                    and rectangularity_ok
                ):

                    status = "OK"

                    color = (0, 255, 0)


                else:

                    status = "NG"

                    color = (0, 0, 255)


            # ====================================================
            # 12. VẼ CONTOUR + BOUNDING BOX
            # ====================================================

            cv2.drawContours(
                frame,
                [largest_contour],
                -1,
                color,
                2
            )


            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                2
            )


            # ====================================================
            # 13. HIỂN THỊ THÔNG TIN
            # ====================================================

            cv2.putText(
                frame,
                status,
                (x, max(30, y - 60)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )


            cv2.putText(
                frame,
                f"Area: {int(area)}",
                (x, max(50, y - 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )


            cv2.putText(
                frame,
                f"AR: {aspect_ratio:.2f}",
                (x, max(70, y - 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )


            cv2.putText(
                frame,
                f"Rect: {rectangularity:.2f}",
                (x, y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )


        # ========================================================
        # 14. HƯỚNG DẪN
        # ========================================================

        cv2.putText(
            frame,
            "R = Set reference",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )


        cv2.putText(
            frame,
            "Q = Quit",
            (20, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )


        # ========================================================
        # 15. HIỂN THỊ
        # ========================================================

        cv2.imshow(
            "Rule Based Inspection",
            frame
        )

        cv2.imshow(
            "Threshold",
            thresh
        )


        # ========================================================
        # 16. ĐỌC PHÍM
        # ========================================================

        key = cv2.waitKey(1) & 0xFF


        # --------------------------------------------------------
        # Nhấn R -> lấy vật hiện tại làm sản phẩm chuẩn
        # --------------------------------------------------------

        if key == ord("r"):

            if current_features is not None:

                (
                    reference_area,
                    reference_aspect,
                    reference_rectangularity
                ) = current_features


                print("\n===== REFERENCE SET =====")

                print(
                    "Area:",
                    int(reference_area)
                )

                print(
                    "Aspect Ratio:",
                    round(reference_aspect, 2)
                )

                print(
                    "Rectangularity:",
                    round(
                        reference_rectangularity,
                        2
                    )
                )


        # --------------------------------------------------------
        # Nhấn Q -> thoát
        # --------------------------------------------------------

        elif key == ord("q"):

            break


# ============================================================
# 17. GIẢI PHÓNG CAMERA
# ============================================================

finally:

    cap.release()

    cv2.destroyAllWindows()
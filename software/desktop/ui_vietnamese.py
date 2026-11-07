"""Display translations only; machine status codes remain unchanged."""
STATES = {
    "READY": "SẴN SÀNG LƯU ẢNH", "MOVING": "CHƯA ỔN ĐỊNH",
    "NO_COVER": "CHƯA TÌM THẤY BÌA", "MULTIPLE_COVERS": "CÓ NHIỀU BÌA TRONG KHUNG",
    "TOUCHING_FRAME": "BÌA CHẠM MÉP KHUNG HÌNH", "QUALITY_WARNING": "CẦN KIỂM TRA CHẤT LƯỢNG ẢNH",
    "EMPTY_FRAME": "CHƯA CÓ ẢNH", "STARTING_CAMERA": "ĐANG MỞ CAMERA",
    "WAITING_FOR_ANALYSIS": "ĐANG CHỜ PHÂN TÍCH", "WAITING_FOR_FRESH_FRAME": "ĐANG CHỜ ẢNH MỚI",
    "PROCESSING_ERROR": "LỖI XỬ LÝ ẢNH", "PICK_4_OUTER_CORNERS": "CHỌN 4 GÓC NGOÀI BÌA",
    "LIVE": "TRỰC TIẾP", "IMAGE_INPUT": "ẢNH TỪ TỆP", "CLOSED": "ĐÃ ĐÓNG CAMERA",
    "READ_FAILED_RECONNECTING": "MẤT ẢNH, ĐANG KẾT NỐI LẠI",
    "CAMERA_UNAVAILABLE_CLOSE_OTHER_APPS_CHECK_INDEX_AND_PRIVACY": "KHÔNG MỞ ĐƯỢC CAMERA",
    "CAMERA_DRIVER_ERROR_SEE_LOG": "LỖI DRIVER CAMERA, XEM NHẬT KÝ",
}
QR_STATES = {
    "VALID_FORMAT": "Đúng định dạng", "UNREADABLE": "Chưa đọc được",
    "INVALID_FORMAT": "Sai định dạng mã", "INVALID_NAMESPACE": "Không thuộc chuẩn PBL5/LIB1",
    "AMBIGUOUS": "Có nhiều mã QR", "PENDING": "Đang chờ đọc", "DECODE_ERROR": "Lỗi giải mã",
}
ISSUES = {
    "FOCUS_UNVERIFIED": "Chưa đủ chi tiết để xác minh độ nét",
    "BLURRY": "Ảnh có dấu hiệu mờ", "BAD_LIGHT": "Ánh sáng chưa đạt",
    "TOO_SMALL": "Bìa quá nhỏ trong ảnh", "BAD_ASPECT": "Tỷ lệ bìa chưa phù hợp A6",
}
SAVE_ERRORS = {
    "No cover crop: cannot save": "Chưa có ảnh bìa đã cắt để lưu. Đặt bìa vào khung hoặc chọn góc bằng M.",
    "Not READY; improve image/QR or use D to save a review sample": "Chưa đủ điều kiện lưu: kiểm tra ảnh và QR; D lưu riêng để xem lại.",
    "Stale frame: capture a new frame": "Ảnh đã cũ. Chờ camera nhận ảnh mới rồi bấm lưu lại.",
    "This frame was already saved; capture a new frame": "Ảnh này đã lưu. Chờ khung mới để tránh lưu trùng.",
}


def state_label(code):
    if code.startswith("QR_"):
        return "QR: " + qr_label(code[3:])
    if code.startswith("OPENING_"):
        return "ĐANG MỞ CAMERA"
    return STATES.get(code, "TRẠNG THÁI CHƯA XÁC ĐỊNH")


def qr_label(code):
    return QR_STATES.get(code, "Cần kiểm tra mã QR")


def issue_label(code):
    return ISSUES.get(code, "Lỗi phân tích; xem runtime.log để biết chi tiết")


def save_error_label(error):
    return SAVE_ERRORS.get(str(error), "Không lưu được ảnh. Kiểm tra thư mục, dung lượng và runtime.log.")

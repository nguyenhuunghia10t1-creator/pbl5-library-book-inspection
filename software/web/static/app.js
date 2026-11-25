const byId = (id) => document.getElementById(id);
const modes = {
  "hardware-manual": "Cơ khí thủ công",
  hardware: "AI hiệu chuẩn",
  simulation: "Mô phỏng",
};
const states = {
  OFF: "Đã dừng", RUN: "Đang cấp sách", WAIT_AI: "Chờ quyết định", PUSH: "Đang gạt",
  RETRACT: "Đang thu tay gạt", SETTLE: "Chờ IR ổn định", RELEASE: "Cho sách đi tiếp",
  FAULT: "Đã dừng do lỗi",
};
const reasons = {
  STARTUP: "Nhấn nút vật lý khi sẵn sàng.",
  MANUAL_OFF: "Đã dừng bằng nút vật lý.",
  CLEAR_STATION: "Dọn trống vùng IR trước khi chạy.",
  PC_NOT_READY: "Kiểm tra trạng thái sẵn sàng của PC.",
  LINK_LOST: "Kiểm tra USB, nguồn bộ điều khiển băng tải và cổng COM.",
  BOOK_MOVED: "Sách rời IR trước khi có quyết định. Kiểm tra vị trí dừng.",
  RETURN_WAIT: "Chờ tay gạt thu về.",
  NG_NOT_CLEAR: "Hết thời gian chờ sau gạt, IR chưa trống ổn định. Kiểm tra sách và tay gạt.",
  RELEASE_JAM: "Sách OK chưa rời vùng IR đúng hạn. Kiểm tra băng tải.",
  INSPECTION_HOLD: "Đã dừng để kiểm tra sách.",
  AI_TIMEOUT: "Quá hạn quyết định. Kiểm tra ảnh và vùng IR.",
  JOB_LIMIT: "Bộ điều khiển đã đạt giới hạn số lượt.",
  SERVICE_STOPPED: "Dịch vụ trạm đã dừng.",
  "Đang kết nối": "Đang kết nối với ESP32.",
  "Đang kết nối USB": "Đang kết nối với ESP32 qua USB.",
  "Đang tải model": "Đang tải mô hình.",
  MODEL_CLASS_MAPPING: "Nhãn của mô hình không khớp cấu hình OK/NG.",
  MODEL_NO_PROBABILITIES: "Mô hình không trả về độ tin cậy.",
  MODEL_BAD_PROBABILITY: "Độ tin cậy của mô hình không hợp lệ.",
  JPEG_ENCODE: "Không tạo được ảnh JPEG.",
};
const diagnostics = {
  EMPTY_FRAME: ["Khung hình trống hoặc quá nhỏ.", "Kiểm tra nguồn hình và độ phân giải của camera."],
  BLURRY: ["Ảnh bìa bị mờ.", "Chỉnh lấy nét và cố định camera để tránh rung."],
  BAD_LIGHT: ["Độ sáng ảnh nằm ngoài khoảng cho phép.", "Chỉnh ánh sáng và tránh lóa trên bìa."],
  NO_COVER: ["Không tìm thấy bìa sách.", "Đặt một cuốn sách vào giữa khung hình và kiểm tra độ tương phản."],
  MULTIPLE_COVERS: ["Phát hiện nhiều bìa sách.", "Chỉ để một cuốn trong khung hình."],
  TOUCHING_FRAME: ["Bìa sách chạm mép khung hình.", "Đưa cả bìa vào trong khung hình."],
  TOO_SMALL: ["Bìa sách quá nhỏ trong khung hình.", "Đưa camera lại gần hoặc dùng ảnh có độ phân giải cao hơn."],
  BAD_ASPECT: ["Tỉ lệ bìa nằm ngoài khoảng cho phép.", "Chỉnh góc camera sao cho nhìn thấy đủ bốn mép bìa."],
  MOVING: ["Bìa sách chưa ổn định.", "Chờ băng tải và sách dừng hẳn."],
  FRAME_STALE: ["Chưa nhận được khung hình mới.", "Kết nối lại camera và xem ảnh trực tiếp có thay đổi không."],
  FRAME_FROZEN: ["Hình ảnh camera bị đứng.", "Đưa tay qua camera và xem ảnh trực tiếp có thay đổi không."],
  FRAME_SIZE_CHANGED: ["Độ phân giải camera đã thay đổi từ khi lưu ảnh nền.", "Khôi phục độ phân giải và chụp lại băng tải trống."],
  CAMERA_SESSION: ["Kết nối camera thay đổi trong lúc kiểm tra.", "Kết nối lại camera rồi thử lại."],
  COVER_MOVING: ["Bìa sách chưa ổn định.", "Chờ băng tải và sách dừng hẳn."],
  WEAK_FOREGROUND: ["Chưa tách được bìa sách khỏi nền băng tải.", "Chỉnh ánh sáng rồi chụp lại ảnh băng tải trống."],
  MODEL_ERROR: ["Mô hình không phân loại được ảnh.", "Kiểm tra tệp trọng số và cấu hình nhãn."],
  INSPECTION_EXPIRED: ["Lượt kiểm tra quá hạn hoặc đã bị hủy.", "Kiểm tra thời gian nhận ảnh, độ ổn định của bìa và tốc độ suy luận."],
  INSPECTION_ERROR: ["Gặp lỗi khi kiểm tra bìa.", "Kiểm tra ảnh đầu vào và mô hình trước khi chạy lại."],
  INSPECTION_HOLD: ["Đã tạm giữ sách để kiểm tra.", "Xem lại sách trước khi khởi động lại."],
  MANUAL_TIMEOUT: ["Đã hết thời gian chọn kết quả.", "Chọn kết quả cho lượt tiếp theo trước khi hết giờ."],
  LOW_CONFIDENCE: ["Độ tin cậy nằm dưới ngưỡng đã đặt.", "Dùng sách đã biết nhãn để kiểm tra lại mô hình và ngưỡng."],
  UNCALIBRATED: ["Chưa có bộ ngưỡng được xác nhận.", "Dùng sách đã biết nhãn để kiểm tra ngưỡng."],
};
const uiJobs = {
  WAIT_AI: "Đang chờ", DECIDED: "Đã nhận lệnh", COMPLETE: "Hoàn tất",
  UNCONFIRMED: "Chưa xác nhận", HOLD: "Tạm giữ", FAULT: "Dừng lỗi",
};
const settingsLabels = {
  min_sharpness: "Độ sắc nét tối thiểu",
  min_brightness: "Độ sáng tối thiểu",
  max_brightness: "Độ sáng tối đa",
  min_source_short_edge: "Cạnh ngắn tối thiểu của bìa",
  min_area_fraction: "Tỉ lệ diện tích bìa tối thiểu trong ảnh",
  max_area_fraction: "Tỉ lệ diện tích bìa tối đa trong ảnh",
  aspect_tolerance: "Sai lệch tỉ lệ bìa cho phép",
  background_tolerance: "Ngưỡng chênh lệch với nền",
  stable_frames: "Số khung hình ổn định",
  stable_motion_pixels: "Dịch chuyển tối đa của góc bìa",
  min_foreground_fraction: "Tỉ lệ tối thiểu của bìa tách khỏi nền",
  frame_age_s: "Tuổi tối đa của khung hình",
  frozen_s: "Thời gian phát hiện hình bị đứng",
  stabilize_s: "Chờ ổn định trước khi chụp",
  inspection_s: "Thời hạn kiểm tra",
  uncertain_policy: "Khi điểm dưới ngưỡng",
  min_confidence: "Độ tin cậy tối thiểu",
  "min_confidence.OK": "Độ tin cậy tối thiểu cho OK",
  "min_confidence.NG": "Độ tin cậy tối thiểu cho NG",
};
const policies = { hold: "Tạm giữ sách", strict_ng: "Xếp NG nếu ảnh hợp lệ" };
const settingUnits = {
  "Laplacian variance": "phương sai Laplace", "gray level": "mức xám",
  fraction: "tỉ lệ từ 0 đến 1", frames: "khung hình", px: "điểm ảnh",
  s: "giây", probability: "độ tin cậy từ 0 đến 1",
};
const diagnosticUnits = {
  FRAME_STALE: "giây", FRAME_FROZEN: "giây", INSPECTION_EXPIRED: "giây", MANUAL_TIMEOUT: "giây",
  LOW_CONFIDENCE: "%", UNCALIBRATED: "%", WEAK_FOREGROUND: "%", BAD_ASPECT: "%",
  TOO_SMALL: "điểm ảnh", BLURRY: "phương sai Laplace", BAD_LIGHT: "mức xám (0–255)",
  COVER_MOVING: "khung hình",
};
const verdicts = { OK: "OK", NG: "NG", HOLD: "Tạm giữ" };
const runPolicies = { ...modes, direct: "AI trực tiếp", calibrated: "AI hiệu chuẩn" };
const labels = { ...verdicts, Manual: "Người vận hành", "Image file": "Ảnh đã tải" };
const testLabels = { ...verdicts, wrong_ok: "Xếp nhầm vào OK", wrong_ng: "Xếp nhầm vào NG" };
const calibrationIssues = {
  CALIBRATION_INPUTS: [
    "Dữ liệu đầu vào để hiệu chuẩn thiếu, không hợp lệ hoặc đã thay đổi.",
    "Có thể dùng chế độ thủ công. Khi phân loại tự động, hãy nạp mô hình tương thích, chụp băng tải trống và kiểm tra lại bằng tập sách độc lập.",
  ],
  CALIBRATION_COVERAGE: [
    "Thiếu mẫu hiệu chuẩn được mô hình dự đoán đúng.",
    "Lấy lại mẫu với mô hình, góc chụp và ảnh nền hiện tại. Có thể dùng chế độ thủ công để thử băng tải.",
  ],
  TEST_COVERAGE: [
    "Tập kiểm tra độc lập cần cả sách OK và NG.",
    "Dùng các cuốn khác nhau giữa hai tập. Có thể dùng chế độ thủ công để thử băng tải.",
  ],
  REFERENCE_ERROR: [
    "Không kiểm tra được ảnh chuẩn IMG_7.",
    "Khôi phục ảnh chuẩn IMG_7 và kiểm tra mô hình trước khi hiệu chuẩn lại.",
  ],
  KNOWN_BOOK_FAILURE: [
    "Kết quả không đạt khi đối chiếu với sách đã biết nhãn.",
    "Dừng phân loại tự động. Có thể tiếp tục thử băng tải bằng chế độ thủ công. Kiểm tra ánh sáng và khung hình rồi thử lại với tập sách độc lập. Khi sách NG bị xếp vào OK ở độ tin cậy cao, cần sửa mô hình hoặc hiệu chuẩn lại và kiểm tra trên tập độc lập.",
  ],
};
const messages = {
  "Choose OK or NG in manual hardware mode.": "Chọn OK hoặc NG trong chế độ cơ khí thủ công.",
  "This capture is no longer accepting a decision.": "Lượt này đã hết thời gian nhận quyết định.",
  "Image files are only available in simulation.": "Chỉ dùng tệp ảnh trong chế độ mô phỏng.",
  "Wait for the current simulated capture before changing its source.": "Chờ lượt mô phỏng kết thúc trước khi đổi nguồn ảnh.",
  "This control is only available in simulation.": "Thao tác này chỉ dùng được trong chế độ mô phỏng.",
  "Vision settings are available in automatic mode and simulation.": "Chỉ chỉnh thông số hình ảnh trong chế độ tự động và mô phỏng.",
  "Wait for the current vision operation to finish.": "Chờ thao tác xử lý ảnh đang chạy kết thúc.",
  "Calibration requires the station camera.": "Cần camera của trạm để hiệu chuẩn.",
  "Enter a known book ID, truth, and calibration or test split.": "Nhập mã sách, nhãn thực tế và chọn tập hiệu chuẩn hoặc tập kiểm tra.",
  "Load the model and capture the empty belt first.": "Nạp mô hình và chụp băng tải trống trước.",
  "Vision inputs changed during sampling. Retake this sample.": "Đầu vào xử lý ảnh đã thay đổi. Hãy lấy lại mẫu này.",
  "Choose either reset or new settings.": "Chọn khôi phục mặc định hoặc lưu thông số mới.",
  "Unknown station setting": "Có thông số trạm không hợp lệ.",
  "min_confidence must contain OK and/or NG": "Nhập độ tin cậy tối thiểu cho OK hoặc NG.",
  "uncertain_policy must be hold or strict_ng": "Chọn cách xử lý khi độ tin cậy thấp.",
  "frozen_s must be at least frame_age_s": "Thời gian phát hiện hình bị đứng phải lớn hơn hoặc bằng tuổi tối đa của khung hình.",
  "inspection_s must exceed stabilize_s by at least 0.5 seconds": "Thời hạn kiểm tra phải dài hơn thời gian chờ ổn định ít nhất 0,5 giây.",
  "min_brightness must be less than max_brightness": "Độ sáng tối thiểu phải nhỏ hơn độ sáng tối đa.",
  "min_area_fraction must be less than max_area_fraction": "Tỉ lệ diện tích tối thiểu phải nhỏ hơn tỉ lệ diện tích tối đa.",
  "Select a JPG or PNG cover image.": "Chọn ảnh bìa định dạng JPEG hoặc PNG.",
  "Select an image smaller than 10 MiB.": "Chọn ảnh nhỏ hơn 10 MiB.",
  "Upload a JPEG or PNG no larger than 10 MiB.": "Tải ảnh JPEG hoặc PNG có dung lượng tối đa 10 MiB.",
  "Upload one image with at most 12 megapixels.": "Tải một ảnh có độ phân giải tối đa 12 triệu điểm ảnh.",
  "The file is not a readable JPEG or PNG.": "Không đọc được tệp ảnh JPEG hoặc PNG.",
  "A previous image prediction is still running.": "Mô hình đang phân loại ảnh trước đó.",
  "Operator selected a simulated hold.": "Người vận hành chọn tạm giữ trong mô phỏng.",
  "Inspection requested a hold.": diagnostics.INSPECTION_HOLD[0],
  "Manual decision timed out.": diagnostics.MANUAL_TIMEOUT[0],
  "Waiting for a fresh camera frame": diagnostics.FRAME_STALE[0],
  "Camera is repeating a frozen frame": diagnostics.FRAME_FROZEN[0],
  "Cover has not stabilized": diagnostics.COVER_MOVING[0],
  "Waiting for a stable cover": "Đang chờ bìa sách ổn định.",
  "A full cover could not be isolated": "Chưa tách được toàn bộ bìa sách.",
  "Cover does not separate from the empty belt": diagnostics.WEAK_FOREGROUND[0],
  "Camera resolution changed after baseline capture": diagnostics.FRAME_SIZE_CHANGED[0],
  "Camera session changed during inspection": diagnostics.CAMERA_SESSION[0],
  "Camera session changed during inference": diagnostics.CAMERA_SESSION[0],
  "Inspection expired or was cancelled": diagnostics.INSPECTION_EXPIRED[0],
  "Image prediction timed out.": "Phân loại ảnh đã quá hạn.",
  "Prediction is below the simulation confidence floor.": diagnostics.LOW_CONFIDENCE[0],
  "Model confidence is below the validated threshold": diagnostics.LOW_CONFIDENCE[0],
  "No validated threshold profile": diagnostics.UNCALIBRATED[0],
  "Invalid model confidence": reasons.MODEL_BAD_PROBABILITY,
  "Classification failed": diagnostics.MODEL_ERROR[0],
  "Chưa tìm thấy ESP32 CP210x qua USB. Chọn cổng COM nếu dùng adapter khác.": "Chưa tìm thấy ESP32 CP210x qua USB. Nếu dùng bộ chuyển đổi khác, hãy chọn cổng COM.",
  "Kết quả không khớp yêu cầu CAPTURE": "Kết quả không khớp yêu cầu chụp ảnh.",
  "ID trong CAPTURE không hợp lệ": "Mã lượt chụp không hợp lệ.",
  "Thiếu ACK của ESP32 cho kết quả vừa gửi": "ESP32 chưa xác nhận kết quả vừa gửi.",
  "Thiếu CAPTURE đúng mã sách": "Chưa nhận được yêu cầu chụp đúng mã sách.",
  "CAPTURE không khớp trạng thái ESP32": "Yêu cầu chụp ảnh không khớp trạng thái ESP32.",
  "Bản tin USB hoặc ACK không hợp lệ": "Bản tin USB hoặc phản hồi xác nhận không hợp lệ.",
  "Mất camera khi lấy nền trống": "Mất kết nối camera khi lưu ảnh băng tải trống.",
  "Bad Light": diagnostics.BAD_LIGHT[0],
  "Blurry": diagnostics.BLURRY[0],
  "Too Small": diagnostics.TOO_SMALL[0],
  "Bad Aspect": diagnostics.BAD_ASPECT[0],
  "Not Found": "Không tìm thấy dữ liệu.",
  STARTING_CAMERA: "Đang khởi động camera.",
  READ_FAILED_RECONNECTING: "Mất hình, đang kết nối lại camera.",
  CAMERA_UNAVAILABLE_CLOSE_OTHER_APPS_CHECK_INDEX_AND_PRIVACY: "Không mở được camera. Đóng ứng dụng đang dùng camera và kiểm tra quyền truy cập.",
  CAMERA_DRIVER_ERROR_SEE_LOG: "Trình điều khiển camera gặp lỗi. Xem nhật ký trạm.",
  CLOSED: "Camera đã đóng.",
};
const el = (tag, value) => {
  const node = document.createElement(tag);
  if (value != null) node.textContent = value;
  return node;
};
const number = (value, options = {}) => value.toLocaleString("vi-VN", options);
const percentage = (value) => number(100 * value, { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%";
const verdictText = (verdict) => Object.hasOwn(verdicts, verdict) ? verdicts[verdict] : "";
const labelText = (label) => Object.hasOwn(labels, label) ? labels[label] : label;

function describe(value, fallback = "Trạm báo lỗi. Xem nhật ký để biết chi tiết.") {
  const message = String(value || "");
  if (!message) return "";
  const codes = message.split(", ");
  const translated = codes.map((code) => (
    (Object.hasOwn(reasons, code) && reasons[code])
    || (Object.hasOwn(diagnostics, code) && diagnostics[code][0])
    || (Object.hasOwn(messages, code) && messages[code])
  ));
  if (translated.every(Boolean)) return translated.join(" ");
  const settingRange = /^([a-z_]+) must be between ([\d.]+) and ([\d.]+)$/.exec(message);
  if (settingRange && Object.hasOwn(settingsLabels, settingRange[1])) {
    return settingsLabels[settingRange[1]] + " phải từ " + number(Number(settingRange[2])) + " đến " + number(Number(settingRange[3])) + ".";
  }
  if (message.startsWith("Invalid station settings:")) return "Cài đặt trạm không hợp lệ. Hãy khôi phục mặc định.";
  if (message.startsWith("The image classifier is unavailable.")) return "Không dùng được mô hình phân loại ảnh. Kiểm tra tệp trọng số.";
  const brightness = /^Cover brightness is ([\d.]+) \(required ([\d.]+)–([\d.]+)\)\.$/.exec(message);
  if (brightness) {
    const [measured, low, high] = brightness.slice(1).map((part) => number(Number(part)));
    return "Độ sáng bìa " + measured + " nằm ngoài khoảng " + low + "–" + high + ".";
  }
  const sharpness = /^Cover is blurred or blank \(sharpness ([\d.]+), minimum ([\d.]+)\)\.$/.exec(message);
  if (sharpness) {
    const [measured, minimum] = sharpness.slice(1).map((part) => number(Number(part)));
    return "Ảnh bìa bị mờ hoặc trống. Độ sắc nét " + measured + ", yêu cầu tối thiểu " + minimum + ".";
  }
  const edge = /^Cover is too small \((\d+) px on the short edge\)\.$/.exec(message);
  if (edge) return "Bìa quá nhỏ. Cạnh ngắn dài " + number(Number(edge[1])) + " điểm ảnh.";
  if (/^OPENING_[A-Z]+_CAMERA_\d+$/.test(message)) return "Đang mở camera.";
  if (message.includes("FileNotFoundError") || message.includes("No such file or directory")) {
    return "Không tìm thấy tệp đã cấu hình. Kiểm tra đường dẫn và quyền truy cập.";
  }
  const serialPort = /could not open port ['"]?(COM\d+)/i.exec(message);
  if (serialPort) return "Không mở được cổng " + serialPort[1].toUpperCase() + ". Kiểm tra cổng USB và đóng ứng dụng đang dùng cổng.";
  // Backend messages already in Vietnamese can contain technical names and book IDs.
  return /[đăâêôơưàáảãạèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵ\u1ea0-\u1ef9]/i.test(message) ? message : fallback;
}

function issueText(issue) {
  if (!issue) return { message: "", remedy: "" };
  const code = issue.code;
  const known = Object.hasOwn(diagnostics, code) ? diagnostics[code] : calibrationIssues[code];
  const remedy = known?.[1] || describe(issue.remedy, "");
  if (code === "KNOWN_BOOK_FAILURE" && issue.book) {
    const result = [issue.truth && "nhãn thực tế " + verdictText(issue.truth), issue.label && "dự đoán " + labelText(issue.label),
      issue.confidence != null && "độ tin cậy " + percentage(issue.confidence),
      issue.threshold != null && "ngưỡng " + percentage(issue.threshold), issue.decision && "quyết định " + verdictText(issue.decision)];
    return { message: issue.book + " · " + result.filter(Boolean).join(" · ") + ".", remedy };
  }
  const coverage = /^No correctly predicted (OK|NG) calibration sample\.$/.exec(issue.message || "");
  const message = coverage ? "Thiếu mẫu hiệu chuẩn " + coverage[1] + " được mô hình dự đoán đúng."
    : code === "FRAME_STALE" && issue.message ? describe(issue.message, known[0])
    : known?.[0] || describe(issue.message || code);
  return { message, remedy };
}
const current = { state: null, idle: false, pending: "", manualUntil: 0 };
let lastImage = "", portInitialized = false, settings = null;
let sourceRevision = 0;
let settingsPending = false, uploadPending = false, submittedKey = "", submittedVerdict = "", manualTimer;

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch("/api/" + path, { cache: "no-store", ...options });
  } catch {
    throw Error("Không kết nối được với dịch vụ trạm.");
  }
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = result.detail;
    const fallback = "Trạm không thực hiện được yêu cầu (" + response.status + ").";
    const message = typeof detail === "string" ? describe(detail, fallback)
      : Object.values(issueText(detail)).filter(Boolean).join(" ");
    throw Error(message || fallback);
  }
  return result;
}
async function post(path, data = {}, message = "Đã lưu.", feedback = byId("feedback")) {
  try {
    const result = await request(path, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data),
    });
    feedback.textContent = result.label
      ? [result.book, labelText(result.label), result.confidence == null ? "" : percentage(result.confidence)].filter(Boolean).join(" · ")
      : result.thresholds
        ? ["Đã lưu ngưỡng. Kiểm tra độc lập", ...Object.entries(testLabels)
          .filter(([key]) => result.test?.[key] != null).map(([key, label]) => label + " " + number(result.test[key]))].join(" · ")
        : message;
    return result;
  } catch (err) {
    feedback.textContent = err.message;
    return null;
  }
}
byId("serial-connect").onsubmit = (event) => {
  event.preventDefault();
  if (current.idle) post("connect", Object.fromEntries(new FormData(event.target)), "Đã chọn cổng USB. Chờ phản hồi.");
};
byId("pilot").onsubmit = async (event) => {
  event.preventDefault();
  if (!current.idle || !await post("pilot", Object.fromEntries(new FormData(event.target)))) return;
  if (byId("settings").open) await loadSettings();
  else settings = null;
};
async function refreshCalibration(path, message) {
  if (!current.idle) return;
  await post(path, {}, message, byId("calibrationResult"));
  if (byId("settings").open) await loadSettings();
  else settings = null;
}
byId("threshold").onclick = () => refreshCalibration("thresholds");
byId("background").onclick = () => refreshCalibration("background", "Đã lưu nền băng. Xác nhận lại hiệu chuẩn trước khi chạy.");
byId("reset").onclick = () => { if (current.idle && window.confirm("Mở ca mới và bắt đầu lại bộ đếm?")) post("shift", {}, "Đã mở ca mới."); };

function addActions(container, actions) {
  for (const [cmd, label] of Object.entries(actions)) {
    const button = el("button", label);
    button.type = "button";
    button.onclick = async () => {
      const feedback = byId("simulationFeedback");
      const outcome = ["OK", "NG", "HOLD"].includes(cmd);
      if (uploadPending && (cmd === "insert" || outcome)) {
        feedback.textContent = "Chờ tải ảnh xong trước khi đặt sách hoặc chọn kết quả.";
        return;
      }
      if (cmd === "insert" && byId("simulationFile").files.length) {
        feedback.textContent = "Nhấn Dùng ảnh mô phỏng để dùng tệp đã chọn, hoặc chọn kết quả mô phỏng.";
        return;
      }
      if (await post("sim/" + cmd, {}, label + ".", feedback) && outcome) {
        sourceRevision++;
        renderSimulationSource(null);
        byId("simulationFile").value = "";
        byId("simulationFile").onchange();
      }
    };
    byId(container).append(button);
  }
}
addActions("actions", { button: "Nhấn nút trạm", insert: "Đặt sách", remove: "Lấy sách ra" });
addActions("demoActions", { OK: "Chọn OK", NG: "Chọn NG", HOLD: "Tạm giữ sách" });
addActions("faultActions", { link: "Đổi kết nối ESP32", camera: "Đổi trạng thái camera", ai: "Đổi trạng thái lỗi AI" });

function setManualButtons() {
  const canRespond = current.pending && current.pending !== submittedKey && current.manualUntil > performance.now();
  for (const id of ["manualOK", "manualNG"]) byId(id).disabled = !canRespond;
}
async function sendManual(verdict) {
  const key = current.pending;
  if (!key || key === submittedKey || current.manualUntil <= performance.now()) return;
  submittedKey = key;
  submittedVerdict = "";
  byId("manualPrompt").textContent = "Lượt " + key.split("-").pop() + " · Đang gửi " + verdictText(verdict);
  setManualButtons();
  const accepted = await post("manual/decision", { key, verdict }, "Đã gửi quyết định cho lượt " + key.split("-").pop() + ".");
  if (accepted && submittedKey === key) submittedVerdict = verdict;
  if (accepted && current.state?.board?.capture_id === key && current.state?.board?.phase === "WAIT_AI"
      && current.state?.manual_decision?.state !== "acknowledged") {
    byId("manualPrompt").textContent = "Lượt " + key.split("-").pop() + " · Đã gửi " + verdictText(verdict) + " · chờ ESP32 xác nhận.";
  } else if (!accepted && submittedKey === key) {
    submittedKey = "";
    setManualButtons();
  }
}
byId("manualOK").onclick = () => sendManual("OK");
byId("manualNG").onclick = () => sendManual("NG");

byId("simulationFile").onchange = () => {
  const file = byId("simulationFile").files[0];
  byId("uploadImage").disabled = !file || uploadPending;
  byId("simulationImageResult").textContent = file ? file.name + " đã chọn. Hãy tải ảnh trước khi đặt sách." : "";
};
byId("simulationInput").onsubmit = async (event) => {
  event.preventDefault();
  const file = byId("simulationFile").files[0];
  if (!file || uploadPending) return;
  const type = file.type || (/\.png$/i.test(file.name) ? "image/png" : "image/jpeg");
  if (!["image/jpeg", "image/png"].includes(type)) {
    byId("simulationImageResult").textContent = "Chọn ảnh JPEG hoặc PNG.";
    return;
  }
  const selectedFile = byId("simulationFile");
  uploadPending = true;
  selectedFile.disabled = true;
  byId("uploadImage").disabled = true;
  byId("simulationImageResult").textContent = "Đang tải " + file.name + "...";
  try {
    const accepted = await request("sim/image", { method: "POST", headers: { "Content-Type": type }, body: file });
    selectedFile.value = "";
    sourceRevision++;
    renderSimulationSource(accepted.simulation_image_version);
    byId("simulationImageResult").textContent = file.name + " đã tải. Chạy mô phỏng và đặt sách để kiểm tra.";
  } catch (err) {
    byId("simulationImageResult").textContent = err.message;
  } finally {
    uploadPending = false;
    selectedFile.disabled = false;
    byId("uploadImage").disabled = !selectedFile.files.length;
  }
};

function rowFor(key, value) {
  const row = el("div");
  row.append(el("dt", key), el("dd", value));
  return row;
}
function diagnosticValue(value, code) {
  const unit = diagnosticUnits[code];
  const format = (n) => typeof n === "number" ? number(n, { maximumFractionDigits: 2 }) : String(n);
  if (Array.isArray(value)) {
    if (code === "FRAME_SIZE_CHANGED") return value.map(format).join(" × ") + " điểm ảnh (cao × rộng)";
    return value.map(format).join("–") + (unit ? " " + unit : "");
  }
  if (unit === "%" && typeof value === "number") return percentage(value);
  return format(value) + (unit ? " " + unit : "");
}
function renderStop(issue, stop) {
  const panel = byId("stopDiagnostic");
  panel.hidden = !stop && !issue;
  if (panel.hidden) return;
  byId("stopHeading").textContent = stop ? "Lần dừng gần nhất" : "Chẩn đoán";
  const reason = typeof stop === "string" ? stop : stop?.reason;
  const detail = issueText(issue);
  byId("stopMessage").textContent = [...new Set([describe(reason), detail.message].filter(Boolean))].join(" ");
  byId("stopHelp").textContent = detail.remedy;
  byId("stopMeta").textContent = [stop?.occurred_at && new Date(stop.occurred_at).toLocaleString("vi-VN", { timeZone:"Asia/Ho_Chi_Minh" }), stop?.job_id && "Lượt " + stop.job_id.split("-").pop()].filter(Boolean).join(" · ");
  const metrics = byId("stopMetrics");
  metrics.replaceChildren();
  for (const [key, values] of Object.entries({ "Đo được": issue?.measured, "Giới hạn": issue?.limit })) {
    if (typeof values === "number" || (Array.isArray(values) && values.length)) {
      metrics.append(rowFor(key, diagnosticValue(values, issue.code)));
    }
  }
}

function fieldInfo(schema, key, child) {
  const entry = schema.limits[key] || {};
  return child ? entry[child] || schema.limits[key + "." + child] || entry : entry;
}
function settingsField(key, child, value, defaultValue) {
  const path = child ? key + "." + child : key;
  const info = fieldInfo(settings, key, child);
  const label = el("label", settingsLabels[path] || "Thông số khác");
  const control = Array.isArray(info.choices) ? el("select") : el("input");
  if (Array.isArray(info.choices)) {
    for (const choice of info.choices) {
      const option = el("option", policies[choice] || "Tùy chọn khác");
      option.value = choice;
      control.append(option);
    }
  } else {
    control.type = "number";
    control.step = info.integer ? "1" : "any";
    if (info.minimum != null) control.min = info.minimum;
    if (info.maximum != null) control.max = info.maximum;
    control.required = true;
  }
  control.name = path;
  control.value = value;
  const displayDefault = typeof defaultValue === "number" ? number(defaultValue) : policies[defaultValue];
  label.append(control, el("small", [displayDefault != null && "Mặc định " + displayDefault, settingUnits[info.unit], describe(info.help, "")].filter(Boolean).join(" · ")));
  return label;
}
function renderSettings() {
  const elements = [];
  const advanced = el("details");
  advanced.append(el("summary", "Thông số kỹ thuật"));
  for (const [key, value] of Object.entries(settings.values)) {
    if (current.state?.direct_routing && key !== "stabilize_s") continue;
    if (value && typeof value === "object") {
      for (const [child, nested] of Object.entries(value)) {
        elements.push(settingsField(key, child, nested, settings.defaults[key]?.[child]));
      }
    } else {
      const field = settingsField(key, "", value, settings.defaults[key]);
      if (["stabilize_s", "uncertain_policy"].includes(key)) elements.push(field);
      else advanced.append(field);
    }
  }
  if (!current.state?.direct_routing) elements.push(advanced);
  byId("settingsInputs").replaceChildren(...elements);
  const calibration = settings.calibration;
  const detail = issueText(calibration?.error);
  byId("settingsInfo").textContent = calibration?.valid
    ? "Hồ sơ hiệu chuẩn hợp lệ. Khi đổi thông số, cần xác nhận lại."
    : [detail.message || "Hồ sơ hiện tại cần hiệu chuẩn.", detail.remedy].filter(Boolean).join(" ");
  if (current.state?.direct_routing) byId("settingsInfo").textContent = "Thời gian ổn định chỉ áp dụng cho AI trực tiếp.";
  setIdleControls();
}
async function loadSettings() {
  try {
    settings = await request("settings");
    renderSettings();
  } catch (err) {
    byId("settingsFeedback").textContent = err.message;
  }
}
byId("settings").ontoggle = () => {
  if (byId("settings").open && !settings && current.state?.mode !== "hardware-manual") loadSettings();
};
async function saveSettings(reset = false) {
  if (!settings || settingsPending || !current.idle) return;
  const values = {};
  if (!reset) {
    for (const field of byId("settingsInputs").querySelectorAll("input, select")) {
      const [key, child] = field.name.split(".");
      const value = field.type === "number" ? field.valueAsNumber : field.value;
      if (child) (values[key] ||= {})[child] = value;
      else values[key] = value;
    }
  }
  settingsPending = true;
  setIdleControls();
  try {
    await request("settings", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ values, reset }),
    });
    await loadSettings();
    byId("settingsFeedback").textContent = reset ? "Đã khôi phục mặc định." : "Đã lưu cài đặt.";
  } catch (err) {
    byId("settingsFeedback").textContent = err.message;
  } finally {
    settingsPending = false;
    setIdleControls();
  }
}
byId("settingsForm").onsubmit = (event) => { event.preventDefault(); saveSettings(); };
byId("settingsReset").onclick = () => {
  if (current.idle && window.confirm("Khôi phục cài đặt mặc định của chế độ này?")) saveSettings(true);
};

function setIdleControls() {
  for (const id of ["serial-connect", "pilot"]) {
    for (const control of byId(id).elements) control.disabled = !current.idle;
  }
  byId("reset").disabled = !current.idle;
  const disabled = !settings || !current.idle || settingsPending;
  for (const id of ["settingsFields", "settingsSave", "settingsReset"]) byId(id).disabled = disabled;
}

let pinnedJob = null, historyShift = null, historySignature = "";
function showJob(job) {
  const imageKey = job?.has_image ? job.id : "";
  if (imageKey !== lastImage) {
    lastImage = imageKey;
    const img = byId("decisionImage");
    img.hidden = true;
    img.removeAttribute("src");
    if (imageKey) {
      const fresh = el("img");
      fresh.id = "decisionImage";
      fresh.hidden = true;
      fresh.alt = "Ảnh dùng để phân loại";
      fresh.onload = () => { if (lastImage === imageKey) fresh.hidden = false; };
      img.replaceWith(fresh);
      fresh.src = "/api/jobs/" + encodeURIComponent(imageKey) + "/image";
    }
  }
  byId("follow").hidden = !pinnedJob;
  byId("detailHeading").textContent = (pinnedJob ? "Đang xem" : "Lượt mới nhất") + (job ? " · #" + job.id.split("-").pop() : "");
  byId("decisionText").textContent = job ? (verdictText(job.verdict) || (["WAIT_AI","DECIDED"].includes(job.status) ? "Chờ quyết định" : "Chưa có quyết định")) : "Chưa có lượt";
  byId("decisionText").className = (job?.verdict || "").toLowerCase();
  byId("detail").textContent = job ? [labelText(job.label), job.confidence != null && percentage(job.confidence),
    uiJobs[job.status], describe(job.reason), job.stop_reason !== job.reason && describe(job.stop_reason),
    runPolicies[job.policy], job.inference_ms != null && number(Math.round(job.inference_ms)) + " ms",
    !imageKey && "Chưa có ảnh dùng để phân loại"].filter(Boolean).join(" · ") : "";
}
function renderJobs(jobs) {
  if (historyShift !== current.state.shift_id) pinnedJob = null;
  historyShift = current.state.shift_id;
  if (pinnedJob) pinnedJob = jobs.find(j => j.id === pinnedJob.id) || pinnedJob;
  showJob(pinnedJob || jobs[0]);
  const signature = JSON.stringify([jobs, pinnedJob?.id]);
  if (signature === historySignature) return;
  historySignature = signature;
  const list = byId("jobs");
  list.replaceChildren();
  if (!jobs.length) list.textContent = "Chưa có lượt trong ca";
  for (const job of jobs) {
    const row = el("button");
    row.className = "job" + (job.id === pinnedJob?.id ? " selected" : "");
    const time = new Date(job.created).toLocaleTimeString("vi-VN", {timeZone:"Asia/Ho_Chi_Minh", hour12:false});
    const verdict = el("span", verdictText(job.verdict) || "—");
    if (verdictText(job.verdict)) verdict.className = "verdict-" + job.verdict.toLowerCase();
    row.append(el("span", time), verdict, el("span", job.confidence == null ? "—" : percentage(job.confidence)),
      el("span", uiJobs[job.status] || "Chưa xác định"));
    row.onclick = async () => {
      pinnedJob = job;
      renderJobs(current.state.jobs || []);
      try {
        const detail = await request("jobs/" + encodeURIComponent(job.id));
        if (pinnedJob?.id === detail.id) { pinnedJob = detail; showJob(detail); }
      } catch { /* Keep the snapshot from the status response. */ }
    };
    list.append(row);
  }
}
byId("follow").onclick = () => { pinnedJob = null; renderJobs(current.state.jobs || []); };
function openDrawer(id) {
  byId("drawer").showModal();
  const target = byId(id);
  target.open = true;
  target.scrollIntoView({block:"nearest"});
}
byId("switch").onclick = () => openDrawer("modeMenu");
byId("configure").onclick = () => openDrawer("settings");
byId("connection").onclick = () => openDrawer("setup");
byId("cameraBadge").onclick = () => byId("retry").click();
byId("closeDrawer").onclick = () => byId("drawer").close();
byId("retry").onclick = () => { byId("preview").removeAttribute("src"); byId("preview").src = "/api/live.mjpg?t=" + Date.now(); };
byId("tabs").onclick = () => { byId("tabs").textContent = document.body.classList.toggle("historyTab") ? "Vận hành" : "Lịch sử"; };

function renderSimulationSource(version) {
  const oldImage = byId("simulationPreview");
  const empty = byId("empty");
  byId("simulationSource").textContent = version
    ? "Nguồn quyết định · AI chạy trên ảnh đã tải. Chọn OK, NG hoặc Tạm giữ sách để tự chọn kết quả."
    : "Nguồn quyết định · Kết quả mô phỏng do người dùng chọn.";
  if (!version) {
    oldImage.removeAttribute("src");
    oldImage.hidden = true;
    empty.textContent = "Chọn ảnh hoặc chọn kết quả mô phỏng.";
    empty.hidden = false;
    return;
  }
  const path = "/api/sim/image?version=" + encodeURIComponent(version);
  if (oldImage.getAttribute("src") === path) return;
  const img = el("img");
  img.id = "simulationPreview";
  img.alt = "Ảnh dùng để kiểm tra mô phỏng";
  img.hidden = true;
  oldImage.replaceWith(img);
  empty.hidden = false;
  empty.textContent = "Đang nạp ảnh mô phỏng.";
  img.onload = () => {
    if (byId("simulationPreview") !== img || img.getAttribute("src") !== path) return;
    img.hidden = false;
    empty.hidden = true;
  };
  img.onerror = () => {
    if (byId("simulationPreview") !== img || img.getAttribute("src") !== path) return;
    img.hidden = true;
    empty.hidden = false;
    empty.textContent = "Chưa xem được ảnh. Kiểm tra nguồn mô phỏng đang chọn.";
    img.removeAttribute("src");
  };
  img.src = path;
}

function render(s, statusRevision = sourceRevision) {
  if (current.state && current.state.mode !== s.mode) {
    settings = null;
    byId("settings").open = false;
    submittedKey = submittedVerdict = "";
    byId("simulationPreview").removeAttribute("src");
    byId("simulationPreview").hidden = true;
    byId("calibrationResult").textContent = "";
  }
  current.state = s;
  const mode = s.direct_routing ? "AI trực tiếp" : modes[s.mode] || "Trạm phân loại";
  byId("modeGuideActive").textContent = "Đang dùng · " + mode;
  const sim = s.mode === "simulation", manual = s.mode === "hardware-manual";
  const board = s.board || {}, connected = !!board.phase;
  current.idle = Boolean(s.idle ?? ((!connected || ["OFF", "FAULT"].includes(board.phase)) && !s.busy));
  byId("mode").textContent = s.direct_routing ? mode + " · OK đi tiếp / NG gạt ra" : mode;
  byId("simulation").hidden = !sim;
  byId("simulationInput").hidden = !sim;
  byId("inputPanel").hidden = manual;
  byId("inputHeading").textContent = sim ? "Ảnh mô phỏng" : "Camera trực tiếp";
  byId("manualDecision").hidden = !manual;
  byId("setup").hidden = sim;
  byId("pilot").hidden = manual || s.direct_routing === true;
  byId("settings").hidden = manual;
  byId("configure").onclick = () => openDrawer(manual ? "setup" : "settings");
  byId("settingsInfo").hidden = manual;
  byId("settingsForm").hidden = manual;
  byId("simulationSettingsNote").hidden = !sim;
  setIdleControls();
  if (!sim && !portInitialized) {
    const port = byId("serial-connect").elements.port;
    if (!port.value) port.value = s.port || "";
    portInitialized = true;
  }
  byId("cameraBadge").hidden = manual || sim;
  byId("cameraBadge").textContent = s.camera ? "Camera · mất hình" : "Camera · có hình";
  byId("retry").hidden = manual || sim;
  byId("connection").disabled = sim;
  byId("connection").textContent = sim ? "Mô phỏng" : (s.connected_port || s.bridge?.port || "USB") + " · " + (connected ? "Đã kết nối" : "Chờ bộ điều khiển");
  const radio = { RADIO_READY: "Đã sẵn sàng", RADIO_ERROR: "Lỗi kết nối không dây" };
  byId("connection").title = s.bridge
    ? "Bộ chuyển tiếp · " + (radio[s.bridge.radio] || "Chưa rõ trạng thái") + " · xác nhận " + number(Math.round(s.bridge.age_s)) + " giây trước"
    : "Chưa xác nhận bộ chuyển tiếp";
  byId("cameraBadge").className = s.camera ? "ng" : "ok";
  byId("connection").className = sim ? "" : connected ? "ok" : "ng";
  byId("actionStrip").className = board.phase === "FAULT" || (!connected && !sim) ? "alert" : "";
  byId("stationHeading").textContent = states[board.phase] || "Chờ dữ liệu";
  byId("warning").textContent = [s.health && "Kiểm tra thiết bị trong Cài đặt", s.link_error && "Kiểm tra USB và bộ điều khiển băng tải", describe(board.reason)].filter(Boolean).join(" · ");
  byId("deviceDiagnostic").textContent = [describe(s.health), describe(s.link_error, "Không nhận được phản hồi qua USB. Kiểm tra cổng và nguồn bộ điều khiển."), byId("connection").title].filter(Boolean).join(" · ");
  const stop = s.last_stop;
  // Older saved stops contain unscoped diagnostics from previous books.
  renderStop(stop ? stop.diagnostic : s.diagnostics?.camera || s.diagnostics?.inspection, stop);

  const remain = Number(s.manual_remaining_s || 0);
  if (manual && board.phase === "WAIT_AI" && typeof document.body?.classList?.remove === "function") {
    document.body.classList.remove("historyTab");
    byId("tabs").textContent = "Lịch sử";
  }
  const capture = board.capture_id;
  const decision = manual ? s.manual_decision : null;
  current.pending = manual && board.phase === "WAIT_AI" && capture && !decision && remain > 0 ? capture : "";
  current.manualUntil = performance.now() + Math.max(0, remain) * 1000;
  clearTimeout(manualTimer);
  if (current.pending) manualTimer = setTimeout(setManualButtons, Math.ceil(remain * 1000));
  if (manual) {
    let prompt = "Chờ sách dừng tại IR.";
    if (!connected) prompt = "Chờ ESP32. Kiểm tra kết nối USB.";
    else if (decision?.state === "acknowledged") {
      prompt = "Lượt " + decision.key.split("-").pop() + " · ESP32 đã nhận " + verdictText(decision.verdict) + ".";
    } else if (decision?.state === "queued") {
      prompt = "Lượt " + decision.key.split("-").pop() + " · Đã gửi " + verdictText(decision.verdict) + " · chờ ESP32 xác nhận.";
    } else if (board.phase === "WAIT_AI") {
      if (capture && submittedKey === capture) {
        prompt = "Lượt " + capture.split("-").pop() + " · " + (submittedVerdict ? "Đã gửi " + verdictText(submittedVerdict) + " · chờ ESP32 xác nhận." : "Đang gửi quyết định.");
      } else if (current.pending) prompt = "Lượt " + capture.split("-").pop() + " · " + number(remain, { maximumFractionDigits: 1, minimumFractionDigits: 1 }) + " giây còn lại";
      else prompt = "Lượt " + board.job + " · Chờ phản hồi từ trạm.";
    } else if (board.phase === "FAULT" || (board.phase === "OFF" && board.reason === "MANUAL_OFF")) {
      prompt = describe(board.reason);
    } else if (board.phase === "RUN") {
      const completed = (s.jobs || []).find((job) => job.id === submittedKey && job.status === "COMPLETE" && job.verdict);
      if (completed) prompt = "ESP32 đã nhận " + verdictText(completed.verdict) + " · chờ sách tiếp theo.";
    }
    byId("manualPrompt").textContent = prompt;
  }
  setManualButtons();

  const display = connected ? board : s.last_board || {};
  byId("machine").replaceChildren(...Object.entries({
    "Chu kỳ": manual && board.phase === "WAIT_AI" ? (decision ? "Chờ ESP32" : "Chờ người vận hành") : states[display.phase] || "—",
    "Cảm biến IR": display.phase ? (display.ir ? "Có sách" : "Trống") : "—",
    "PWM băng tải": display.phase ? Math.round((display.pwm / 1023) * 100) + "%" : "—",
    "Lệnh servo": display.phase ? display.servo + "°" : "—",
  }).map(([key, value]) => rowFor(key, value)));
  if (!connected && s.board_age_s != null) byId("machine").append(rowFor("Dữ liệu cũ", number(s.board_age_s, { maximumFractionDigits: 1 }) + " giây"));
  byId("counters").replaceChildren(...Object.entries({ "Đã quyết định": s.counts.total, OK: s.counts.ok, NG: s.counts.ng, "% OK": s.counts.total ? percentage(s.counts.ok / s.counts.total) : "—" }).map(([label, value]) => {
    const box = el("div");
    box.append(el("small", label), el("b", value));
    return box;
  }));
  renderJobs(s.jobs || [], sim, manual);
  if (sim) {
    if (statusRevision === sourceRevision) renderSimulationSource(s.simulation_image_version);
  } else {
    byId("simulationPreview").hidden = true;
    byId("empty").textContent = s.camera ? "Chưa có hình từ camera" : "Chờ hình trực tiếp";
  }
  return s.mode === "hardware" && !s.camera;
}
byId("preview").onerror = hidePreview;
function hidePreview() {
  if (byId("preview").getAttribute("src")) byId("preview").removeAttribute("src");
  byId("preview").hidden = true;
  if (current.state?.mode !== "simulation") byId("empty").hidden = false;
}
async function poll() {
  try {
    const statusRevision = sourceRevision;
    const state = await request("status", {signal: AbortSignal.timeout(1800)});
    if (state.mode === "camera-test") {
      window.location.replace("/?mode=camera-test");
      return;
    }
    if (render(state, statusRevision)) {
      const preview = byId("preview");
      if (!preview.getAttribute("src")) preview.src = "/api/live.mjpg";
      preview.hidden = false;
      byId("empty").hidden = true;
    } else hidePreview();
  } catch {
    byId("actionStrip").className = "alert";
    byId("stationHeading").textContent = "Dữ liệu cũ";
    current.idle = false;
    current.pending = "";
    setIdleControls();
    setManualButtons();
    if (current.state?.mode === "hardware-manual") {
      byId("manualPrompt").textContent = "Mất trạng thái trạm. Chưa xác nhận từ ESP32.";
    }
    byId("connection").textContent = "Mất kết nối với trạm";
    byId("warning").textContent = "Dữ liệu cũ. Kiểm tra dịch vụ trạm.";
  }
  setTimeout(poll, 300);
}
poll();

const preview = document.getElementById("preview");
const cameraStatus = document.getElementById("cameraStatus");
const cameraMessage = document.getElementById("cameraMessage");
const capture = document.getElementById("capture");
const result = document.getElementById("result");
const snapshot = document.getElementById("snapshot");
const download = document.getElementById("download");
const messages = {
  "Waiting for a fresh camera frame": "Đang chờ khung hình mới từ camera.",
  "Camera is repeating a frozen frame": "Hình ảnh camera bị đứng. Thử di chuyển sách trong khung.",
  READ_FAILED_RECONNECTING: "Mất hình camera. Đang thử kết nối lại.",
  CAMERA_UNAVAILABLE_CLOSE_OTHER_APPS_CHECK_INDEX_AND_PRIVACY:
    "Không mở được camera. Kiểm tra kết nối, quyền truy cập và đóng ứng dụng khác đang dùng camera.",
  CAMERA_DRIVER_ERROR_SEE_LOG: "Lỗi trình điều khiển camera. Xem nhật ký trên máy tính.",
  CLOSED: "Camera đã đóng.",
  CAMERA_STATUS_UNAVAILABLE: "Không đọc được trạng thái camera.",
  MODEL_CLASS_MAPPING: "Cấu hình nhãn của mô hình chưa khớp.",
  MODEL_NO_PROBABILITIES: "Mô hình không trả về điểm phân loại.",
  MODEL_BAD_PROBABILITY: "Mô hình trả về điểm phân loại không hợp lệ.",
  JPEG_ENCODE: "Không tạo được ảnh JPEG.",
};
let cameraReady = false;
let capturing = false;

function localMessage(message, fallback) {
  if (typeof message !== "string") return fallback;
  if (Object.hasOwn(messages, message)) return messages[message];
  if (/^OPENING_.*_CAMERA_\d+$/.test(message)) return "Đang mở camera USB…";
  if (message.startsWith("Không chạy được mô hình AI (")) {
    return "Không chạy được mô hình AI. Kiểm tra tệp mô hình và cấu hình nhãn.";
  }
  if (message.startsWith("Không tìm được duy nhất camera ")
    || message === "Đang phân loại ảnh vừa chụp"
    || message === "Thiếu tệp mô hình. Kiểm tra đường dẫn best.pt.") {
    return message;
  }
  return fallback;
}

function renderCamera(message = "") {
  preview.hidden = !cameraReady;
  cameraMessage.hidden = cameraReady;
  if (!cameraReady && cameraMessage.textContent !== message) {
    cameraMessage.textContent = message;
  }
  const state = cameraReady ? "ready" : "offline";
  if (cameraStatus.dataset.state !== state) {
    cameraStatus.dataset.state = state;
    cameraStatus.textContent = cameraReady ? "Có tín hiệu" : "Chưa có hình";
  }
  capture.disabled = !cameraReady || capturing;
}

preview.onerror = () => {
  preview.removeAttribute("src");
  cameraReady = false;
  renderCamera("Mất luồng hình. Đang thử kết nối lại.");
};

async function errorMessage(response, fallback) {
  const body = await response.json().catch(() => ({}));
  return localMessage(body?.detail, fallback);
}

async function refreshPreview() {
  let message = "";
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    if (!response.ok) throw new Error("CAMERA_STATUS_UNAVAILABLE");
    const status = await response.json();
    if (status.mode !== "camera-test") {
      window.location.replace("/");
      return;
    }
    if (status.camera) throw new Error(status.camera);
    if (!preview.getAttribute("src")) preview.src = "/api/live.mjpg";
    cameraReady = true;
  } catch (error) {
    if (preview.getAttribute("src")) preview.removeAttribute("src");
    cameraReady = false;
    message = error instanceof TypeError
      ? "Mất kết nối với dịch vụ trên máy tính."
      : localMessage(error.message, "Không lấy được hình camera. Kiểm tra kết nối và quyền truy cập.");
  }
  renderCamera(message);
  window.setTimeout(refreshPreview, 250);
}

capture.addEventListener("click", async () => {
  if (!cameraReady || capturing) return;
  capturing = true;
  capture.disabled = true;
  snapshot.hidden = download.hidden = true;
  delete result.dataset.verdict;
  result.textContent = "Đang chụp và phân loại…";
  try {
    const response = await fetch("/api/capture", { method: "POST" });
    if (!response.ok) {
      throw new Error(await errorMessage(response, "Chụp hoặc chạy mô hình thất bại."));
    }
    const data = await response.json();
    const percent = (data.confidence * 100).toLocaleString("vi-VN", { maximumFractionDigits: 1 });
    result.textContent = data.prediction + " · " + data.label + " · Độ tin cậy " + percent + "%";
    result.dataset.verdict = data.prediction;
    snapshot.src = download.href = data.image;
    snapshot.hidden = download.hidden = false;
  } catch (error) {
    result.textContent = error instanceof TypeError ? "Mất kết nối với dịch vụ trên máy tính." : error.message;
  } finally {
    capturing = false;
    capture.disabled = !cameraReady;
  }
});

refreshPreview();

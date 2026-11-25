// Run with node --test tests/web/station_ui.test.js. No browser or hardware required.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const app = fs.readFileSync(path.join(__dirname, "../../software/web/static/app.js"), "utf8");

function consoleFixture(fetch) {
  const nodes = new Map();
  class Element {
    constructor() {
      this.children = [];
      this.elements = [];
      this.elements.port = { value: "" };
      this.files = [];
      this.textContent = "";
      this.hidden = false;
    }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    replaceWith(node) { nodes.set(this.id, node); }
    getAttribute(name) { return this[name] || null; }
    removeAttribute(name) { delete this[name]; }
  }
  function byId(id) {
    if (!nodes.has(id)) {
      const node = new Element();
      node.id = id;
      nodes.set(id, node);
    }
    return nodes.get(id);
  }
  // Leave the startup poll pending. Individual cases feed status snapshots explicitly.
  const context = vm.createContext({
    document: { getElementById: byId, createElement: () => new Element() },
    fetch: (url, options) => url === "/api/status" ? new Promise(() => {}) : fetch(url, options),
    performance, AbortSignal, clearTimeout: () => {}, setTimeout: () => 1,
  });
  vm.runInContext(app, context);
  return { byId, run: (code) => vm.runInContext(code, context), context };
}

const base = { mode: "hardware-manual", board: { phase: "OFF", reason: "STARTUP" }, counts: { total: 0, ok: 0, ng: 0 } };
const json = (status, payload) => ({ ok: status < 400, status, json: async () => payload });

test("failed validation shows the book and remedy next to validation with settings closed", async () => {
  const ui = consoleFixture(() => json(409, { detail: {
    code: "KNOWN_BOOK_FAILURE", book: "IMG_7", truth: "NG", label: "ảnh bình thường",
    confidence: 0.999, threshold: 0.85, decision: "OK",
    message: "IMG_7: expected NG, decision OK.", remedy: "Use Manual Mechanics.",
  } }));
  ui.context.state = { ...base, mode: "hardware" };
  ui.run("render(state)");
  await ui.byId("threshold").onclick();
  assert.match(ui.byId("calibrationResult").textContent,
    /IMG_7 · nhãn thực tế NG · dự đoán ảnh bình thường · độ tin cậy 99,9% · ngưỡng 85,0% · quyết định OK\. Dừng phân loại tự động\./);
});

test("board stop wins over legacy diagnostics, current measurements show ranges, units and percent", () => {
  const ui = consoleFixture();
  ui.context.state = { ...base, last_stop: { reason: "RELEASE_JAM", diagnostics: { inspection: { message: "Old blurry image" } } } };
  ui.run("render(state)");
  assert.match(ui.byId("stopMessage").textContent, /chưa rời/);
  assert.doesNotMatch(ui.byId("stopMessage").textContent, /blurry/);
  ui.context.state.last_stop = { reason: "INSPECTION_HOLD", diagnostic: {
    code: "BAD_LIGHT", message: "Image too dark.", remedy: "Adjust lighting and avoid glare.",
    measured: 5, limit: [35, 235],
  } };
  ui.run("render(state)");
  assert.match(ui.byId("stopMessage").textContent, /Đã dừng.*Độ sáng ảnh/);
  assert.match(ui.byId("stopHelp").textContent, /tránh lóa/);
  assert.equal(ui.byId("stopMetrics").children[0].children[0].textContent, "Đo được");
  assert.equal(ui.byId("stopMetrics").children[1].children[1].textContent, "35–235 mức xám (0–255)");
  assert.equal(ui.run('diagnosticValue(0.65, "LOW_CONFIDENCE")'), "65,0%");
  assert.equal(ui.run('diagnosticValue(8, "MANUAL_TIMEOUT")'), "8 giây");
  assert.match(ui.run('diagnosticValue([480, 640], "FRAME_SIZE_CHANGED")'), /480 × 640 điểm ảnh/);
});

test("submitted decision remains keyed and waits for an explicit board ACK", async () => {
  const ui = consoleFixture(() => json(202, { accepted: true }));
  const board = { phase: "WAIT_AI", capture_id: "station-1", job: 1 };
  ui.context.state = { ...base, board, manual_remaining_s: 6 };
  ui.run("render(state)");
  await ui.byId("manualOK").onclick();
  ui.run("render(state)");
  assert.match(ui.byId("manualPrompt").textContent, /Lượt 1.*chờ ESP32 xác nhận/);
  assert.equal(ui.byId("manualNG").disabled, true);
  const decision = { key: board.capture_id, verdict: "OK", state: "queued" };
  ui.context.state = { ...base, board, manual_remaining_s: null, manual_decision: decision };
  ui.run("render(state)");
  assert.match(ui.byId("manualPrompt").textContent, /Đã gửi.*chờ ESP32 xác nhận/);
  decision.state = "acknowledged";
  ui.context.state.board = { phase: "RELEASE", job: 1 };
  ui.run("render(state)");
  assert.match(ui.byId("manualPrompt").textContent, /ESP32 đã nhận OK/);
});

test("preview follows the active upload and suppresses stale responses", async () => {
  const ui = consoleFixture(() => json(200, { simulation_image_version: "second" }));
  ui.context.state = { ...base, mode: "simulation", simulation_image_version: "first" };
  ui.run("render(state)");
  const previous = ui.byId("simulationPreview");
  assert.equal(previous.src, "/api/sim/image?version=first");
  previous.onload();
  ui.byId("simulationFile").files = [{ name: "second.jpg", type: "image/jpeg" }];
  ui.byId("simulationFile").onchange();
  assert.equal(ui.byId("simulationPreview"), previous);
  assert.match(ui.byId("simulationImageResult").textContent, /đã chọn/);
  await ui.byId("simulationInput").onsubmit({ preventDefault() {} });
  const active = ui.byId("simulationPreview");
  assert.equal(active.src, "/api/sim/image?version=second");
  ui.run("render(state, 0)");
  previous.onload();
  assert.equal(ui.byId("simulationPreview"), active);
  assert.equal(active.hidden, true);
  active.onload();
  assert.equal(active.hidden, false);
  ui.context.state.simulation_image_version = null;
  ui.run("render(state)");
  active.onload();
  assert.equal(active.hidden, true);
  assert.match(ui.byId("simulationSource").textContent, /Kết quả mô phỏng/);
});

test("a blocked start reports CLEAR_STATION beside simulation controls", async () => {
  const ui = consoleFixture(() => json(409, { detail: "CLEAR_STATION" }));
  const start = ui.byId("actions").children[0];
  await start.onclick();
  assert.match(ui.byId("simulationFeedback").textContent, /Dọn trống vùng IR/);
});

test("a selected or uploading photo cannot accidentally route a manual simulated book", async () => {
  const requests = [];
  let completeUpload;
  const ui = consoleFixture((url) => {
    requests.push(url);
    if (url === "/api/sim/image") return new Promise((resolve) => { completeUpload = resolve; });
    return json(200, { ok: true });
  });
  const file = ui.byId("simulationFile");
  file.files = [{ name: "new-book.png", type: "image/png" }];
  const insert = ui.byId("actions").children[1];
  await insert.onclick();
  assert.deepEqual(requests, []);
  assert.match(ui.byId("simulationFeedback").textContent, /Dùng ảnh mô phỏng/);
  const uploading = ui.byId("simulationInput").onsubmit({ preventDefault() {} });
  await insert.onclick();
  await ui.byId("demoActions").children[0].onclick();
  assert.match(ui.byId("simulationFeedback").textContent, /Chờ tải ảnh/);
  assert.deepEqual(requests, ["/api/sim/image"]);
  completeUpload(json(200, { simulation_image_version: "loaded" }));
  await uploading;
  assert.equal(file.value, "");
  file.files = []; // The browser clears the FileList when its value is reset.
  await insert.onclick();
  assert.deepEqual(requests, ["/api/sim/image", "/api/sim/insert"]);
});

test("history pins its job while current fault and next shift update independently", async () => {
  const first = { id: "boot-3", created: "2026-11-23T08:15:00Z", verdict: "NG", label: "ảnh lỗi",
    confidence: 0.8456, stop_reason: "NG_NOT_CLEAR", status: "FAULT", has_image: 1 };
  const ui = consoleFixture(() => json(200, first));
  ui.context.state = { ...base, mode: "hardware", shift_id: 1, jobs: [first] };
  ui.run("render(state)");
  await ui.byId("jobs").children[0].onclick();
  assert.equal(ui.byId("jobs").children[0].children[1].className, "verdict-ng");
  assert.match(ui.byId("detail").textContent, /84,6%.*IR chưa trống/);
  ui.context.state.jobs = [{ id: "boot-12", status: "FAULT", stop_reason: "BOOK_MOVED" }];
  ui.context.state.board = { phase: "FAULT", reason: "BOOK_MOVED" };
  ui.run("render(state)");
  assert.match(ui.byId("detailHeading").textContent, /Đang xem.*#3/);
  assert.match(ui.byId("warning").textContent, /Sách rời IR/);
  ui.byId("follow").onclick();
  assert.match(ui.byId("detail").textContent, /Chưa có ảnh/);
  assert.equal(ui.byId("decisionImage").hidden, true);
  ui.context.state.jobs = [];
  ui.context.state.shift_id = 2;
  ui.run("render(state)");
  assert.equal(ui.byId("decisionText").textContent, "Chưa có lượt");
});

test("settings preserve submitted option values and localize their display and validation", async () => {
  const ui = consoleFixture(() => json(200, {
    values: { uncertain_policy: "hold", min_sharpness: 60 }, defaults: { uncertain_policy: "hold", min_sharpness: 45 },
    limits: { uncertain_policy: { choices: ["hold", "strict_ng"] }, min_sharpness: { unit: "Laplacian variance" } },
  }));
  ui.context.state = { ...base, mode: "hardware" };
  ui.run("render(state)");
  await ui.run("loadSettings()");
  const [policyField, advanced] = ui.byId("settingsInputs").children;
  assert.match(policyField.children[1].textContent, /Mặc định Tạm giữ sách/);
  assert.equal(policyField.children[0].children[1].value, "strict_ng");
  assert.equal(policyField.children[0].children[1].textContent, "Xếp NG nếu ảnh hợp lệ");
  assert.match(advanced.children[1].children[1].textContent, /phương sai Laplace/);
  assert.equal(ui.run('describe("stabilize_s must be between 0.05 and 2.0")'), "Chờ ổn định trước khi chụp phải từ 0,05 đến 2.");
});

test("device and simulated hold states display localized names while keeping command identifiers", async () => {
  const ui = consoleFixture(() => json(200, { ok: true }));
  ui.context.state = {
    ...base, mode: "hardware", connected_port: "COM5",
    bridge: { port: "COM5", radio: "RADIO_READY", age_s: 2 },
    health: "Camera is repeating a frozen frame", link_error: "could not open port 'COM5'",
  };
  ui.run("render(state)");
  assert.equal(ui.byId("connection").textContent, "COM5 · Đã kết nối");
  assert.match(ui.byId("deviceDiagnostic").textContent, /Hình ảnh camera bị đứng.*Không mở được cổng COM5.*Bộ chuyển tiếp · Đã sẵn sàng/);
  ui.context.state = {
    ...base, mode: "simulation", jobs: [{
      id: "sim-1", verdict: "HOLD", label: "Image file", reason: "Operator selected a simulated hold.",
      policy: "simulation", status: "HOLD",
    }],
  };
  ui.run("render(state)");
  assert.equal(ui.byId("decisionText").textContent, "Tạm giữ");
  assert.match(ui.byId("detail").textContent, /Ảnh đã tải.*Người vận hành chọn tạm giữ trong mô phỏng.*Mô phỏng/);
  assert.equal(ui.byId("jobs").children[0].children[1].className, "verdict-hold");
});

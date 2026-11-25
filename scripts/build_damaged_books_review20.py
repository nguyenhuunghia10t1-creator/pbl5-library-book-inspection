"""Build an offline, proposal-only review of the fixed 20 Damaged Books images.

Only the 40 selected image/label files are read. No model or test files are opened.
Curated observations are inputs, never inferred by this script.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import csv
import hashlib
import html
import io
import json
import math
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["Barcode", "Notch", "Ripped", "Spot", "Wornout"]
COLORS = ["#1674cd", "#b96d00", "#e12a39", "#a728bd", "#188743"]
STATUSES = {"keep", "change_proposed", "needs_review"}
ACTIONS = {"keep", "add", "delete", "change_class", "adjust_box", "merge", "needs_review"}
DEFAULT_DATASET = ROOT / "data/local/damaged_books_v1/split-reviewed-v1"
DEFAULT_OUTPUT = ROOT / "data/local/damaged_books_v1/run2-review20"
DEFAULT_DECISIONS = ROOT / "docs/reviews/damaged_books_review20.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_box(box):
    require(len(box) == 5, "Box must contain class,x,y,w,h")
    c, x, y, w, h = box
    require(type(c) is int and 0 <= c < 5, "Invalid class ID")
    require(all(isinstance(v, (int, float)) and math.isfinite(v) for v in box[1:]), "Nonfinite box")
    require(w > 0 and h > 0, "Zero-area box")
    require(x - w / 2 >= -1e-8 and y - h / 2 >= -1e-8
            and x + w / 2 <= 1 + 1e-8 and y + h / 2 <= 1 + 1e-8, "Box outside image")


def read_labels(path):
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        fields = line.split()
        require(len(fields) == 5, "Invalid YOLO row")
        raw_class = float(fields[0])
        require(raw_class.is_integer(), "Fractional class ID")
        box = [int(raw_class), *map(float, fields[1:])]
        validate_box(box)
        result.append(box)
    return result


def after_box(action, original, size):
    c = action.get("class_id", original[0] if original else None)
    if "xyxy_px" in action:
        left, top, right, bottom = action["xyxy_px"]
        width, height = size
        require(0 <= left < right <= width and 0 <= top < bottom <= height, "Invalid pixel box")
        result = [c, (left + right) / (2 * width), (top + bottom) / (2 * height),
                  (right - left) / width, (bottom - top) / height]
    else:
        require(original is not None, "New box needs coordinates")
        result = [c, *original[1:]]
    validate_box(result)
    return result


def apply_proposals(originals, actions, size):
    """Return display candidates; unresolved boxes stay and are visibly marked."""
    covered = set()
    proposed = []
    changes = []
    for index, action in enumerate(actions, 1):
        kind = action["action"]
        require(kind in ACTIONS and action.get("reason", "").strip(), "Missing action or evidence")
        lines = action.get("source_lines", [])
        require(all(type(n) is int and 1 <= n <= len(originals) for n in lines), "Unknown source line")
        require(len(set(lines)) == len(lines) and not covered.intersection(lines), "Duplicate source coverage")
        require((not lines) == (kind == "add"), "Only additions can have no source")
        require(kind == "merge" or len(lines) <= 1, "Multiple source rows require merge")
        require(kind != "merge" or len(lines) >= 2, "Merge requires multiple rows")
        covered.update(lines)
        before = [originals[n - 1] for n in lines]
        if kind == "merge":
            require("xyxy_px" in action, "Merge needs explicit box")
        if kind == "change_class":
            require(action.get("class_id") != before[0][0], "Class change has no effect")
        if kind in {"keep", "needs_review", "delete"}:
            require("xyxy_px" not in action and "class_id" not in action, "Unexpected edit")
        after = [] if kind == "delete" else [
            after_box(action, before[0] if before else None, size)]
        for box in after:
            proposed.append({"box": box, "source_lines": lines,
                             "review_required": kind == "needs_review", "action_id": index})
        changes.append({**action, "action_id": index, "before": before, "after": after})
    require(covered == set(range(1, len(originals) + 1)), "Every existing box needs a disposition")
    return proposed, changes


def build_report(dataset, decisions):
    manifest_path = dataset / "split_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["classes"] == CLASSES == decisions["classes"], "Class table mismatch")
    require(manifest["dataset_version"] == decisions["dataset_version"], "Dataset version changed")
    require(sha256(manifest_path) == decisions["manifest_sha256"], "Manifest changed")
    lookup = {(split, item["image_id"]): item["group_id"] for split in ("train", "val")
              for item in manifest["assignment"][split]}
    records = decisions["records"]
    require(len(records) == 20 and Counter(r["split"] for r in records) == {"val": 12, "train": 8},
            "Require exactly 12 val + 8 train")
    require(len({r["image_id"] for r in records}) == 20, "Duplicate review ID")
    report = {"schema_version": 1, "purpose": "annotation proposals only; not a trainable dataset",
              "dataset_version": manifest["dataset_version"], "manifest_sha256": sha256(manifest_path),
              "classes": CLASSES, "records": [], "test_opened": False}
    for i, record in enumerate(records, 1):
        split, ident = record["split"], record["image_id"]
        require(lookup.get((split, ident)) == record["group_id"], "Wrong split/group")
        image_rel = f"{split}/images/{ident}.jpg"
        label_rel = f"{split}/labels/{ident}.txt"
        image_path, label_path = dataset / image_rel, dataset / label_rel
        require(sha256(image_path) == record["image_sha256"], f"Image changed: {ident}")
        require(sha256(label_path) == record["label_sha256"], f"Label changed: {ident}")
        image = cv2.imread(str(image_path))
        require(image is not None, f"Unreadable image: {ident}")
        height, width = image.shape[:2]
        require([width, height] == record["image_size"], "Image size changed")
        originals = read_labels(label_path)
        counts = [sum(b[0] == c for b in originals) for c in range(5)]
        require(counts == record["expected_class_counts"], "Class counts changed")
        proposed, changes = apply_proposals(originals, record["actions"], (width, height))
        questions = record.get("questions", [])
        require(all(q.get("question") and q.get("reason") and q.get("priority") in {"route", "label"}
                    for q in questions), "Incomplete review question")
        pending = bool(questions) or any(a["action"] == "needs_review" for a in changes)
        edited = any(a["action"] not in {"keep", "needs_review"} for a in changes)
        status = "needs_review" if pending else "change_proposed" if edited else "keep"
        require(status in STATUSES, "Invalid review status")
        require(record.get("observation"), "Missing original-image observation")
        report["records"].append({**record, "index": i, "image_path": image_rel,
                                  "label_path": label_rel, "original_boxes": originals,
                                  "proposed_boxes": proposed, "actions": changes, "status": status,
                                  "has_changes": edited, "has_questions": pending,
                                  "fully_approved": False})
    report["summary"] = {"images": 20, "splits": {"val": 12, "train": 8},
                         "statuses": dict(Counter(r["status"] for r in report["records"])),
                         "actions": dict(Counter(a["action"] for r in report["records"] for a in r["actions"])),
                         "route_question_images": [r["index"] for r in report["records"]
                             if any(q["priority"] == "route" for q in r.get("questions", []))]}
    return report


def svg_panel(uri, size, boxes):
    width, height = size
    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
             f'<image href="{uri}" width="{width}" height="{height}"/>']
    for item in boxes:
        c, x, y, w, h = item["box"]
        left, top, bw, bh = (x - w / 2) * width, (y - h / 2) * height, w * width, h * height
        pending = item.get("review_required", False)
        color = COLORS[c]
        source = "+".join(map(str, item["source_lines"])) or "mới"
        label = f'{source}:{CLASSES[c]}{" ?" if pending else ""}'
        dash = 'stroke-dasharray="6 3"' if pending else ""
        parts.append(f'<g><title>{html.escape(label)}</title><rect x="{left:.2f}" y="{top:.2f}" '
                     f'width="{bw:.2f}" height="{bh:.2f}" fill="none" stroke="{color}" '
                     f'stroke-width="2" {dash}/><text x="{max(0, left):.2f}" '
                     f'y="{max(12, top-3):.2f}" fill="{color}" font-size="12" '
                     f'paint-order="stroke" stroke="white" stroke-width="2">{html.escape(label)}</text></g>')
    return "".join(parts) + "</svg>"


def render_html(report, dataset):
    cards = []
    labels = {"keep": "Giữ đề xuất hiện tại", "change_proposed": "Có đề xuất sửa", "needs_review": "Cần xác nhận"}
    for row in report["records"]:
        uri = "data:image/jpeg;base64," + base64.b64encode((dataset / row["image_path"]).read_bytes()).decode("ascii")
        originals = [{"box": b, "source_lines": [n]} for n, b in enumerate(row["original_boxes"], 1)]
        panels = [f'<figure><figcaption>{caption}</figcaption>{svg_panel(uri, row["image_size"], boxes)}</figure>'
                  for caption, boxes in [("Ảnh gốc", []), ("Nhãn hiện tại", originals),
                                         ("Đề xuất — nét đứt: chưa rõ, giữ hộp gốc", row["proposed_boxes"])]]
        action_names = {"keep": "Giữ", "add": "Thêm", "delete": "Bỏ nhãn sai", "change_class": "Đổi lớp",
                        "adjust_box": "Chỉnh hộp", "merge": "Gộp hộp", "needs_review": "Cần xác nhận"}
        actions = "".join(f'<li><b>{action_names[a["action"]]} · dòng '
                          f'{html.escape(str(a.get("source_lines", [])))}</b>: {html.escape(a["reason"])}</li>'
                          for a in row["actions"])
        questions = "".join(f'<li>{"Ưu tiên phân tuyến: " if q["priority"] == "route" else ""}'
                            f'{html.escape(q["question"])} — {html.escape(q["reason"])}</li>'
                            for q in row.get("questions", []))
        route = any(q["priority"] == "route" for q in row.get("questions", []))
        cards.append(f'<article id="image-{row["index"]}" data-status="{row["status"]}" data-route="{str(route).lower()}">'
                     f'<h2>#{row["index"]} · {row["split"]} · {labels[row["status"]]}</h2>'
                     f'<p class="path">{html.escape(row["image_path"])}<br>{html.escape(row["group_id"])}</p>'
                     f'<p>{html.escape(row["observation"])}</p><div class="panels">{"".join(panels)}</div>'
                     f'<ul class="questions">{questions}</ul><details><summary>Đề xuất từng hộp ({len(row["actions"])})</summary>'
                     f'<ul>{actions}</ul></details></article>')
    summary = report["summary"]
    status_text = " · ".join(f'{labels[status]}: {count}' for status, count in summary["statuses"].items())
    return '''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rà 20 ảnh sách — đề xuất nhãn</title><style>
body{margin:0;font:16px system-ui;background:#f2f4f7;color:#17212b}header{background:white;padding:16px 24px;border-bottom:1px solid #ccc}
main{max-width:1500px;margin:auto;padding:16px}h1{font-size:24px;margin:0 0 8px}h2{font-size:20px}p{line-height:1.5}
article{background:white;padding:18px;margin-bottom:24px;border:1px solid #ccd2db;border-radius:8px}article[hidden]{display:none}
.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0;overflow:auto}figcaption{font-weight:600;min-height:48px}
svg{display:block;width:100%;background:#eee;cursor:zoom-in}figure.zoom{grid-column:1/-1}figure.zoom svg{width:1280px;max-width:none;cursor:zoom-out}
.path{font:12px monospace;overflow-wrap:anywhere;color:#46556b}li{margin:7px 0;line-height:1.45}.questions{background:#fff4dc;border-left:4px solid #d28a00;padding:8px 8px 8px 28px}.questions:empty{display:none}
select{font:inherit;padding:6px}details{margin-top:16px}a{color:#1261a6}@media(max-width:850px){.panels{grid-template-columns:1fr}figcaption{min-height:0}}
</style><header><h1>Rà 20 ảnh sách · đề xuất nhãn</h1>
<p>Chưa áp dụng vào dataset. Hộp nét đứt và dấu ? cần xác nhận; không có nghĩa ảnh sạch. Bấm ảnh để phóng to.</p>
<p>__SUMMARY__</p><label>Hiện <select id="filter"><option value="all">Tất cả 20 ảnh</option><option value="route">Câu hỏi ảnh hưởng khay A/B</option><option value="needs_review">Cần xác nhận</option><option value="change_proposed">Đề xuất sửa đã rõ</option><option value="keep">Giữ</option></select></label> <span id="count"></span>
<p><a href="review-summary.csv" download>Tải bảng CSV</a> · <a href="proposals.json" download>Tải JSON đề xuất</a></p></header><main>__CARDS__</main>
<script>const cards=[...document.querySelectorAll('article')];function filter(){let n=0;const v=document.querySelector('#filter').value;for(const c of cards){c.hidden=!(v==='all'||(v==='route'?c.dataset.route==='true':c.dataset.status===v));if(!c.hidden)n++}document.querySelector('#count').textContent=n+'/20 ảnh'}document.querySelector('#filter').addEventListener('change',filter);document.querySelectorAll('svg').forEach(s=>s.addEventListener('click',()=>s.closest('figure').classList.toggle('zoom')));filter();</script></html>'''.replace("__SUMMARY__", html.escape(status_text) + " · Barcode: xanh dương; Notch: cam; Ripped: đỏ; Spot: tím; Wornout: xanh lá").replace("__CARDS__", "".join(cards))


def render_csv(report):
    stream = io.StringIO(newline="")
    fields = ["index", "split", "image_path", "group_id", "status", "original_boxes", "proposed_boxes",
              "actions", "route_question", "observation", "questions", "image_sha256", "label_sha256"]
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    for r in report["records"]:
        writer.writerow({**{k: r[k] for k in fields if k in r and k not in {"original_boxes", "proposed_boxes", "actions", "questions"}},
                         "original_boxes": len(r["original_boxes"]), "proposed_boxes": len(r["proposed_boxes"]),
                         "actions": "; ".join(f'{a["action"]}:{a.get("source_lines", [])}' for a in r["actions"]),
                         "route_question": any(q["priority"] == "route" for q in r.get("questions", [])),
                         "questions": " | ".join(q["question"] for q in r.get("questions", []))})
    return "\ufeff" + stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Validate sources and existing generated files without writing")
    args = parser.parse_args()
    dataset, output = args.dataset.resolve(), args.output.resolve()
    # Outputs cannot collide with any input or the original review page.
    require(output.is_relative_to(ROOT / "data/local"), "Output must be inside ignored data/local")
    for protected in (dataset, ROOT / "data/local/damaged_books_v1/prepared-verified"):
        require(not output.is_relative_to(protected) and not protected.is_relative_to(output), "Unsafe output location")
    decisions = json.loads(args.decisions.read_text(encoding="utf-8"))
    report = build_report(dataset, decisions)
    outputs = {"proposals.json": json.dumps(report, ensure_ascii=False, indent=2) + "\n",
               "review-summary.csv": render_csv(report), "review.html": render_html(report, dataset)}
    if args.check:
        for name, content in outputs.items():
            require((output / name).read_bytes() == content.encode("utf-8"), f"Generated output differs: {name}")
    else:
        # Preserve operator edits: refuse to overwrite a changed generated file.
        old_lock = output / "generated-checksums.json"
        if old_lock.exists():
            for name, digest in json.loads(old_lock.read_text(encoding="utf-8")).items():
                require((output / name).is_file() and sha256(output / name) == digest,
                        f"Existing output was edited; use a new output folder: {name}")
        else:
            require(not any((output / n).exists() for n in outputs), "Unmanaged existing outputs")
        output.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (output / name).write_bytes(content.encode("utf-8"))
        (output / "generated-checksums.json").write_text(
            json.dumps({name: sha256(output / name) for name in outputs}, indent=2) + "\n", encoding="utf-8")
    # Re-read only selected source files to detect edits during generation.
    for row in report["records"]:
        require(sha256(dataset / row["image_path"]) == row["image_sha256"]
                and sha256(dataset / row["label_path"]) == row["label_sha256"], "Source changed during build")
    print("PASS", json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()

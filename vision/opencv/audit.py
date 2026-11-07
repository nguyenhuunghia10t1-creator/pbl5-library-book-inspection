"""Read-only integrity and declared-provenance audit of schema-v1 capture bundles.

metadata.json is authoritative. A matching checksum does not establish that the
declared source, book identity, crop boundary, or defect labels are ground truth.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import uuid


IMAGE_KINDS = ("raw", "cover", "debug")
SOURCE_KINDS = ("real", "imported", "synthetic")
COLLECTION_STATUSES = ("accepted", "review")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Non-finite JSON value: {value}")


def _parse_json(text):
    value = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def _is_link(path):
    return path.is_symlink() or path.is_junction()


def _uuid(value):
    if not isinstance(value, str):
        return False
    try:
        return str(uuid.UUID(value)) == value
    except ValueError:
        return False


def _timestamp(value):
    try:
        return isinstance(value, str) and datetime.fromisoformat(value).utcoffset() is not None
    except (ValueError, OverflowError):
        return False


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _Audit:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.issues = []
        self.records = {}
        self.valid_records = []
        self.sessions = {}
        self.packets = {}
        self.discovered = 0
        self.pending = 0

    def issue(self, code, path, message, severity="error"):
        self.issues.append({"severity": severity, "code": code,
                            "path": str(path), "message": message})

    def read_object(self, path, relative):
        if _is_link(path):
            self.issue("LINK_NOT_ALLOWED", relative, "Linked files/directories are not audited.")
            return None
        try:
            return _parse_json(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError) as error:
            self.issue("INVALID_JSON", relative, str(error))
            return None

    def session(self, identifier):
        if identifier in self.sessions:
            return self.sessions[identifier]
        relative = f"sessions/{identifier}/session.json"
        folder = self.root / "sessions" / identifier
        if _is_link(self.root / "sessions") or _is_link(folder):
            self.issue("LINK_NOT_ALLOWED", relative, "Session path contains a link.")
            result = None
        else:
            result = self.read_object(folder / "session.json", relative)
        self.sessions[identifier] = result
        return result

    def bundle(self, folder):
        self.discovered += 1
        prefix = f"captures/{folder.name}"
        before = len(self.issues)
        if _is_link(folder):
            self.issue("LINK_NOT_ALLOWED", prefix, "Linked capture directories are not audited.")
            return
        record = self.read_object(folder / "metadata.json", prefix + "/metadata.json")
        if record is None:
            return
        # Retain even malformed metadata for manifest comparison; never count it as valid.
        self.records[folder.name] = record
        if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
            self.issue("INVALID_SCHEMA", prefix, "Expected integer schema_version 1.")
        if not _uuid(folder.name) or record.get("image_id") != folder.name:
            self.issue("INVALID_IMAGE_ID", prefix, "Folder and metadata must share a canonical UUID.")
        for field in ("timestamp_utc", "saved_utc"):
            if not _timestamp(record.get(field)):
                self.issue("INVALID_TIMESTAMP", prefix, f"{field} must include a UTC offset.")
        source = record.get("source_kind")
        if source not in SOURCE_KINDS:
            self.issue("INVALID_SOURCE", prefix, "source_kind must be real/imported/synthetic.")
        status = record.get("collection_status")
        if status not in COLLECTION_STATUSES:
            self.issue("INVALID_COLLECTION_STATUS", prefix, "Expected accepted or review.")
        copy_id = record.get("copy_id")
        invalid_copy_id = copy_id is not None and (
            not isinstance(copy_id, str) or not copy_id.strip())
        if "copy_id" not in record or invalid_copy_id:
            self.issue("INVALID_COPY_ID", prefix, "copy_id must be a nonempty string or null.")
        qr = record.get("qr")
        if (not isinstance(qr, dict) or "book_id" not in qr or qr["book_id"] != copy_id or
                not isinstance(qr.get("status"), str) or not qr["status"].strip()):
            self.issue("QR_ID_MISMATCH", prefix, "QR requires a nonempty status and book_id matching copy_id.")
        if status == "accepted" and (record.get("vision_status") != "READY" or
                                    not isinstance(qr, dict) or qr.get("status") != "VALID_FORMAT" or
                                    not isinstance(copy_id, str) or not copy_id.strip()):
            self.issue("INVALID_ACCEPTED", prefix, "Accepted captures require READY and a formatted QR ID.")
        camera_session = record.get("camera_session_id")
        sequence = record.get("capture_seq")
        if (not isinstance(camera_session, str) or not camera_session.strip() or
                type(sequence) is not int or sequence < 1):
            self.issue("INVALID_FRAME_REFERENCE", prefix, "Expected a camera_session_id and positive capture_seq.")
        else:
            packet = (camera_session, sequence)
            if packet in self.packets:
                self.issue("DUPLICATE_FRAME", prefix, f"Frame also appears in {self.packets[packet]}.")
            self.packets[packet] = prefix
        session_id = record.get("session_id")
        if not _uuid(session_id):
            self.issue("INVALID_SESSION_ID", prefix, "Expected a canonical session UUID.")
        else:
            session = self.session(session_id)
            if session is None:
                self.issue("SESSION_UNAVAILABLE", prefix, "Cannot verify the referenced session.")
            elif (session.get("session_id") != session_id or session.get("source_kind") != source or
                  session.get("source_description") != record.get("source_description")):
                self.issue("SESSION_MISMATCH", prefix, "Capture and session provenance do not agree.")
            elif not _timestamp(session.get("created_utc")):
                self.issue("INVALID_SESSION_TIMESTAMP", prefix, "Session created_utc must include a UTC offset.")
            background = record.get("background_reference")
            if background is not None and session is not None:
                pattern = rf"sessions/{session_id}/background_[0-9a-f]{{12}}\.png"
                if not isinstance(background, str) or not re.fullmatch(pattern, background):
                    self.issue("INVALID_BACKGROUND_PATH", prefix, "Background must belong to the same session.")
                else:
                    path = self.root / background
                    if _is_link(path) or not path.is_file():
                        self.issue("BACKGROUND_UNAVAILABLE", prefix, "Background reference is missing or linked.")
        files, hashes = record.get("files"), record.get("sha256")
        if not isinstance(files, dict) or set(files) != set(IMAGE_KINDS):
            self.issue("INVALID_FILES", prefix, "files must contain exactly raw, cover and debug.")
        if not isinstance(hashes, dict) or set(hashes) != set(IMAGE_KINDS):
            self.issue("INVALID_HASHES", prefix, "sha256 must contain exactly raw, cover and debug.")
        for kind in IMAGE_KINDS:
            expected = prefix + f"/{kind}.png"
            if not isinstance(files, dict) or files.get(kind) != expected:
                self.issue("INVALID_IMAGE_PATH", prefix, f"{kind} must point to {expected}.")
                continue
            path = folder / f"{kind}.png"
            if _is_link(path):
                self.issue("LINK_NOT_ALLOWED", expected, "Linked images are not read.")
                continue
            declared = hashes.get(kind) if isinstance(hashes, dict) else None
            if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", declared):
                self.issue("INVALID_SHA256", expected, "Expected a 64-character SHA256 digest.")
                continue
            try:
                actual = _sha256(path)
            except OSError as error:
                self.issue("IMAGE_UNAVAILABLE", expected, str(error))
                continue
            if actual != declared.lower():
                self.issue("HASH_MISMATCH", expected, "Image bytes do not match metadata SHA256.")
        if len(self.issues) == before:
            self.valid_records.append(record)

    def manifest(self):
        path = self.root / "manifest.jsonl"
        if _is_link(path):
            self.issue("LINK_NOT_ALLOWED", "manifest.jsonl", "Linked manifests are not read.")
            return
        seen = set()
        try:
            with path.open(encoding="utf-8-sig") as stream:
                for number, line in enumerate(stream, 1):
                    if not line.strip():
                        continue
                    location = f"manifest.jsonl:{number}"
                    try:
                        record = _parse_json(line)
                    except ValueError as error:
                        self.issue("INVALID_MANIFEST_RECORD", location, str(error))
                        continue
                    identifier = record.get("image_id")
                    if not _uuid(identifier):
                        self.issue("INVALID_MANIFEST_ID", location, "Expected a canonical image UUID.")
                        continue
                    if identifier in seen:
                        self.issue("DUPLICATE_MANIFEST_ID", location, f"Repeated image_id {identifier}.")
                    seen.add(identifier)
                    if identifier not in self.records:
                        self.issue("ORPHAN_MANIFEST_RECORD", location, "No readable capture metadata for image_id.")
                    elif record != self.records[identifier]:
                        self.issue("MANIFEST_MISMATCH", location, "Manifest differs from authoritative metadata.")
        except (OSError, UnicodeError) as error:
            self.issue("MANIFEST_UNAVAILABLE", "manifest.jsonl", str(error))
            return
        for identifier in sorted(self.records.keys() - seen):
            self.issue("MISSING_MANIFEST_RECORD", f"captures/{identifier}", "Capture is not indexed in manifest.")

    def run(self):
        captures = self.root / "captures"
        if not self.root.is_dir():
            self.issue("COLLECTION_UNAVAILABLE", ".", "Collection root is not an existing directory.")
        elif _is_link(captures):
            self.issue("LINK_NOT_ALLOWED", "captures", "Linked capture roots are not audited.")
        elif not captures.is_dir():
            self.issue("CAPTURES_UNAVAILABLE", "captures", "No captures directory.")
        else:
            try:
                folders = sorted(captures.iterdir(), key=lambda p: p.name)
            except OSError as error:
                self.issue("CAPTURES_UNAVAILABLE", "captures", str(error))
                folders = []
            for folder in folders:
                if folder.name.startswith(".pending_"):
                    self.pending += 1
                    self.issue("PENDING_BUNDLE", f"captures/{folder.name}",
                               "Unfinished staging entry was left untouched.", "warning")
                elif folder.is_dir() or _is_link(folder):
                    self.bundle(folder)
                else:
                    self.issue("UNEXPECTED_CAPTURE_ENTRY", f"captures/{folder.name}",
                               "Expected a completed capture directory.", "warning")
            if not self.discovered:
                self.issue("NO_CAPTURES", "captures", "No completed captures to audit.")
            self.manifest()
        by_source = Counter(r["source_kind"] for r in self.valid_records)
        by_status = Counter(r["collection_status"] for r in self.valid_records)
        by_copy = {}
        for record in self.valid_records:
            key = record["copy_id"]
            if key not in by_copy:
                by_copy[key] = Counter()
            by_copy[key][record["collection_status"]] += 1
        errors = sum(issue["severity"] == "error" for issue in self.issues)
        return {
            "report_version": 1, "ok": errors == 0, "collection_root": str(self.root),
            "statistics_scope": "valid_bundles_only",
            "summary": {"captures": self.discovered, "valid_bundles": len(self.valid_records),
                        "invalid_bundles": self.discovered - len(self.valid_records),
                        "pending_entries": self.pending, "errors": errors,
                        "warnings": len(self.issues) - errors},
            "by_source_kind": {kind: by_source[kind] for kind in SOURCE_KINDS},
            "by_collection_status": {status: by_status[status] for status in COLLECTION_STATUSES},
            "by_copy_id": [
                {"copy_id": key, "captures": sum(counts.values()),
                 **{status: counts[status] for status in COLLECTION_STATUSES}}
                for key, counts in sorted(
                    by_copy.items(), key=lambda item: (item[0] is not None, item[0] or ""))
            ],
            "issues": sorted(self.issues, key=lambda issue: (issue["path"], issue["code"], issue["message"])),
            "limits": "Checks file integrity and declared provenance, not real-source truth, DB identity, crop correctness or defect labels.",
        }


def audit_collection(root):
    """Read a stopped collector's collection and return a JSON-serializable report."""
    return _Audit(root).run()

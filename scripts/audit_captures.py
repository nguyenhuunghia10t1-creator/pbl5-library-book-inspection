"""Audit capture bundles and their manifest without changing the collection."""
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vision.opencv.audit import audit_collection


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", nargs="?", type=Path, default=ROOT / "data/opencv/collection",
                        help="Collection directory (default: this repository's data/opencv/collection)")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable JSON report")
    args = parser.parse_args(argv)
    report = audit_collection(args.collection)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2, allow_nan=False))
    else:
        counts = report["summary"]
        print(f"{'PASS' if report['ok'] else 'FAIL'}: {counts['captures']} captures, "
              f"{counts['valid_bundles']} valid bundles, {counts['invalid_bundles']} invalid, "
              f"{counts['errors']} errors, {counts['warnings']} warnings")
        print("Statistics cover valid bundles only; accepted/review are capture statuses.")
        print("Source: " + ", ".join(f"{key}={value}" for key, value in report["by_source_kind"].items()))
        print("Collection: " + ", ".join(f"{key}={value}" for key, value in report["by_collection_status"].items()))
        for entry in report["by_copy_id"]:
            print(f"Copy {entry['copy_id'] if entry['copy_id'] is not None else '(unidentified)'}: "
                  f"{entry['captures']} captures, accepted={entry['accepted']}, review={entry['review']}")
        for issue in report["issues"]:
            print(f"{issue['severity'].upper()} {issue['path']} [{issue['code']}]: {issue['message']}")
        print(report["limits"])
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

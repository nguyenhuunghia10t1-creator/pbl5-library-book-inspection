"""Check source syntax, current documentation links and workspace folder paths."""
import ast
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    sources = [ROOT / "scripts", ROOT / "vision", ROOT / "software", ROOT / "tests", ROOT / "examples"]
    count = 0
    for folder in sources:
        for file in folder.rglob("*.py"):
            try:
                ast.parse(file.read_text(encoding="utf-8-sig"), filename=str(file))
                count += 1
            except (SyntaxError, UnicodeError) as error:
                errors.append(f"{file.relative_to(ROOT)}: {error}")
    # Session history and the immutable roadmap deliberately retain historical paths.
    documents = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "PROGRESS.md"]
    if (ROOT / "AGENTS.md").exists():
        documents.append(ROOT / "AGENTS.md")
    documents += [p for p in (ROOT / "docs").rglob("*.md") if p.name not in ("SESSION_LOG.md", "ROADMAP_SOURCE.md")]
    for folder in ("vision", "software", "firmware", "examples", "scripts", "data"):
        documents += [p for p in (ROOT / folder).rglob("README.md") if ".pio" not in p.parts and "local" not in p.parts]
    for file in documents:
        for destination in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8-sig")):
            if "://" in destination or destination.startswith("#"):
                continue
            destination = destination.split("#", 1)[0]
            if destination and not (file.parent / destination).exists():
                errors.append(f"{file.relative_to(ROOT)}: missing link {destination}")
    workspace = json.loads((ROOT / "smart-vision-inspection.code-workspace").read_text(encoding="utf-8"))
    for folder in workspace["folders"]:
        if not (ROOT / folder["path"]).is_dir():
            errors.append(f"Workspace missing folder: {folder['path']}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {count} Python sources, current documentation links, VS Code workspace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

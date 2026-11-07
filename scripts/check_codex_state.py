"""Validate Codex task/state structure, not the truth of evidence or hardware claims."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HEADER = ["ID", "Task", "Who", "Depends", "Acceptance", "Status", "Evidence"]
ID_PATTERN = re.compile(r"[HVBASFIER][0-9]{2}")
WHO_VALUES = {"CODEX", "USER-HW", "USER-DATA", "DECISION", "REVIEW"}
STATUS_VALUES = {"TODO", "IN_PROGRESS", "BLOCKED", "DONE", "DONE-SIM", "DONE-HW"}
DONE_VALUES = {"DONE", "DONE-SIM", "DONE-HW"}
STATE_FIELDS = ("Active task", "Last updated", "Branch", "Last green commit")


@dataclass(frozen=True)
class Task:
    identifier: str
    who: str
    depends: tuple[str, ...]
    status: str
    evidence: str
    line: int


def _visible_lines(lines):
    """Exclude fenced examples so a sample heading cannot become the task table."""
    visible = []
    fence = None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            visible.append((number, ""))
        else:
            visible.append((number, line if fence is None else ""))
    return visible


def _cells(line, number, errors):
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        errors.append(f"docs/codex/TASKS.md:{number}: table row must start and end with '|'.")
        return None
    cells = [cell.strip() for cell in stripped[1:-1].split("|")]
    if len(cells) != 7:
        errors.append(f"docs/codex/TASKS.md:{number}: expected 7 columns, found {len(cells)}; "
                      "do not put '|' inside a cell, even escaped or in code.")
        return None
    return cells


def _parse_tasks(lines, errors):
    visible = _visible_lines(lines)
    headings = []
    for index, (number, line) in enumerate(visible):
        match = re.fullmatch(r"(#{1,6})\s+Tasks\s*#*\s*", line.strip())
        if match:
            headings.append((index, number, len(match.group(1))))
    if len(headings) != 1:
        errors.append("docs/codex/TASKS.md: expected exactly one 'Tasks' heading, "
                      f"found {len(headings)}.")
        return {}
    start, heading_line, level = headings[0]
    section = []
    for number, line in visible[start + 1:]:
        heading = re.match(r"^(#{1,6})\s+", line.strip())
        if heading and len(heading.group(1)) <= level:
            break
        section.append((number, line))
    table_start = next((i for i, (_, line) in enumerate(section) if "|" in line), None)
    if table_start is None:
        errors.append(f"docs/codex/TASKS.md:{heading_line}: missing Tasks table.")
        return {}
    number, line = section[table_start]
    if _cells(line, number, errors) != HEADER:
        errors.append(f"docs/codex/TASKS.md:{number}: header must be " + " | ".join(HEADER) + ".")
    if table_start + 1 >= len(section):
        errors.append(f"docs/codex/TASKS.md:{number}: missing table separator row.")
        return {}
    separator_number, separator = section[table_start + 1]
    separators = _cells(separator, separator_number, errors)
    if separators is None or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
        errors.append(f"docs/codex/TASKS.md:{separator_number}: invalid Markdown table separator.")
    tasks = {}
    ended = False
    for number, line in section[table_start + 2:]:
        if not line.strip():
            ended = True
            continue
        if ended:
            if "|" in line:
                errors.append(f"docs/codex/TASKS.md:{number}: only one contiguous table is allowed under Tasks.")
            continue
        cells = _cells(line, number, errors)
        if cells is None:
            continue
        identifier, title, who, dependency_text, acceptance, status, evidence = cells
        prefix = f"docs/codex/TASKS.md:{number} [{identifier or '?'}]"
        if not ID_PATTERN.fullmatch(identifier):
            errors.append(f"{prefix}: ID must match ^[HVBASFIER][0-9]{{2}}$.")
            continue
        if identifier in tasks:
            errors.append(f"{prefix}: duplicate ID (first at line {tasks[identifier].line}).")
            continue
        if not title or not acceptance:
            errors.append(f"{prefix}: Task and Acceptance must be nonempty.")
        if who not in WHO_VALUES:
            errors.append(f"{prefix}: invalid Who '{who}'; choose {', '.join(sorted(WHO_VALUES))}.")
        if status not in STATUS_VALUES:
            errors.append(f"{prefix}: invalid Status '{status}'; choose {', '.join(sorted(STATUS_VALUES))}.")
        depends = () if dependency_text == "-" else tuple(part.strip() for part in dependency_text.split(","))
        if any(not ID_PATTERN.fullmatch(item) for item in depends):
            errors.append(f"{prefix}: Depends must be '-' or comma-separated task IDs.")
        if len(set(depends)) != len(depends):
            errors.append(f"{prefix}: duplicate dependency ID.")
        tasks[identifier] = Task(identifier, who, depends, status, evidence, number)
    if not tasks:
        errors.append(f"docs/codex/TASKS.md:{heading_line}: Tasks table must contain at least one valid task ID.")
    return tasks


def _placeholder(value):
    normalized = value.strip().strip("`*_[] ").casefold()
    if normalized in {"", "-", "--", "---", "—", "–", "...", "…", "n/a", "na", "none", "null",
                      "unknown", "todo", "tbd", "tbc", "pending", "placeholder", "not_run", "not run",
                      "not provided", "not available", "not recorded", "to be added", "chưa có", "chưa xác minh", "chưa kiểm chứng", "chờ"}:
        return True
    if re.fullmatch(r"[-\u2014\u2013.\u2026?]+", normalized):
        return True
    if re.match(r"^(?:todo|tbd|tbc|placeholder|pending|unknown|n/a|not_run|not run)(?:\s|:)", normalized):
        return True
    return normalized.startswith("<") and normalized.endswith(">") and "://" not in normalized


def _check_tasks(tasks, errors):
    for task in tasks.values():
        prefix = f"docs/codex/TASKS.md:{task.line} [{task.identifier}]"
        for dependency in task.depends:
            if dependency == task.identifier:
                errors.append(f"{prefix}: task cannot depend on itself.")
            elif dependency not in tasks:
                errors.append(f"{prefix}: dependency '{dependency}' does not exist.")
        if task.status in DONE_VALUES:
            if _placeholder(task.evidence):
                errors.append(f"{prefix}: {task.status} requires non-placeholder Evidence.")
            for dependency in task.depends:
                if dependency in tasks and tasks[dependency].status not in DONE_VALUES:
                    errors.append(f"{prefix}: completed task depends on unfinished {dependency} "
                                  f"({tasks[dependency].status}).")
    visiting = []
    finished = set()

    def visit(identifier):
        if identifier in finished:
            return
        if identifier in visiting:
            cycle = visiting[visiting.index(identifier):] + [identifier]
            errors.append("docs/codex/TASKS.md: dependency cycle: " + " -> ".join(cycle) + ".")
            return
        visiting.append(identifier)
        for dependency in tasks[identifier].depends:
            if dependency in tasks and dependency != identifier:
                visit(dependency)
        visiting.pop()
        finished.add(identifier)

    for identifier in tasks:
        visit(identifier)
    active = [task.identifier for task in tasks.values() if task.who == "CODEX" and task.status == "IN_PROGRESS"]
    if len(active) > 1:
        errors.append("docs/codex/TASKS.md: at most one CODEX task may be IN_PROGRESS; found " + ", ".join(active) + ".")
    return active


def _check_state(lines, tasks, active, errors):
    fields = {}
    for index, label in enumerate(STATE_FIELDS):
        number = index + 1
        line = lines[index] if index < len(lines) else ""
        prefix = f"{label}: "
        if not line.startswith(prefix) or not line[len(prefix):].strip():
            errors.append(f"docs/codex/STATE.md:{number}: expected '{label}: <value>' in the first four lines.")
        else:
            fields[label] = line[len(prefix):].strip()
    updated = fields.get("Last updated")
    if updated is not None:
        try:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", updated):
                raise ValueError
            date.fromisoformat(updated)
        except ValueError:
            errors.append("docs/codex/STATE.md:2: Last updated must be a valid calendar date in YYYY-MM-DD format.")
    declared = fields.get("Active task")
    if declared is None:
        return
    if declared != "NONE" and declared not in tasks:
        errors.append(f"docs/codex/STATE.md:1: Active task '{declared}' does not exist in Tasks.")
    elif declared != "NONE" and (tasks[declared].who != "CODEX" or tasks[declared].status != "IN_PROGRESS"):
        errors.append(f"docs/codex/STATE.md:1: Active task '{declared}' must be a CODEX task IN_PROGRESS.")
    if not active and declared != "NONE":
        errors.append("docs/codex/STATE.md:1: Active task must be NONE when no CODEX task is IN_PROGRESS.")
    elif active and (len(active) != 1 or declared != active[0]):
        errors.append("docs/codex/STATE.md:1: Active task must match the single CODEX task IN_PROGRESS: " + ", ".join(active) + ".")


def validate(root: Path) -> list[str]:
    """Return actionable structural errors; never inspect or certify task evidence."""
    root = Path(root)
    errors = []
    documents = {}
    for name in ("TASKS.md", "STATE.md"):
        path = root / "docs" / "codex" / name
        try:
            documents[name] = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as error:
            errors.append(f"docs/codex/{name}: cannot read file: {error}")
    tasks = _parse_tasks(documents["TASKS.md"], errors) if "TASKS.md" in documents else {}
    active = _check_tasks(tasks, errors)
    if "STATE.md" in documents:
        _check_state(documents["STATE.md"], tasks, active, errors)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root (default: this script's parent repository)")
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS: Codex task/state structure and consistency; evidence content and hardware are not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

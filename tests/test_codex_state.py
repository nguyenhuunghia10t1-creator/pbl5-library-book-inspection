"""Structural task/state regressions, using isolated temporary Markdown fixtures."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_codex_state import validate


ROOT = Path(__file__).resolve().parents[1]
HEADER = "| ID | Task | Who | Depends | Acceptance | Status | Evidence |"
SEPARATOR = "|---|---|---|---|---|---|---|"


def row(identifier="H01", who="CODEX", depends="-", status="TODO", evidence="-"):
    return f"| {identifier} | Focused output | {who} | {depends} | Run documented checks | {status} | {evidence} |"


class CodexStateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.folder = self.root / "docs" / "codex"
        self.folder.mkdir(parents=True)

    def write(self, rows=None, active="NONE", updated="2026-11-07", tasks=None, state=None):
        if tasks is None:
            tasks = "# Work queue\n\n## Tasks\n\n" + HEADER + "\n" + SEPARATOR + "\n"
            tasks += "\n".join(rows if rows is not None else [row()]) + "\n\n## Backlog\n\nH01\n"
        if state is None:
            state = (f"Active task: {active}\nLast updated: {updated}\nBranch: chore/codex-harness\n"
                     "Last green commit: UNKNOWN\n\n## Resume notes\nRead TASKS.md.\n")
        (self.folder / "TASKS.md").write_text(tasks, encoding="utf-8")
        (self.folder / "STATE.md").write_text(state, encoding="utf-8")

    def assert_invalid(self, fragment):
        errors = validate(self.root)
        self.assertTrue(errors, "Fixture should be rejected")
        self.assertIn(fragment, "\n".join(errors))
        self.assertTrue(all("docs/codex/" in error for error in errors))

    def test_valid_no_active_task(self):
        self.write()
        self.assertEqual(validate(self.root), [])

    def test_valid_codex_and_humans_working_in_parallel(self):
        self.write(rows=[row(status="IN_PROGRESS"), row("F01", "USER-HW", status="IN_PROGRESS"),
                         row("A01", "USER-DATA", status="IN_PROGRESS")], active="H01")
        self.assertEqual(validate(self.root), [])

    def test_valid_human_active_without_codex(self):
        self.write(rows=[row("F01", "USER-HW", status="IN_PROGRESS")])
        self.assertEqual(validate(self.root), [])

    def test_valid_completed_dependencies_and_all_terminal_states(self):
        self.write(rows=[row("H01", status="DONE", evidence="docs/SESSION_LOG.md: fixture checks PASS"),
                         row("S01", depends="H01", status="DONE-SIM", evidence="logs/simulator.txt"),
                         row("F01", "USER-HW", depends="H01, S01", status="DONE-HW", evidence="User supplied run recording")])
        self.assertEqual(validate(self.root), [])

    def test_valid_leap_date(self):
        self.write(updated="2024-02-29")
        self.assertEqual(validate(self.root), [])

    def test_fenced_sample_heading_is_not_tasks(self):
        self.write()
        path = self.folder / "TASKS.md"
        path.write_text("```markdown\n## Tasks\n| Sample |\n```\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(validate(self.root), [])

    def test_missing_tasks_heading(self):
        self.write(tasks=HEADER + "\n" + SEPARATOR + "\n" + row())
        self.assert_invalid("exactly one 'Tasks' heading")

    def test_duplicate_tasks_heading(self):
        self.write(tasks="## Tasks\n\n## Tasks\n" + HEADER + "\n" + SEPARATOR + "\n" + row())
        self.assert_invalid("found 2")

    def test_table_outside_tasks_section_is_not_accepted(self):
        self.write(tasks="## Tasks\nNo tasks yet.\n\n## Backlog\n" + HEADER + "\n" + SEPARATOR + "\n" + row())
        self.assert_invalid("missing Tasks table")

    def test_wrong_header(self):
        self.write(tasks="## Tasks\n" + HEADER.replace("Who", "Owner") + "\n" + SEPARATOR + "\n" + row())
        self.assert_invalid("header must be")

    def test_missing_or_invalid_separator(self):
        for separator in ("", "|x|x|x|x|x|x|x|"):
            with self.subTest(separator=separator):
                self.write(tasks="## Tasks\n" + HEADER + ("\n" + separator if separator else ""))
                self.assert_invalid("separator")

    def test_missing_or_extra_columns_and_embedded_pipes(self):
        for malformed in (row().rsplit("|", 2)[0] + " |", row().replace("Focused output", "one | two"),
                          row().replace("Focused output", r"one \| two"),
                          row().replace("Focused output", "`one | two`")):
            with self.subTest(row=malformed):
                self.write(rows=[malformed])
                self.assert_invalid("expected 7 columns")

    def test_missing_row_delimiter(self):
        self.write(rows=[row().rstrip("|")])
        self.assert_invalid("row must start and end")

    def test_second_table_under_tasks(self):
        self.write(tasks="## Tasks\n" + HEADER + "\n" + SEPARATOR + "\n" + row() +
                   "\n\n" + HEADER + "\n" + SEPARATOR + "\n" + row("H02"))
        self.assert_invalid("only one contiguous table")

    def test_empty_task_table(self):
        self.write(rows=[])
        self.assert_invalid("at least one valid task ID")

    def test_bad_and_duplicate_ids(self):
        for identifier in ("D-01", "D01", "H1", "H001", "h01", "H٠١"):
            with self.subTest(identifier=identifier):
                self.write(rows=[row(identifier)])
                self.assert_invalid("ID must match")
        self.write(rows=[row(), row()])
        self.assert_invalid("duplicate ID")

    def test_invalid_who_and_status(self):
        self.write(rows=[row(who="BOT", status="PASS")])
        self.assert_invalid("invalid Who")
        self.assert_invalid("invalid Status")

    def test_missing_title_and_acceptance(self):
        self.write(rows=[row().replace("Focused output", "").replace("Run documented checks", "")])
        self.assert_invalid("Task and Acceptance must be nonempty")

    def test_dependency_format(self):
        for depends in ("", "H02; H03", "-, H02", "H02,", "H02,H02"):
            with self.subTest(depends=depends):
                self.write(rows=[row(depends=depends), row("H02"), row("H03")])
                self.assert_invalid("dependency" if depends == "H02,H02" else "Depends must be")

    def test_unknown_and_self_dependencies(self):
        self.write(rows=[row(depends="H01, H02")])
        self.assert_invalid("cannot depend on itself")
        self.assert_invalid("does not exist")

    def test_dependency_cycle(self):
        self.write(rows=[row("H01", depends="H02"), row("H02", depends="H03"), row("H03", depends="H01")])
        self.assert_invalid("dependency cycle: H01 -> H02 -> H03 -> H01")

    def test_terminal_evidence_placeholders(self):
        for status in ("DONE", "DONE-SIM", "DONE-HW"):
            for evidence in ("", "-", "TBD", "TODO: attach log", "N/A", "...", "<evidence>", "`pending`", "chưa có", "N/A: not measured", "???", "TBC", "not available"):
                with self.subTest(status=status, evidence=evidence):
                    self.write(rows=[row(status=status, evidence=evidence)])
                    self.assert_invalid("requires non-placeholder Evidence")

    def test_completed_task_has_unfinished_dependency(self):
        for status in ("TODO", "IN_PROGRESS", "BLOCKED"):
            with self.subTest(status=status):
                self.write(rows=[row(status=status), row("H02", depends="H01", status="DONE", evidence="log.md")],
                           active="H01" if status == "IN_PROGRESS" else "NONE")
                self.assert_invalid("completed task depends on unfinished H01")

    def test_multiple_codex_tasks_in_progress(self):
        self.write(rows=[row(status="IN_PROGRESS"), row("H02", status="IN_PROGRESS")], active="H01")
        self.assert_invalid("at most one CODEX")

    def test_active_missing_task(self):
        self.write(active="V99")
        self.assert_invalid("Active task 'V99' does not exist")

    def test_active_must_be_codex_in_progress(self):
        for who, status in (("USER-HW", "IN_PROGRESS"), ("CODEX", "TODO"), ("CODEX", "BLOCKED")):
            with self.subTest(who=who, status=status):
                self.write(rows=[row(who=who, status=status)], active="H01")
                self.assert_invalid("must be a CODEX task IN_PROGRESS")
                self.assert_invalid("must be NONE")

    def test_active_none_mismatch(self):
        self.write(rows=[row(status="IN_PROGRESS")])
        self.assert_invalid("must match the single CODEX task IN_PROGRESS")

    def test_active_wrong_existing_task(self):
        self.write(rows=[row(status="IN_PROGRESS"), row("H02")], active="H02")
        self.assert_invalid("must match the single CODEX task IN_PROGRESS")

    def test_invalid_dates(self):
        for updated in ("2026-2-01", "2026-02-29", "2026-13-01", "2026-11-31", "0000-01-01", "20261107", "tomorrow"):
            with self.subTest(updated=updated):
                self.write(updated=updated)
                self.assert_invalid("valid calendar date in YYYY-MM-DD")

    def test_state_fields_must_lead_document_in_order(self):
        self.write(state="# State\nActive task: NONE\nLast updated: 2026-11-07\nBranch: task\nLast green commit: UNKNOWN\n")
        self.assert_invalid("in the first four lines")

    def test_missing_or_unreadable_documents(self):
        self.assert_invalid("cannot read file")
        self.write()
        (self.folder / "STATE.md").write_bytes(b"\xff\xfe\xfd")
        self.assert_invalid("cannot read file")

    def test_cli_success_and_failure_from_another_directory(self):
        self.write()
        command = [sys.executable, str(ROOT / "scripts" / "check_codex_state.py"), "--root", str(self.root)]
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("evidence content and hardware are not verified", result.stdout)
        self.write(active="H99")
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/codex/STATE.md:1", result.stdout)


if __name__ == "__main__":
    unittest.main()

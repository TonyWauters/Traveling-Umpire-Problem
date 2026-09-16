from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_results
import validate_legacy
from validate_submission import SubmissionError, validate_solution


class LegacySolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.solutions = validate_legacy.legacy_solutions()

    def test_all_published_downloads_are_restored_and_validated(self) -> None:
        with (ROOT / "results" / "legacy-results.csv").open(newline="", encoding="utf-8") as handle:
            rows = [row for row in csv.DictReader(handle) if row["kind"] == "upper_bound" and row["artifact_url"]]
        expected = {
            "solutions/legacy/" + row["artifact_url"].removeprefix(validate_legacy.ARTIFACT_BASE): int(row["value"])
            for row in rows
        }
        self.assertEqual(92, len(expected))
        self.assertEqual(expected, {row["solution"]: row["cost"] for row in self.solutions})

    def test_restoration_adds_links_without_changing_results_or_ledger(self) -> None:
        with patch("update_results.submission_files", return_value=[]), patch("update_results.legacy_solutions", return_value=[]):
            before, ledger_before = update_results.build()
        with patch("update_results.submission_files", return_value=[]), patch("update_results.legacy_solutions", return_value=self.solutions):
            after, ledger_after = update_results.build()
        self.assertEqual(ledger_before, ledger_after)
        self.assertEqual([], ledger_after)
        self.assertEqual(len(before), len(after))
        changed_links = 0
        for old, new in zip(before, after):
            self.assertEqual(
                {key: value for key, value in old.items() if key != "solution"},
                {key: value for key, value in new.items() if key != "solution"},
            )
            if old["solution"]:
                self.assertEqual(old["solution"], new["solution"])
            elif new["solution"]:
                changed_links += 1
                self.assertTrue((ROOT / new["solution"]).is_file())
        self.assertEqual(65, changed_links)

    def test_equal_cost_artifact_preserves_historical_attribution(self) -> None:
        with patch("update_results.submission_files", return_value=[]), patch("update_results.legacy_solutions", return_value=self.solutions):
            best, _ = update_results.build()
        row = next(row for row in best if (row["instance"], row["q1"], row["q2"]) == ("umps14", "7", "3"))
        self.assertEqual("Wauters et al.", row["upper_bound_originator"])
        self.assertEqual("2013-11-05", row["upper_bound_date"])
        self.assertEqual("solutions/legacy/14/umps14_7_3.txt", row["solution"])

    def test_improved_community_submission_takes_precedence(self) -> None:
        submission = {
            "instance": "umps16", "q1": 8, "q2": 3, "cost": 178929,
            "authors": ["Example Author"], "submitted": "2026-09-16",
            "solution": "submissions/example/umps16_8_3.txt",
        }
        with (
            patch("update_results.legacy_solutions", return_value=self.solutions),
            patch("update_results.submission_files", return_value=[Path(submission["solution"])]),
            patch("update_results.validate_submission", return_value=submission),
        ):
            best, ledger = update_results.build()
        row = next(row for row in best if (row["instance"], row["q1"], row["q2"]) == ("umps16", "8", "3"))
        self.assertEqual("178929", row["upper_bound"])
        self.assertEqual("Example Author", row["upper_bound_originator"])
        self.assertEqual(submission["solution"], row["solution"])
        self.assertEqual(1, len(ledger))
        self.assertEqual(submission["solution"], ledger[0]["solution"])

    def test_wrong_historical_cost_blocks_generation(self) -> None:
        with patch("validate_legacy.validate_solution", return_value=0):
            with self.assertRaisesRegex(SubmissionError, "differs from historical cost"):
                update_results.build()

    def test_invalid_published_solution_blocks_generation(self) -> None:
        with patch("validate_legacy.validate_solution", side_effect=SubmissionError("Solution is infeasible!")):
            with self.assertRaisesRegex(SubmissionError, r"solutions/legacy/14/.*infeasible"):
                update_results.build()

    def test_infeasible_temporary_file_is_retained_but_not_published(self) -> None:
        path = ROOT / "solutions" / "legacy" / "14" / "umps12_6_3.txt.temp"
        with self.assertRaisesRegex(SubmissionError, "infeasible"):
            validate_solution(path, "umps12", 6, 3)
        self.assertFalse(any(row["solution"].endswith(".temp") for row in self.solutions))


if __name__ == "__main__":
    unittest.main()

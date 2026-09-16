from __future__ import annotations

import csv
import re
import subprocess
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_matrix(text: str, name: str, rows: int) -> list[list[int]]:
    match = re.search(rf"\b{name}\s*=\s*\[(.*?)\]\s*;", text, re.DOTALL)
    if not match:
        raise AssertionError(f"missing {name}")
    parsed = []
    for row in re.findall(r"\[([^\]]+)\]", match.group(1)):
        parsed.append([int(value) for value in row.split()])
    if len(parsed) != rows:
        raise AssertionError(f"{name} has {len(parsed)} rows, expected {rows}")
    return parsed


class BenchmarkDataTests(unittest.TestCase):
    def test_instances_are_complete_double_round_robins(self) -> None:
        instance_files = sorted((ROOT / "instances").glob("umps*.txt"))
        self.assertEqual(30, len(instance_files))
        for path in instance_files:
            with self.subTest(instance=path.stem):
                text = path.read_text()
                n_teams = int(re.search(r"\bnTeams\s*=\s*(\d+)\s*;", text).group(1))
                distances = parse_matrix(text, "dist", n_teams)
                opponents = parse_matrix(text, "opponents", 2 * n_teams - 2)
                self.assertTrue(all(len(row) == n_teams for row in distances))
                self.assertTrue(all(len(row) == n_teams for row in opponents))
                for i in range(n_teams):
                    self.assertEqual(0, distances[i][i])
                    for j in range(n_teams):
                        self.assertGreaterEqual(distances[i][j], 0)
                        self.assertEqual(distances[i][j], distances[j][i])
                max_rounding_violation = max(
                    distances[i][k] - distances[i][j] - distances[j][k]
                    for i in range(n_teams)
                    for j in range(n_teams)
                    for k in range(n_teams)
                )
                self.assertLessEqual(max_rounding_violation, 6)
                meetings = {(home, away): 0 for home in range(1, n_teams + 1) for away in range(1, n_teams + 1) if home != away}
                for round_row in opponents:
                    for team, opponent in enumerate(round_row, 1):
                        self.assertNotEqual(0, opponent)
                        self.assertNotEqual(team, abs(opponent))
                        reciprocal = -team if opponent > 0 else team
                        self.assertEqual(reciprocal, round_row[abs(opponent) - 1])
                        if opponent > 0:
                            meetings[(team, opponent)] += 1
                self.assertTrue(all(count == 1 for count in meetings.values()))

    def test_legacy_parameters_fit_validator_windows(self) -> None:
        with (ROOT / "results" / "legacy-best-known.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            n_teams = int(re.match(r"umps(\d+)", row["instance"]).group(1))
            n_rounds = 2 * n_teams - 2
            self.assertIn(int(row["q1"]), range(1, n_rounds + 1))
            self.assertIn(int(row["q2"]), range(1, n_rounds + 1))

    def test_legacy_result_inventory(self) -> None:
        expected_counts = {
            "legacy-best-known.csv": 92,
            "legacy-history.csv": 289,
            "legacy-groups.csv": 17,
            "legacy-results.csv": 506,
        }
        known_instances = {path.stem for path in (ROOT / "instances").glob("umps*.txt")}
        for filename, expected in expected_counts.items():
            with self.subTest(filename=filename):
                with (ROOT / "results" / filename).open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(expected, len(rows))
                self.assertTrue(all(row["instance"] in known_instances for row in rows if "instance" in row))

    def test_best_known_bounds_are_consistent(self) -> None:
        with (ROOT / "results" / "best-known.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        keys = [(row["instance"], row["q1"], row["q2"]) for row in rows]
        self.assertEqual(len(keys), len(set(keys)))
        for row in rows:
            if row["lower_bound"] and row["upper_bound"]:
                self.assertLessEqual(Decimal(row["lower_bound"]), Decimal(row["upper_bound"]))
            if row["status"] == "optimal":
                self.assertEqual(Decimal(row["lower_bound"]), Decimal(row["upper_bound"]))

    def test_validator_on_reference_solution(self) -> None:
        completed = subprocess.run(
            [
                "java", "-jar", str(ROOT / "validator" / "validator.jar"),
                str(ROOT / "instances" / "umps4.txt"), "2", "1",
                str(ROOT / "tests" / "fixtures" / "umps4_2_1.txt"),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual("5176", completed.stdout.strip())


if __name__ == "__main__":
    unittest.main()

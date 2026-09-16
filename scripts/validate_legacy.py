#!/usr/bin/env python3
"""Validate restored solution downloads against their published legacy costs."""

from __future__ import annotations

import csv
import sys
from typing import Any

from validate_submission import ROOT, SubmissionError, validate_solution


LEGACY_RESULTS = ROOT / "results" / "legacy-results.csv"
ARTIFACT_BASE = "https://benchmark.gent.cs.kuleuven.be/tup/media/solutions/"


def legacy_solutions() -> list[dict[str, Any]]:
    """Return validated artifacts with provenance in the immutable result snapshot.

    Missing downloads are allowed so that partial restorations remain possible.
    Unreferenced files, archives, and temporary solver output are kept for
    historical purposes but do not contribute to the maintained result table.
    """
    with LEGACY_RESULTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    solutions = []
    for row in rows:
        if row["kind"] != "upper_bound" or not row["artifact_url"]:
            continue
        filename = f"{row['instance']}_{row['q1']}_{row['q2']}.txt"
        artifact = f"{row['group_id']}/{filename}"
        if row["artifact_url"] != ARTIFACT_BASE + artifact:
            raise SubmissionError(f"unexpected legacy artifact URL: {row['artifact_url']}")
        path = ROOT / "solutions" / "legacy" / artifact
        if not path.is_file():
            continue
        try:
            cost = validate_solution(path, row["instance"], int(row["q1"]), int(row["q2"]))
            if cost != int(row["value"]):
                raise SubmissionError(f"validated cost {cost} differs from historical cost {row['value']}")
        except SubmissionError as exc:
            raise SubmissionError(f"{path.relative_to(ROOT)}: {exc}") from exc
        solutions.append({
            "instance": row["instance"],
            "q1": int(row["q1"]),
            "q2": int(row["q2"]),
            "cost": cost,
            "group_id": row["group_id"],
            "solution": path.relative_to(ROOT).as_posix(),
        })
    return solutions


def main() -> int:
    try:
        solutions = legacy_solutions()
    except SubmissionError as exc:
        print(f"Legacy validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {len(solutions)} restored legacy solution(s); all costs match the historical records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

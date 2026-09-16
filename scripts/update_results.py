#!/usr/bin/env python3
"""Rebuild the submission ledger, best-known CSV, and Markdown results table."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

from validate_submission import ROOT, SubmissionError, submission_files, validate_submission


RESULTS = ROOT / "results"
LEGACY_BEST = RESULTS / "legacy-best-known.csv"
BEST = RESULTS / "best-known.csv"
LEDGER = RESULTS / "submissions.csv"
README = RESULTS / "README.md"
BEST_FIELDS = [
    "instance",
    "q1",
    "q2",
    "lower_bound",
    "lower_bound_originator",
    "lower_bound_date",
    "upper_bound",
    "upper_bound_originator",
    "upper_bound_date",
    "status",
    "gap_percent",
    "solution",
]
LEDGER_FIELDS = [
    "instance",
    "q1",
    "q2",
    "cost",
    "authors",
    "algorithm",
    "institution",
    "submitted",
    "publication",
    "notes",
    "contributor",
    "solution",
]


def read_legacy() -> list[dict[str, str]]:
    with LEGACY_BEST.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != BEST_FIELDS:
            raise SubmissionError(f"unexpected columns in {LEGACY_BEST.relative_to(ROOT)}")
        return [dict(row) for row in reader]


def csv_text(rows: list[dict[str, object]], fields: list[str]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _gap(lower: str, upper: int) -> str:
    if not lower:
        return ""
    gap = (Decimal(upper) - Decimal(lower)) / Decimal(upper) * Decimal(100)
    return f"{gap:.2f}"


def build() -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    best = deepcopy(read_legacy())
    by_key = {(row["instance"], int(row["q1"]), int(row["q2"])): row for row in best}
    ledger: list[dict[str, object]] = []

    for path in submission_files():
        result = validate_submission(path)
        ledger_row = {field: result.get(field, "") for field in LEDGER_FIELDS}
        ledger_row["authors"] = "; ".join(result["authors"])
        ledger.append(ledger_row)

        key = (result["instance"], result["q1"], result["q2"])
        row = by_key.get(key)
        if row is None:
            row = {field: "" for field in BEST_FIELDS}
            row.update(
                {"instance": key[0], "q1": str(key[1]), "q2": str(key[2]), "status": "open"}
            )
            best.append(row)
            by_key[key] = row
        if row["status"] == "infeasible":
            raise SubmissionError(f"{key} is recorded as infeasible but has a valid submission")
        if row["lower_bound"] and Decimal(result["cost"]) < Decimal(row["lower_bound"]):
            raise SubmissionError(
                f"valid cost {result['cost']} is below recorded lower bound {row['lower_bound']} for {key}"
            )

        existing = int(row["upper_bound"]) if row["upper_bound"] else None
        if existing is None or result["cost"] < existing:
            row["upper_bound"] = str(result["cost"])
            row["upper_bound_originator"] = "; ".join(result["authors"])
            row["upper_bound_date"] = result["submitted"]
            row["solution"] = result["solution"]
            if row["lower_bound"] and Decimal(row["lower_bound"]) == Decimal(result["cost"]):
                row["status"] = "optimal"
                row["gap_percent"] = ""
            else:
                row["status"] = "open"
                row["gap_percent"] = _gap(row["lower_bound"], result["cost"])
        elif result["cost"] == existing and not row["solution"]:
            # Preserve the historical attribution while making an equal-quality artifact available.
            row["solution"] = result["solution"]

    best.sort(key=lambda row: (int(row["instance"][4:].rstrip("ABC")), row["instance"], -int(row["q1"]), -int(row["q2"])))
    ledger.sort(key=lambda row: (str(row["instance"]), int(row["q1"]), int(row["q2"]), str(row["solution"])))
    return best, ledger


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown(best: list[dict[str, str]]) -> str:
    lines = [
        "# Best-known results",
        "",
        "This table is generated from [`legacy-best-known.csv`](legacy-best-known.csv) and validated community submissions. The legacy snapshot was migrated from the benchmark website on 2026-09-15; the dates in the table are the original result dates.",
        "",
        "A decimal lower bound is valid even though every feasible solution has an integer cost. The displayed gap is `(upper bound - lower bound) / upper bound`. Blank cells mean the legacy benchmark did not report that side of the bound.",
        "",
        "Machine-readable data:",
        "",
        "- [`best-known.csv`](best-known.csv): current generated overview",
        "- [`submissions.csv`](submissions.csv): all repository submissions that pass the validator",
        "- [`legacy-best-known.csv`](legacy-best-known.csv): immutable migrated baseline",
        "- [`legacy-history.csv`](legacy-history.csv): up to three improving bounds/solutions shown by the old overview",
        "- [`legacy-groups.csv`](legacy-groups.csv): originator, publication, and submission metadata",
        "- [`legacy-results.csv`](legacy-results.csv): all 506 rows shown on the 17 legacy result-group pages",
        "",
        "Historical solution downloads disappeared from the live legacy server. See [`../solutions/legacy/README.md`](../solutions/legacy/README.md) for the placeholder layout used to restore local copies.",
        "",
        "| Instance | q1 | q2 | Lower bound | Upper bound | Status / gap | Lower-bound originator | Upper-bound originator | Solution |",
        "|---|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in best:
        lower = row["lower_bound"] or "—"
        upper = row["upper_bound"] or "—"
        if row["status"] == "optimal":
            status = "optimal"
        elif row["status"] == "infeasible":
            status = "infeasible"
        elif row["gap_percent"]:
            status = f"{row['gap_percent']}%"
        else:
            status = "open"
        lb_by = row["lower_bound_originator"]
        if lb_by and row["lower_bound_date"]:
            lb_by += f" ({row['lower_bound_date']})"
        ub_by = row["upper_bound_originator"]
        if ub_by and row["upper_bound_date"]:
            ub_by += f" ({row['upper_bound_date']})"
        solution = f"[file](../{row['solution']})" if row["solution"] else "—"
        lines.append(
            "| " + " | ".join(
                _escape(value)
                for value in (
                    row["instance"], row["q1"], row["q2"], lower, upper,
                    status, lb_by or "—", ub_by or "—", solution,
                )
            ) + " |"
        )
    lines.extend(
        [
            "",
            "## Updating the table",
            "",
            "Do not edit `best-known.csv`, `submissions.csv`, or this file by hand for a solution submission. Follow [`../CONTRIBUTING.md`](../CONTRIBUTING.md); the post-merge workflow rebuilds them from validated files under `submissions/`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="validate and render without writing")
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    if args.dry_run and args.check:
        parser.error("--dry-run and --check are mutually exclusive")
    try:
        best, ledger = build()
    except SubmissionError as exc:
        print(f"Cannot update results: {exc}", file=sys.stderr)
        return 1
    rendered = {
        BEST: csv_text(best, BEST_FIELDS),
        LEDGER: csv_text(ledger, LEDGER_FIELDS),
        README: markdown(best),
    }
    if args.dry_run:
        print(f"Validated {len(ledger)} submission(s); would publish {len(best)} result rows.")
        return 0
    if args.check:
        stale = [path for path, content in rendered.items() if not path.is_file() or path.read_text() != content]
        if stale:
            print("Generated files are stale: " + ", ".join(str(path.relative_to(ROOT)) for path in stale), file=sys.stderr)
            return 1
        print(f"Generated results are current ({len(best)} rows, {len(ledger)} submissions).")
        return 0
    for path, content in rendered.items():
        path.write_text(content, encoding="utf-8")
    print(f"Published {len(best)} result rows from {len(ledger)} validated submission(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

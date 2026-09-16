#!/usr/bin/env python3
"""Validate TUP solution submissions with the repository's Java validator."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "instances"
SUBMISSIONS = ROOT / "submissions"
VALIDATOR = ROOT / "validator" / "validator.jar"
FILENAME_RE = re.compile(
    r"(?P<instance>umps\d+[A-C]?)_(?P<q1>[1-9]\d*)_(?P<q2>[1-9]\d*)\.txt"
)
CONTRIBUTOR_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
MAX_SOLUTION_BYTES = 2 * 1024 * 1024
MAX_METADATA_BYTES = 64 * 1024


class SubmissionError(ValueError):
    """Raised when a submission is malformed or infeasible."""


def _read_n_teams(instance_path: Path) -> int:
    match = re.search(r"\bnTeams\s*=\s*(\d+)\s*;", instance_path.read_text())
    if not match:
        raise SubmissionError(f"cannot read nTeams from {instance_path}")
    return int(match.group(1))


def _validate_text_field(name: str, value: Any, *, required: bool = False) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise SubmissionError(f"metadata field '{name}' must be a non-empty string")
    value = value.strip()
    if len(value) > 1000 or "\n" in value or "\r" in value:
        raise SubmissionError(f"metadata field '{name}' is too long or contains a newline")
    return value


def load_metadata(solution_path: Path) -> dict[str, Any]:
    metadata_path = solution_path.with_suffix(".json")
    if not metadata_path.is_file():
        raise SubmissionError(f"missing metadata file: {metadata_path.relative_to(ROOT)}")
    if metadata_path.stat().st_size > MAX_METADATA_BYTES:
        raise SubmissionError(f"metadata file is larger than {MAX_METADATA_BYTES} bytes")

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SubmissionError(f"invalid JSON in {metadata_path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(metadata, dict):
        raise SubmissionError("submission metadata must be a JSON object")

    authors = metadata.get("authors")
    if not isinstance(authors, list) or not authors or len(authors) > 20:
        raise SubmissionError("metadata field 'authors' must be a non-empty list")
    normalized_authors = []
    for author in authors:
        normalized_authors.append(_validate_text_field("authors", author, required=True))

    submitted = _validate_text_field("submitted", metadata.get("submitted"), required=True)
    try:
        date.fromisoformat(submitted)
    except ValueError as exc:
        raise SubmissionError("metadata field 'submitted' must use YYYY-MM-DD") from exc

    return {
        "authors": normalized_authors,
        "algorithm": _validate_text_field(
            "algorithm", metadata.get("algorithm"), required=True
        ),
        "institution": _validate_text_field("institution", metadata.get("institution")),
        "submitted": submitted,
        "publication": _validate_text_field("publication", metadata.get("publication")),
        "notes": _validate_text_field("notes", metadata.get("notes")),
    }


def _preflight_solution(solution_path: Path, n_teams: int) -> None:
    if solution_path.stat().st_size > MAX_SOLUTION_BYTES:
        raise SubmissionError(f"solution is larger than {MAX_SOLUTION_BYTES} bytes")
    try:
        lines = solution_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise SubmissionError("solution must be UTF-8 text") from exc
    if not lines or not lines[0].strip():
        raise SubmissionError("solution is empty")

    n_umpires = n_teams // 2
    n_rounds = 2 * n_teams - 2
    if "," in lines[0]:
        tokens = [token.strip() for token in lines[0].rstrip(",").split(",")]
        expected = n_umpires * n_rounds
        if len(tokens) != expected:
            raise SubmissionError(
                f"compact solution has {len(tokens)} assignments; expected {expected}"
            )
        try:
            assignments = [int(token) for token in tokens]
        except ValueError as exc:
            raise SubmissionError("compact solution contains a non-integer assignment") from exc
        expected_umpires = set(range(1, n_umpires + 1))
        for round_index in range(n_rounds):
            start = round_index * n_umpires
            round_assignments = set(assignments[start : start + n_umpires])
            if round_assignments != expected_umpires:
                raise SubmissionError(
                    f"round {round_index + 1} must assign every umpire exactly once"
                )
        return

    schedule_lines = []
    for line in lines:
        if line.strip() == "---":
            break
        if line.strip():
            schedule_lines.append(line)
    if len(schedule_lines) != n_umpires:
        raise SubmissionError(
            f"matrix solution has {len(schedule_lines)} umpire rows; expected {n_umpires}"
        )
    for umpire_index, line in enumerate(schedule_lines, 1):
        tokens = line.split()
        if len(tokens) != n_rounds:
            raise SubmissionError(
                f"umpire row {umpire_index} has {len(tokens)} venues; expected {n_rounds}"
            )
        try:
            venues = [int(token) for token in tokens]
        except ValueError as exc:
            raise SubmissionError(f"umpire row {umpire_index} contains a non-integer") from exc
        if any(venue < 1 or venue > n_teams for venue in venues):
            raise SubmissionError(f"umpire row {umpire_index} contains an invalid venue")


def parse_submission_path(path: Path) -> tuple[str, int, int, str]:
    try:
        relative = path.resolve().relative_to(SUBMISSIONS.resolve())
    except ValueError as exc:
        raise SubmissionError("solutions must be stored below submissions/") from exc
    if len(relative.parts) != 2:
        raise SubmissionError(
            "use submissions/<contributor>/umpsN_q1_q2.txt (one contributor directory)"
        )
    contributor = relative.parts[0]
    if not CONTRIBUTOR_RE.fullmatch(contributor):
        raise SubmissionError(f"invalid contributor directory: {contributor}")
    match = FILENAME_RE.fullmatch(relative.name)
    if not match:
        raise SubmissionError(
            "solution filename must use umpsN_q1_q2.txt, optionally with variant A, B, or C"
        )
    return (
        match.group("instance"),
        int(match.group("q1")),
        int(match.group("q2")),
        contributor,
    )


def validate_solution(solution_path: Path, instance: str, q1: int, q2: int) -> int:
    """Check an assignment and return its cost, independently of submission metadata."""
    solution_path = solution_path.resolve()
    if not solution_path.is_file():
        raise SubmissionError(f"solution does not exist: {solution_path}")
    instance_path = INSTANCES / f"{instance}.txt"
    if not instance_path.is_file():
        raise SubmissionError(f"unknown benchmark instance: {instance}")
    n_teams = _read_n_teams(instance_path)
    n_rounds = 2 * n_teams - 2
    # Some official benchmark rows use q1 = n_umpires + 1. Both parameters are
    # direct window lengths, so the season length is the non-lossy general cap.
    if not 1 <= q1 <= n_rounds:
        raise SubmissionError(f"q1 must be between 1 and {n_rounds} for {instance}")
    if not 1 <= q2 <= n_rounds:
        raise SubmissionError(f"q2 must be between 1 and {n_rounds} for {instance}")

    _preflight_solution(solution_path, n_teams)
    try:
        completed = subprocess.run(
            [
                "java",
                "-jar",
                str(VALIDATOR),
                str(instance_path),
                str(q1),
                str(q2),
                str(solution_path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError as exc:
        raise SubmissionError("Java is required to run validator/validator.jar") from exc
    except subprocess.TimeoutExpired as exc:
        raise SubmissionError("validator timed out after 60 seconds") from exc

    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    if completed.returncode != 0:
        raise SubmissionError(output or f"validator exited with code {completed.returncode}")
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not lines or not re.fullmatch(r"\d+", lines[-1]):
        raise SubmissionError(f"unexpected validator output: {completed.stdout!r}")

    return int(lines[-1])


def validate_submission(solution_path: Path) -> dict[str, Any]:
    solution_path = solution_path.resolve()
    if not solution_path.is_file():
        raise SubmissionError(f"solution does not exist: {solution_path}")
    instance, q1, q2, contributor = parse_submission_path(solution_path)
    metadata = load_metadata(solution_path)
    cost = validate_solution(solution_path, instance, q1, q2)
    return {
        "instance": instance,
        "q1": q1,
        "q2": q2,
        "cost": cost,
        "contributor": contributor,
        "solution": solution_path.relative_to(ROOT).as_posix(),
        **metadata,
    }


def submission_files() -> list[Path]:
    return sorted(
        path
        for path in SUBMISSIONS.glob("*/*.txt")
        if path.is_file() and FILENAME_RE.fullmatch(path.name)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="solution files to validate")
    parser.add_argument("--all", action="store_true", help="validate every submission")
    args = parser.parse_args()
    if args.all and args.paths:
        parser.error("use either explicit paths or --all")
    paths = submission_files() if args.all else args.paths
    if not paths:
        print("No solution submissions found.")
        return 0

    failed = False
    for path in paths:
        try:
            result = validate_submission(path)
            print(
                f"VALID {result['solution']}: cost={result['cost']} "
                f"({result['instance']}, q1={result['q1']}, q2={result['q2']})"
            )
        except SubmissionError as exc:
            failed = True
            display = path if path.is_absolute() else path.as_posix()
            print(f"INVALID {display}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

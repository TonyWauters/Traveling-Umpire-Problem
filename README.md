# Traveling Umpire Problem benchmark

This repository is the new, version-controlled home of the Traveling Umpire Problem (TUP) benchmark. It replaces the [legacy automated benchmark](https://benchmark.gent.cs.kuleuven.be/tup/en/) with downloadable instances, machine-readable results, validation tooling, publications, and a pull-request submission process.

## At a glance

- **30 benchmark instances**, from 4 to 32 teams
- **historical result records** 
- A **Java solution validator** and repository integrity tests
- **Automatic pull-request validation** and post-merge result publication

| Looking for… | Go to |
|---|---|
| Benchmark files and their format | [`instances/`](instances/) |
| Best lower/upper bounds and optima | [`results/README.md`](results/README.md) |
| Machine-readable current results | [`results/best-known.csv`](results/best-known.csv) |
| Publications and BibTeX | [`publications/`](publications/) |
| Validator instructions | [`validator/README.md`](validator/README.md) |
| Submitting a solution | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Problem definition

Let a tournament have an even number `N = 2n` of teams. Every pair of teams plays twice—once at each home venue—in a double round robin of `2N - 2 = 4n - 2` rounds. Every team plays once per round, so each round contains `n` games and requires `n` umpires. Distances between venues are given by a symmetric distance matrix. The legacy problem statement describes the distances as satisfying the triangle inequality; some integer benchmark matrices have rounding violations of at most six distance units, so the files must be used as supplied.

The task is to assign every game to an umpire. Each umpire handles exactly one game per round. The objective is to minimize the total distance traveled by all umpires between the venues of games in consecutive rounds; there is no additional start or end depot cost.

A feasible assignment satisfies all of the following:

1. Every game is assigned to exactly one umpire.
2. Every umpire handles exactly one game in every round.
3. Every umpire visits every team's home venue at least once.
4. An umpire visits the same home venue at most once in any `q1` consecutive rounds.
5. An umpire sees the same team, as either home or away team, at most once in any `q2` consecutive rounds.

The original formulation expresses the usual windows as `q1 = n - d1` and `q2 = floor(n / 2) - d2`. Smaller `d1` and `d2` make the constraints tighter. The legacy benchmark also includes `q1 = n + 1` configurations for `umps12` and the `umps14` family, so this repository and the validator identify configurations directly by their `q1` and `q2` values rather than inferring them from `d1` and `d2`.

The TUP abstracts the central travel and fairness considerations in Major League Baseball umpire scheduling, much as the Traveling Tournament Problem abstracts team travel.

## Repository contents

```text
instances/                 Canonical tournament and distance data
results/                   Current results and the complete migrated history
publications/              Chronological bibliography and BibTeX
solutions/legacy/          Placeholder for legacy solution files no longer online
submissions/<contributor>/ Community solution and metadata pairs
validator/                 Original Java validator
scripts/                   Validation and deterministic result-generation tools
tests/                     Data-integrity and validator tests
.github/workflows/         Pull-request validation and result publication
```

## Validate a solution locally

Java 8 or newer is sufficient for the bundled validator:

```bash
java -jar validator/validator.jar instances/umps14.txt 7 3 path/to/umps14_7_3.txt
```

A valid solution prints its integer travel cost. An invalid one exits with a nonzero status and prints an error or `Solution is infeasible!`. See [`validator/README.md`](validator/README.md) for both supported solution formats.

## Submit a result

Fork the repository and open a pull request containing:

```text
submissions/<your-handle>/umpsN_q1_q2.txt
submissions/<your-handle>/umpsN_q1_q2.json
```

The read-only pull-request workflow checks the file structure, metadata, feasibility, and cost using the bundled validator. After an accepted pull request is merged, a second workflow records the submission and updates the best-known upper bound only if it improves the existing value. Equal or non-improving valid submissions remain in [`results/submissions.csv`](results/submissions.csv). Full instructions and a metadata example are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

Repository maintainers should make the **Validate benchmark** check required in branch protection and grant GitHub Actions read/write workflow permissions so the post-merge publisher can commit generated result files. If a ruleset blocks direct bot commits, allow the GitHub Actions bot to bypass that rule only for this generated-results workflow, or have a maintainer run `python3 scripts/update_results.py` and commit the three generated files after each merge.

## Resources, history, and attribution

The problem was introduced by Michael Trick and Hakan Yildiz. The legacy website was developed and maintained by Túlio A. M. Toffolo and Tony Wauters at KU Leuven.

## Solvers

The open-source branch-and-bound solver implemented in Java can be found at: [branch-and-bound and decomposition solver](https://github.com/tuliotoffolo/tup).

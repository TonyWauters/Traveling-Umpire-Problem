# Contributing

Contributions of improved solutions, stronger lower bounds, missing historical artifacts, publications, and corrections are welcome through pull requests.

## Submit a solution

1. Fork the repository and create a branch.
2. Choose a contributor directory containing only letters, digits, `.`, `_`, or `-`.
3. Add the solution as `submissions/<contributor>/umpsN_q1_q2.txt`.
4. Add metadata beside it as `submissions/<contributor>/umpsN_q1_q2.json`.
5. Run the local checks and open a pull request.

For example, a solution to `umps16` with `q1 = 8` and `q2 = 3` submitted by `ada-lovelace` uses:

```text
submissions/ada-lovelace/umps16_8_3.txt
submissions/ada-lovelace/umps16_8_3.json
```

The filename contains the direct constraint-window lengths, not `d1` and `d2`. For an existing benchmark configuration, copy `q1` and `q2` exactly from [`results/best-known.csv`](results/best-known.csv).

The metadata file must be a JSON object:

```json
{
  "authors": ["Ada Lovelace", "Grace Hopper"],
  "algorithm": "Example decomposition heuristic",
  "institution": "Example University",
  "submitted": "2026-09-15",
  "publication": "https://doi.org/10.example/example",
  "notes": "Optional short reproducibility note"
}
```

`authors`, `algorithm`, and `submitted` are required. The other fields may be omitted or set to an empty string. Use the scientific authors' names in `authors`; the directory name is only the GitHub contributor identifier.

Run:

```bash
python3 scripts/validate_submission.py submissions/ada-lovelace/umps16_8_3.txt
python3 scripts/update_results.py --dry-run
python3 -m unittest discover -s tests -v
```

The first command checks metadata and invokes the Java validator. The second confirms that the submission can be incorporated without contradicting a known lower bound or infeasibility result. The test suite also checks all instance and result data.

Do not edit `results/best-known.csv`, `results/submissions.csv`, or `results/README.md` for a normal solution submission. They are generated after merge. A valid submission is always recorded in `results/submissions.csv`; it becomes the displayed upper bound only when it is strictly better, or supplies an artifact for an equal bound whose historical file is missing.

Maintainers should require the **Validate benchmark** check before merging. The post-merge workflow needs `contents: write` permission under the repository's Actions settings and, where branch rules require it, narrowly scoped permission to push its generated-results commit.

## Submit a lower bound or infeasibility proof

The Java tool validates feasible solutions but cannot certify lower bounds. Open a pull request that edits `results/legacy-best-known.csv` only if correcting migrated history; for a new bound, open an issue first and include the full citation, method, value, configuration, computational conditions, and a durable proof or publication link. A maintainer can then add a reviewed bound to the maintained baseline or extend the data model.

## Restore legacy solution files

The old site's solution URLs now return 404. If you have the original archives, follow [`solutions/legacy/README.md`](solutions/legacy/README.md). Please preserve the bytes and legacy names, and mention the group ID and source in the pull request.

## Add a publication

Add the formatted reference to [`publications/README.md`](publications/README.md) and a BibTeX entry to [`publications/references.bib`](publications/references.bib). Prefer a DOI or a stable institutional repository URL. The publication must directly study TUP or report TUP benchmark results.

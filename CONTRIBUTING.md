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

Maintainers should require the **validate** job from **Validate benchmark** before merging. After a submission is merged, **Publish accepted results** rebuilds the generated files and opens or updates a pull request from `automation/update-results` to `main`. A maintainer reviews and merges that results pull request after validation passes. The workflow does not push directly to protected `main`.

In **Settings → Actions → General → Workflow permissions**, enable **Allow GitHub Actions to create and approve pull requests**. The publishing workflow declares `contents: write` and `pull-requests: write` to maintain the results pull request, plus `actions: write` to explicitly dispatch **Validate benchmark** on its branch using the built-in `GITHUB_TOKEN`. This runs the required `validate` check without a personal access token or branch-protection bypass.

To recover a failed publication, first merge the workflow fix, then select **Actions → Publish accepted results → Run workflow** on `main`. This rebuilds results from all currently accepted submissions. If the generated files are already current, no results pull request is needed.

## Submit a lower bound or infeasibility proof

The Java tool validates feasible solutions but cannot certify lower bounds. Open a pull request that edits `results/legacy-best-known.csv` only if correcting migrated history; for a new bound, open an issue first and include the full citation, method, value, configuration, computational conditions, and a durable proof or publication link. A maintainer can then add a reviewed bound to the maintained baseline or extend the data model.

## Restore legacy solution files

The restored collection and its validation notes are described in [`solutions/legacy/README.md`](solutions/legacy/README.md). For additional original files or archives, preserve the bytes and legacy names, and mention the directory/group ID and source in the pull request.

Run `python3 scripts/validate_legacy.py` to check restored downloads against the costs in `results/legacy-results.csv`, then `python3 scripts/update_results.py` to regenerate their links. Include the generated result changes in a historical-restoration pull request and verify them with `python3 scripts/update_results.py --check`. Original legacy CSVs retain their migrated values and source URLs; restored files are linked automatically only when they match a published download and the displayed upper-bound cost. Legacy artifacts do not need community-submission JSON metadata.

## Add a publication

Add the formatted reference to [`publications/README.md`](publications/README.md) and a BibTeX entry to [`publications/references.bib`](publications/references.bib). Prefer a DOI or a stable institutional repository URL. The publication must directly study TUP or report TUP benchmark results.

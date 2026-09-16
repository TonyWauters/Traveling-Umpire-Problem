# Restored legacy solutions

This directory preserves the supplied legacy solution files, ZIP archives, and temporary solver output under their original directory IDs and filenames. The individual files referenced by the migrated result tables are now available locally, including:

```text
solutions/legacy/14/umps16_8_3.txt
solutions/legacy/52/umps30_5_5.txt
```

The restoration contains **259 `.txt` files, 15 ZIP archives, and 6 `.txt.temp` files**. All supplied file bytes are retained, including duplicate copies and diagnostic text after `---`. Archive members can have different filenames or line endings from the standalone downloads; the ZIPs are preserved without repacking or replacing the standalone files.

## Published result files

All **92 downloadable solutions** referenced by [`legacy-results.csv`](../../results/legacy-results.csv) have been restored. Each passes the bundled Java validator and has exactly the cost recorded in that CSV.

| Directory | Historical result group | Referenced files |
|---|---|---:|
| [`14/`](14/) | Toffolo2015 | 58 |
| [`36/`](36/) | Wauters2013 | 1 |
| [`38/`](38/) | Toffolo2015b | 1 |
| [`46/`](46/) | DeOliveira2014 | 1 |
| [`52/`](52/) | DecompHeuristic | 31 |

The original download URLs, group metadata, and result history remain unchanged in [`legacy-results.csv`](../../results/legacy-results.csv), [`legacy-groups.csv`](../../results/legacy-groups.csv), and [`legacy-history.csv`](../../results/legacy-history.csv). A local path corresponds to the suffix after `/media/solutions/` in its original URL. Directory IDs alone do not establish a relationship to a result group: the legacy site had separate namespaces for bound and solution groups.

The result generator validates these referenced files and fills a missing `solution` field only when the instance, `q1`, `q2`, and cost match the displayed upper bound. It preserves the bound's original originator and date, even when the equal-cost artifact belongs to a later group. Improved community submissions still take precedence. This restoration adds **64 historical file links** to the current table without changing any bound, gap, date, or attribution. The existing community solution link remains in place.

## Other preserved files

Directories `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13`, `15`, `37`, and `48` contain additional or duplicate copies without corresponding download URLs in the migrated result rows. They remain available as historical artifacts, but are not assigned authors or promoted into the results by guessing their provenance.

All 259 standalone `.txt` files pass the validator. Of the six `.txt.temp` files, five pass; **[`14/umps12_6_3.txt.temp`](14/umps12_6_3.txt.temp) is infeasible**. Temporary files and archive-only members are excluded from result generation. Keeping an original archive or temporary file does not certify every assignment it contains.

Some best-known bounds still have no matching restored file, including the small-instance optima and `umps16_8_2` / `umps16C_8_2`. Their solution cells remain blank rather than linking a more expensive assignment.

## Validate and regenerate

From the repository root:

```bash
python3 scripts/validate_legacy.py
python3 scripts/update_results.py
python3 scripts/update_results.py --check
python3 -m unittest discover -s tests -v
```

`validate_legacy.py` checks restored files with published download URLs. `update_results.py` performs the same checks before regenerating the maintained CSV and Markdown tables; the pull-request workflow runs it with `--dry-run`. Legacy artifacts do not enter the community submission ledger and do not need new JSON metadata. For future restorations, preserve the original bytes and names and identify the source in the pull request.

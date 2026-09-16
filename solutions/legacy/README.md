# Legacy solution-file placeholder

The old benchmark result tables refer to solution files below URLs such as:

```text
https://benchmark.gent.cs.kuleuven.be/tup/media/solutions/14/umps16_8_3.txt
```

Those individual files and the downloadable group archives now return 404, so this directory intentionally contains placeholders rather than guessed reconstructions.

When original files are available, store them without modification as:

```text
solutions/legacy/<group-id>/<original-filename>
```

For example:

```text
solutions/legacy/14/umps16_8_3.txt
solutions/legacy/52/umps30_5_5.txt
```

The original URLs and group IDs are preserved in [`../../results/legacy-history.csv`](../../results/legacy-history.csv), [`../../results/legacy-groups.csv`](../../results/legacy-groups.csv), and [`../../results/legacy-results.csv`](../../results/legacy-results.csv). After restoring files, validate each one and update the matching `solution` field in the maintained result data through a reviewed pull request.

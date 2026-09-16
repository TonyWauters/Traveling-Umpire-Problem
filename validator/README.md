# TUP solution validator

The bundled `validator.jar` is the Java validator distributed by the legacy TUP benchmark. Java 8 or newer is required.

```text
java -jar validator.jar <instance> <q1> <q2> <solution>
```

From the repository root:

```bash
java -jar validator/validator.jar instances/umps14.txt 7 3 path/to/umps14_7_3.txt
```

Success prints the integer total travel distance. Invalid input or an infeasible assignment produces a nonzero exit code and prints an error or `Solution is infeasible!`.

## Recommended compact solution format

Put a single comma-separated sequence on the first line. There is one number per game, ordered first by round and then by increasing home-team number within that round. Each number is the 1-based ID of the umpire assigned to that game.

For `N` teams there are `N / 2` games per round, `2N - 2` rounds, and therefore `N(N - 1)` entries. Within every round, the IDs `1` through `N / 2` must each occur once. A trailing comma is accepted.

The six-round `umps4` reference solution begins:

```text
2,1,1,2,2,1,2,1,1,2,2,1
```

## Additional solution print after `---`

The validator ignores diagnostic text written after `---` by the original solver's solution writer.

## Automated wrapper

[`../scripts/validate_submission.py`](../scripts/validate_submission.py) adds filename, metadata, size, and structural checks before invoking this JAR. Use it for files placed under `submissions/`; see [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

The original short instructions remain in [`readme.txt`](readme.txt).

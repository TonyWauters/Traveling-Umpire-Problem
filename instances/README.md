# Benchmark instances

This directory contains the 30 instances used by the legacy TUP benchmark.

| Teams | Instances | Umpires | Rounds |
|---:|---|---:|---:|
| 4 | `umps4` | 2 | 6 |
| 6 | `umps6`, `umps6A`, `umps6B`, `umps6C` | 3 | 10 |
| 8 | `umps8`, `umps8A`, `umps8B`, `umps8C` | 4 | 14 |
| 10 | `umps10`, `umps10A`, `umps10B`, `umps10C` | 5 | 18 |
| 12 | `umps12` | 6 | 22 |
| 14 | `umps14`, `umps14A`, `umps14B`, `umps14C` | 7 | 26 |
| 16 | `umps16`, `umps16A`, `umps16B`, `umps16C` | 8 | 30 |
| 18–32 | `umps18`, `umps20`, …, `umps32` | 9–16 | 34–62 |

Lettered variants use the same tournament schedule as the unlettered instance of that size and a different distance matrix. Some small variant files retain a historical permutation comment.

## File format

Each text file defines three values in an OPL-like syntax:

```text
nTeams=4;

dist= [
[0 745 665 929]
...
];

opponents= [
[3 4 -1 -2]
...
];
```

- `nTeams` is the even number `N` of teams.
- `dist` is an `N × N` symmetric integer distance matrix. Its diagonal is zero.
- `opponents` has `2N - 2` rows (rounds) and `N` columns (teams).
- A positive entry `j` in team `i`'s column means team `i` hosts team `j` in that round.
- A negative entry `-j` means team `i` plays away at team `j`.

Every unordered pair meets twice and every ordered home/away pairing appears once.

The problem description calls the distance matrices metric. Because the published values are rounded integers, 17 files contain small triangle-inequality violations; the largest difference is six distance units. These values are retained exactly because changing them would make historical objective values incomparable.


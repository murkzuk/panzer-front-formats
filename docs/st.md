# ST — gunnery table

112 files, 3.3 MB. **Partially understood.**

| | files | size |
|---|---|---|
| `\D\UN\ST\<unitid>.ST` | 92 | 35,912 |
| `\D\MA\ST\M##.ST` | 20 | 5,752 |

## What is known

88-93% of each file parses as IEEE floats in the range 0..10. The commonest values are
`0.001` (2401 occurrences in one file), `1.0`, `0.365`, `0.5`, `0.02`, `0.05`, `0.2`.
There is no vertex or index structure; the tail is zero-padded.

A 16-byte header precedes the data, e.g. `33 00 10 81 00 01 01 00 03 01 0A 01`, then
floats from 0x0C onward.

## It is a gunnery table, not a selector

Identified during the decal hunt. The non-float remainder (11.7%) is a `-1` sentinel plus
out-of-range floats that read as **ranges in metres and angles in degrees**. There are **no
small-integer indices anywhere in the file**.

That rules `.ST` out as the home of any texture or decal selector — a guess made from two
directions at once, and wrong from both. The actual camouflage selector is in
[tank-tables.md](tank-tables.md).

The record layout and the meaning of individual values are still undecoded.

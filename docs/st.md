# ST — statistics table

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

## What is not known

The record layout, and what the values mean. Given a simulation that models component
damage, a per-vehicle table of several thousand probabilities most likely holds
hit / penetration / component-damage odds — but **no value has been tied to observed
in-game behaviour**. Treat this as a lead.

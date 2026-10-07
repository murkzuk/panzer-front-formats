# PZE — message table

All in-game text: radio dialogue, briefings, UI strings. 324 files across five languages.

The game shipped the converter that builds them, `MessageConv.exe` (MFC, built
2003-10-14), **and** the `.txt` sources next to every `.PZE`. The format below is derived
from matched input/output pairs, not guessed.

## Source `.txt`

Shift-JIS, CRLF line endings, one record per line:

```
0002,0,16,-1,-1,-1,-1,-1,-1,0,16,-1,-1,-1,-1,-1,-1,Panzer-Regiment 35:¥Right flank, advance towards¥Jandrenouille from the north.
```

- 4-digit record ID
- 16 comma-separated integers (-1 = unused)
- the message text

`¥` (Shift-JIS 0x5C, the yen sign at the backslash codepoint) is the **line break** inside
a message.

## Compiled `.PZE`

```
always 19712 bytes = 144 slots x 136 bytes + a 128-byte trailer
```

Record *N*'s text begins at `N * 136`, NUL-terminated. Empty slots are blank, so a file
with one message and a file with 127 are both 19712 bytes.

Confirmed against the source: line 2 -> 0x0088, line 3 -> 0x0110, line 4 -> 0x0198,
line 10 -> 0x04C8.

## Caution: uninitialised buffer

`MessageConv.exe` does not clear its working buffer between runs. Unused space in the
`.PZE` files contains fragments of previously converted files — one observed file holds
the literal string `MAP\EVT19.PZE` and pieces of other messages. Harmless to the game,
but **parse by the NUL terminators, never by scanning for readable runs**.

## Languages

`\D\NE\00` .. `\D\NE\04`, same IDs throughout:

| | |
|---|---|
| `00` | English |
| `01` | German |
| `02` | Japanese |
| `03`, `04` | remaining PAL languages |

The English build still contains untranslated Japanese in places, e.g. 政治将校
(*politruk*, the Soviet political officer) in the crew-role table.

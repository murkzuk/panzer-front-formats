# PAK — the disc archive

The entire game ships in two archives in the ISO root: `D.PAK` (898 MB, 2630 files) and
`D1.PAK` (408 MB, 12 files — streamed audio and an SPU2 sound bank).

Original container research by **derplayer**
([QuickBMS script, 2022](https://gist.github.com/derplayer/d825a75a99e9844d9e643596c006099c)).
This repo reimplements it in Python and adds a sanity-checked listing.

## Layout

```
0x00  u32   file count
0x04  u32   global header length (= offset of the first file's data)
0x08        entry table, 0x48 (72) bytes per entry:
              0x00  u32   offset, absolute from the start of the PAK
              0x04  u32   size in bytes
              0x08  char  name, NUL-terminated, backslash-separated path
                          (remaining bytes of the 72 are padding)
```

Verified against the PAL release (SLES-52984): 2630 entries, zero offsets or sizes
falling outside the archive.

## Contents of D.PAK

| directory | files | bytes | holds |
|---|---|---|---|
| `\D\ME` | 924 | 89 M | missions and briefings |
| `\D\UN` | 470 | 29 M | units |
| `\D\NE` | 395 | 6 M | message text, five languages |
| `\D\MA` | 336 | 89 M | maps |
| `\D\OT` | 230 | 7 M | duplicate/other |
| `\D\DI` | 165 | 3 M | tank data tables |
| `\D\CM` | 87 | 3 M | Sony IOP modules (.irx) |
| `\D\SD` | 20 | 672 M | audio |
| `\D\FO` | 3 | 0.1 M | fonts |

## Developer leftovers shipped on the retail disc

- `\D\NE\*\MessageConv.exe` — 360 KB MFC tool, built 2003-10-14, that produced the
  `.PZE` message files from `.txt`. Six identical copies.
- `nor_copy2.bat`, `SET_copy.bat`, `ALL.bat`, `ALL.PIF` — build scripts
- 37 dated backups, e.g. `tname.pze0107`, `tname.pze1219`, `tname.pze_0612`,
  `TENTRY06.PZE_mk1`, `map007.tex_`

## Tools

```
python tools/paklist.py            # inventory both archives from the ISO
python tools/pakx.py "*.PZA" out/  # extract by wildcard
```

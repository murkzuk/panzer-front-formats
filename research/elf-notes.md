# ELF notes — locating the resource loader

Target: `SLES_529.84.ELF`, 1,489,712 bytes, fully stripped (`.symtab` and `.strtab` size 0),
built with Metrowerks CodeWarrior for PlayStation 2. `$gp = 0x00273570`.
~372,288 instructions.

## CORRECTION: every address in the first version of this file was wrong by +0x80

The program headers are:

```
PH0  PT_LOAD  p_offset=0x00000080  p_vaddr=0x00100000  p_filesz=0x0016B900  p_memsz=0x00272D00
PH1  PT_LOAD  p_offset=0x0016B980  p_vaddr=0x00372D00  filesz=0  memsz=0
```

The loadable segment starts at **file offset 0x80**, not 0. The conversion is therefore:

```
vaddr = 0x00100000 + (file_offset - 0x80)
file_offset = vaddr - 0x00100000 + 0x80
```

The first version of these notes used `0x00100000 + file_offset`, omitting `p_offset`. Every
data address it published was **0x80 too high**. Corrected, with the old values shown so the
error is traceable:

| string | correct vaddr | as first published (wrong) |
|---|---|---|
| `\D\UN\PZ\%06d.PZ` | `0x00264810` | ~~0x00264890~~ |
| `\D\UN\PZA\%08d.PZA` | `0x00264830` | ~~0x002648B0~~ |
| `\D\UN\ST\%06d.ST` | `0x00264850` | ~~0x002648D0~~ |
| `\D\MA\DCL\DCL%03d_%d.PZA` | `0x002647D0` | — |
| `\D\MA\GRD\%03d.PZC` | `0x002643A0` | ~~0x00264420~~ |
| `\D\MA\GRD\MAP%03d.TEX` | `0x00264380` | ~~0x00264400~~ |
| `\D\MA\GRD\CLD%02du.PZA` | `0x00264250` | ~~0x002642D0~~ |
| `\D\MA\OBJ\OBJ%03d.PZ` | `0x00266FC0` | ~~0x00267040~~ |
| `\D\OT\AS\INF\MDL\%s.PZ` | `0x002653A0` | ~~0x00265420~~ |
| `\D\OT\TH\CURSOR.PZ` | `0x002642D0` | ~~0x00264350~~ |
| `cdrom0:\D.PAK` | `0x00263E40` | ~~0x00263EC0~~ |

Credit: the `+0x80` error was spotted by the parallel DeepSeek session.

**This is why the reference searches failed.** The old notes recorded
"`lui`/`addiu` loading a path string address: **0 references**", and concluded that
Metrowerks used `$gp`-relative addressing and pointer tables rather than inline address
construction. That conclusion was an artefact of searching for addresses that do not exist.

## Both retracted conclusions

### 1. "Zero code references to the path strings" — wrong

With correct addresses there are **199** `lui`/`addiu` pairs constructing a path-string
address. Every single path format string in the game is referenced this way. The scanner is
`refscan3.py`.

### 2. "Reached by index x stride, so the resource table is an index table" — wrong

The strings do sit at regular 0x20 intervals (39 of 94 are on a 0x20 boundary; 49 of the 93
gaps are exactly 32 bytes), and that regularity is real. But it is **alignment padding, not
an addressing scheme**. The code reaches each string by its own `lui`/`addiu` immediate
pair. There is no index table.

This is the second time in this project that a strong statistical regularity turned out to
be a symptom rather than a mechanism — see the `8*(n%2)` phase in [pz.md](../docs/pz.md),
which held at 100% and was still not part of the format.

### 3. The trap that defeats a corrected search too

`\D\UN\PZ\%06d.PZ` and its two siblings appear **twice** in the ELF:

```
0x00264810   referenced by the mission loader at 0x00188870
0x00268B60   referenced by a second code path at 0x002273C8
```

Searching for references to the wrong copy finds nothing even with the right address. A
`count` check on each string catches this; the first probe reported `count=2` and it was
not followed up. Only three data words in the whole ELF point at any path string
(`0x0023BE30/34/38` -> the three `\D\SD\SE.*` sound files), so the two copies really are
reached by immediate, not through a table.

## The resource loader — found

```
0x00215AA8  (char *namebuf, const char *fmt, int a, int b) -> handle
```

The generic "format a resource name and load it" helper predicted by the old notes. Every
asset path goes through it. Two call clusters worth naming:

**Mission asset load**, `0x00188868` onward — vehicle model, texture and stats from three
ids in a descriptor record at `+0x90`, `+0x94`, `+0x98`, skipped when the id is zero:

```
00188868  lw   a2,144(s3)        ; model id
00188878  jal  0x00215AA8        ; -> \D\UN\PZ\%06d.PZ
00188890  sw   v0,20996(s2)
00188898  lw   a2,148(s3)        ; texture id   -> \D\UN\PZA\%08d.PZA
001888B8  lw   a2,152(s3)        ; stats id     -> \D\UN\ST\%06d.ST
```

**Decal load**, `0x001881A0` onward — five sheets selected by the map index at `+0x1678`.
Fully solved, see [decals.md](../docs/decals.md).

**Second code path**, `0x002273C8` onward — the same three vehicle paths, from the duplicate
string block at `0x00268B60`, storing handles at `+0x1F8`, `+0x200`, `+0x204` of a different
struct. Not yet identified; a garage or vehicle-viewer screen is the obvious guess.

## The localised string table

`0x00242D00` onward (**not** `0x00242D80`) is the localised string table: path formats sit
in it beside crew-role and component names, in three language blocks. The single code
reference into it, at `0x00190990`, is a 24-byte-stride table walk feeding a text routine —
the vehicle information screen, not a loader. That part of the old analysis stands; only its
addresses were wrong.

## Searches that did not find a `.PZ` *parser*

Still unfound, and these negative results remain valid — they were structural searches, not
address searches:

| approach | result |
|---|---|
| `sll r,n,6` + `sll r,n,3` (shift-based x72 / x76) | 0 candidates |
| immediate 72 or 76 near a `mult` | 2 hits, both unrelated |
| `andi r,1` + `sll r,3` (the `8*(n%2)` phase) | 2 hits, both bit-field code |

The phase search was always going to fail: the phase is a consequence of AABB-table
alignment, not something the code computes.

Next entry point for the parser is the loader itself: `0x00215AA8` returns a handle, and
whatever consumes a `.PZ` handle has to walk the node hierarchy.

## Tools

* `refscan3.py` — enumerates path strings by true vaddr, then finds both data pointers and
  `lui`/`addiu` immediates that reach them.
* `dis.py` — minimal MIPS disassembler, vaddr in, listing out.
* `fld.py` — every load/store using a given struct offset, `sp`/`gp` relative excluded.
  Finding the single write to `+0x1678` is what identified the map-index field.

**Method note.** Convert file offsets through `p_offset` once, in one helper, and assert it:
take a string's known file offset, convert, convert back. Both of the wrong conclusions above
came from a two-line omission that no amount of further searching could reveal, because the
searches were self-consistently wrong.

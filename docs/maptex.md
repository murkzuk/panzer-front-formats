# Map and terrain — `\D\MA\GRD\`

Status: **partially decoded.** The terrain grid is solved structurally and the heightfield is
identified. The surface texture decodes. The world scale is **not** established.

Research and first decode by the parallel DeepSeek session, 2026-10-07. Every claim below was
re-run before publication — `tools/verify_map.py` reproduces the lot from the ISO. Four of the
original claims did not survive that check and are marked where they appear.

---

## 1. What is in the directory

```
MAP%03d.TEX      x20    702,464 bytes   (MAP013 is 699,776)
%03d.PZC         x23    657,096 or 1,470,024 bytes
%03d.ZC          x23    same sizes
CLD%02d[u|l].PZA x60      8,272 bytes   cloud layers
```

The 23 are not 23 maps. They are maps `001`..`020` plus three working variants that shipped by
accident: a Shift-JIS named `003<kana>`, `LINE_003` and `_009` / `_019`.

### `.ZC` and `.PZC` are *near* duplicates, not duplicates

**Correction.** The original finding was "byte-identical duplicates, verified on 001: 0 differing
bytes". That holds for 001 and for most of the set, but not all of it:

| | |
|---|---|
| names present as both `.ZC` and `.PZC` | 22 |
| byte-identical pairs | 18 |
| pairs that **differ** | 4 — `003<kana>` (109 bytes), `005` (16), `006` (46), `009` (26) |
| `.ZC` with no `.PZC` | `_009` |
| `.PZC` with no `.ZC` | `LINE_003` |

The differences are tiny — 0.002% to 0.017% of the file — so these look like two revisions of the
same map rather than two formats. Verifying on one file and generalising is what produced the
original claim; the pair check is cheap and is now in `verify_map.py`.

---

## 2. `.ZC` / `.PZC` — the terrain grid

```
+0x00  u32 header_size   always 24
+0x01  u32 cell_step     59 or 40      (see below)
+0x02  u32 width         468 or 700
+0x03  u32 height        468 or 700
+0x04  u32 ?             always 10
+0x05  u32 ?             always 10
+0x18  body              width * height * 3 bytes, THREE PLANES, PLANE-MAJOR
```

`header_size + width * height * 3 == filesize` exactly, for every file. The grid is fixed-size and
uncompressed.

### Correction: there are TWO grid sizes, and the dimensions are in the header

The original finding was that the header is `(24, 59, 468, 468, 10, 10)` **identical in all 23
files**. It is not. There are two classes:

| header | size | files |
|---|---|---|
| `(24, 59, 468, 468, 10, 10)` | 657,096 | 42 — everything else |
| `(24, 40, 700, 700, 10, 10)` | 1,470,024 | 4 — **maps 011 and 018**, both extensions |

So **maps 011 and 018 are 700x700, not 468x468.** Read the dimensions from fields 2 and 3; never
hardcode 468. Anything that assumed a single grid size silently mis-reads those two maps.

### Field 1 looks like the cell step, not an unknown

Taking field 1 as world units per cell makes the two grid sizes describe nearly the same world:

```
468 cells x 59 = 27,612
700 cells x 40 = 28,000      — 1.4% apart
```

Two different grid resolutions covering one map size is exactly what you would expect, and it is
the only reading tried so far that explains why field 1 moves when the dimensions do. It is a
**hypothesis supported by one coincidence across two samples**, not a measurement.

It matters because it **competes directly with the assumption underneath the height scale** (§5):
that chain takes the trailing `10, 10` as the cell size. Both cannot be the cell size. Fields 4
and 5 are constant at `10` across every file and remain unidentified.

### The body is plane-major, and the evidence is decisive

Not interleaved 3-byte cells. Reshaping the body as interleaved `(h, w, 3)` yields three channels
with near-identical statistics, which no real data does:

| layout | plane 0 | plane 1 | plane 2 |
|---|---|---|---|
| **plane-major** mean / adj-diff | 30.56 / 13.78 | 97.59 / **0.66** | 2.29 / 2.38 |
| interleaved mean / adj-diff | 43.45 / 8.79 | 43.50 / 8.93 | 43.48 / 8.93 |

The original route to this was a statistical-character scan that located the change at
~213,000–221,000 against a plane boundary at `468^2 = 219,024`. The interleaved-is-identical
check above is the cheaper confirmation and is the one in `verify_map.py`.

---

## 3. The three planes

### Plane 1 is the heightfield — confirmed

Smooth in **both** axes (adjacent-difference 0.625 across, 0.618 down) and varying per map as
terrain should:

| map | min | max | mean | relief |
|---|---|---|---|---|
| 001 | 35 | 205 | 97.6 | 170 |
| 002 | 69 | 176 | 137.8 | 107 |
| 003 | 69 | 176 | 137.8 | 107 |
| 006 | 75 | 239 | 128.5 | 164 |
| 013 | 75 | 255 | 119.7 | 180 |

Jeff identified the planes by eye from a side-by-side render; the smoothness and per-map variance
are the independent confirmation.

### Correction: plane 0 is dense, not sparse

The original text grouped planes 0 and 2 as "sparse feature maps" and stated plane 0 is **71%
zero**. Measured, plane 0 is **4.5% zero** on map 001 and **0% zero** on map 011. It is a dense,
high-frequency field with a flat histogram — 185 distinct values, adjacent-difference ~14. The
71% figure appears to be the separate `(p0 >> 4) == (p2 >> 4)` agreement statistic, which is 72%.

The original table in the same document already said "share of commonest value 4.5%", so the
document contradicted itself; the table was right.

| | plane 0 | plane 2 |
|---|---|---|
| distinct values | 185 (0..221) | 32 (0..31) |
| zero | **4.5%** | 82.1% |
| adjacent-diff x / y | 13.73 / 15.05 | 2.38 / 2.15 |
| pearson vs heightmap | 0.068 | 0.071 |
| pearson vs each other | — | 0.569 |

So: **plane 2 is sparse, plane 0 is not.** Neither correlates with the heightfield, so neither is
terrain shape; they correlate with each other, so they encode related information. What they mark
is unknown — roads, spawn points and object placement are all plausible, none is confirmed.

### Plane 2 is not populated on every map

On map 001, plane 2 decomposes into a flag bit plus a 4-bit code: the high nibble takes only 0 and
1, the low nibble is 0 in 85% of cells and otherwise dominated by 8. That is a single-map
observation, and plane 2 varies enormously across the set:

| map | grid | plane 2 zero | distinct values |
|---|---|---|---|
| 001 | 468x468 | 82.1% | 32 |
| 011 | 700x700 | **100.0%** | 4 |
| 018 | 700x700 | **100.0%** | 4 |
| 020 | 468x468 | 23.7% | **2** |

Map 020 is the opposite extreme from 001 — mostly non-zero, but only two values in the whole
plane. Any reading of plane 2 has to tolerate both an entirely empty plane and a near-binary one,
and the nibble decomposition cannot be assumed to generalise.

---

## 4. `MAP%03d.TEX` — the surface texture

The five header `u32`s are a size and a **chain of section offsets**, not opaque constants:

```
+0x00  u32  0x00800080   = two u16: width 128, height 128
+0x04  u32  96      0x0060   -> 4bpp index map 128x128   8,192 bytes
+0x08  u32  8288    0x2060   -> 4bpp mip        64x64    2,048 bytes
+0x0C  u32  10336   0x2860   -> 4bpp mip        32x32      512 bytes
+0x10  u32  10848   0x2A60   -> tail block             691,616 bytes
+0x20  palette 16 x RGBA (64 bytes)
```

Each offset is the previous one plus that level's exact size, and the last points at the tail. The
header is identical in all 20 files; only the tail length differs (MAP013 is 2,688 bytes shorter).

* The **16-colour palette is per map**: MAP001 is green (mean RGB 55,108,46), the rest are sand.
* The 4bpp levels decode cleanly with all 16 entries used.
* The **691,616-byte tail is unexplained.** High-entropy (adjacent-byte delta 43–59 against 85 for
  random), not structured 4bpp (nibbles uniform), not compressed (size barely varies between
  maps), no discoverable stride. It now has one new property: it is a **header-declared section**,
  which makes "sub-resources with their own headers" a more reasonable thing to scan for.

---

## 5. Resolved non-question: there is no 468 -> 128 mapping

`468 / 128 = 3.6562` is not a ratio to solve. The texture is a **tiling detail texture** at a
different spatial scale from the terrain:

| | ac(1) | ac(4) | ac(16) | ac(64) |
|---|---|---|---|---|
| heightmap | 0.997 | 0.969 | 0.902 | 0.827 |
| `MAP001.TEX` 128x128 | 0.362 | 0.215 | 0.128 | 0.039 |

Correlation between texture and heightmap is **-0.138 at zero lag and no better at any offset**
(rolls of 32/64/96 tested in both axes), so the texture is not an albedo of the terrain. Tile it at
a chosen rate; the rate is a rendering parameter, not format data.

Published as a resolved non-question specifically so the next person does not spend time on it.

---

## 6. The height scale is NOT established

Enough is known to build terrain geometry and surface it. The **vertical scale is a guess** and
must not be used as a fact.

The derivation offered was: model 110003 measures 5.58 units against a roughly 5.9 m Panzer III,
therefore a cell is 10 units (from the header's trailing `10, 10` — **assumed**), therefore one
height level is one model unit (**guessed**), giving `K = 0.10` and a 3.6% average slope. A
plausible average slope is the entire support for it.

§2 gives a reason to doubt the first assumption outright: field 1 is the better cell-step
candidate, and it is 59 or 40, not 10. An earlier render of this terrain shipped at roughly 25x
the correct vertical exaggeration before a sanity check caught it, which is how the question
surfaced.

No render is published here, because any render bakes in a vertical scale that is not known.

---

## 7. Open questions

1. **What do planes 0 and 2 mark?** Plane 0 dense, plane 2 sparse and sometimes empty, neither
   correlated with height, 0.569 correlated with each other.
2. **What is the world scale?** Specifically whether field 1 is the cell step, and what the two
   trailing `10`s are.
3. **What is the 691,616-byte `.TEX` tail?** Scan it for `.PZA`-style sub-headers.
4. **Why are 011 and 018 the same 700x700 terrain?** They are byte-identical to each other, and
   they are two of the four maps that have **no decal sheets** (11, 12, 18, 20 — see
   [decals.md](decals.md)). Two map slots sharing one larger terrain and carrying no vehicle
   markings is a consistent enough pattern to be worth a look.
5. **Maps 002 and 003 are near-duplicates, not duplicates.** They have identical min/max/mean/
   relief, which raised the question, but the files differ: 800 differing bytes in the heightfield,
   1,582 in plane 0, 979 in plane 2. 003 reads as a lightly edited copy of 002.

---

## 8. Method note

The plane split was found by scanning for where the statistical character changes, **not** by
assuming a layout. `24 + w*h*3 == filesize` would have supported the wrong interleaved layout
just as well. Arithmetic that fits is not evidence of layout — look for a change in character, or
for a redundancy that an incorrect decode cannot reproduce.

The four corrections on this page all have one shape: **a property verified on one sample and
generalised to the set.** Byte-identical on map 001; the header on map 001; the nibble structure
on map 001; "71% zero" taken from the wrong line of the same table. `verify_map.py` runs every one
of them across all files rather than one, which is the cheap guard.

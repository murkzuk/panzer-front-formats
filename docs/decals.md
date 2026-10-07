# Decals — `\D\MA\DCL\DCL%03d_%d.PZA`

**The selector is solved.** Decal sheets are chosen by the **map**, not by nation and not by
vehicle. Each map loads a fixed set of five sheets.

## The format string and its two integers

```
\D\MA\DCL\DCL%03d_%d.PZA        at vaddr 0x002647D0
```

Referenced from exactly **one** site in the ELF, `0x001881A4`, inside a five-iteration loop:

```
00188194  s2 = 0                     ; sheet counter
001881A0  v0 = [s0 + 0x1678]         ; the map index  (s0 = a0 at function entry)
001881A4  lui   a1,0x0026
001881A8  a0 = sp+848                ; name buffer
001881AC  addiu a1,a1,0x47D0         ; -> the format string
001881B0  a3 = s2                    ; the _%d
001881B4  jal   0x00215AA8           ; the generic resource loader
001881B8  a2 = v0 + 1                ; the %03d   (delay slot)
001881C8  s2 = s2 + 1
001881D0  sw    v0,-12352(at)        ; handle table, stride 4
001881D4  slti  v0,s2,5              ; loop while s2 < 5
```

So the two integers are **not** two selectors:

| field | meaning |
|---|---|
| `%03d` | map index + 1 — the same number as the map's terrain, objects and clouds |
| `_%d` | a plain 0..4 sheet sequence, iterated by the loop. Not a choice. |

## The map index: field `+0x1678`

One write in the whole ELF, and every reader is a `\D\MA\…` (map tree) asset path. All of
them use the identical `index + 1` idiom:

| site | asset |
|---|---|
| `0x00173808` | **the only write** — `sw s0,5752(v0)`, immediately before `CLD%02du.PZA` |
| `0x00178368` | `\D\MA\GRD\MAP%03d.TEX` |
| `0x001783E0` | `\D\MA\GRD\%03d.PZC` |
| `0x001881A0` | `\D\MA\DCL\DCL%03d_%d.PZA` |
| `0x001E7218` | `\D\MA\MM\MINI%02d%c.PZA` |
| `0x00206A28` | `\D\MA\OBJ\T%02d.T` |
| `0x00206AB0` | `\D\MA\OBJ\OBJTEX.DAT` |
| `0x00206B08` | `\D\MA\OBJ\OBJ%03d.PZ` |
| `0x00173940` | `\D\MA\ST\M%02d.ST` |

That identifies the field: `+0x1678` is the **0-based map index**, and every map-tree asset
is numbered from 1.

## Verification against the disc

The code predicts the filenames. The disc confirms them, exactly:

* **16 sheet numbers × `_0`..`_4` = 80 files, with no exceptions** — the `slti ...,5` loop
  bound reproduced from the PAK listing without reference to the code.
* Every DCL number lies inside the map range 1..20, alongside `GRD\%03d.PZC`,
  `MAP%03d.TEX`, `OBJ%03d.PZ` and `MA\ST\M%02d.ST`, which all have the full 1..20.
* The set is **sparse**: maps **11, 12, 18 and 20** have terrain but no decal sheets. The
  loader still asks for them; a missing resource is tolerated.
* All 80 are 32,848 bytes — one `.PZA` geometry, consistent with a fixed sheet size.

## Why decals are per-map, not per-nation

This looked wrong at first, because markings are national (Balkenkreuz, RAF roundel,
tricolour). It is consistent for a scenario-based game: each map has a fixed set of
combatants, so one sheet set per map covers every marking needed in that battle. It also
explains why `DCL` sits under `\D\MA\` (the map tree) rather than under `\D\UN\` (units) —
the earlier guess that this made them *map markers* was wrong, but the directory is not an
accident.

Contrast the vehicle loader at `0x00188868`, two hundred bytes further on, which takes
**three separate ids out of a descriptor record** — `+0x90` model, `+0x94` texture, `+0x98`
stats — and skips the entry when the id is zero. Vehicle assets are per-vehicle; decals
are per-map. Two different mechanisms, adjacent in the same function.

## The generic resource loader

```
0x00215AA8  (char *namebuf, const char *fmt, int a, int b) -> handle
```

Every asset path in the game goes through it, including all three vehicle paths and the
decal sheets. Its return value is stored straight into the owning struct, so it formats the
name **and** loads, rather than being a bare `sprintf`.

## Still open

The **selector** is solved; **placement** is not.

* Which decal on a sheet lands on which quad, and the UV mapping that puts it there.
* The decal-quad classifier over-selects: diagonal strips across the road wheels take decal
  texture in `DCL002_0` / `DCL006_2` and should not. `DCL001_0` is good ground truth — it
  draws two correctly formed, correctly placed Balkenkreuz on the hull side plus yellow
  turret numerals.
* `DCL002_0` is the magenta `TEST-TYPE` placeholder family.

The `\D\ME\BRIEFING\*.PZD` lead is **not needed** for the selector and is now moot. Noted
for the record: those 57 files are 84 bytes each, far too small to hold a decal table.

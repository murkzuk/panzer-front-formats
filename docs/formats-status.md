# Format status

| extension | count | status |
|---|---|---|
| `.PAK` | 2 | **solved** — container, see [pak.md](pak.md) |
| `.PZA` | 1409 | **solved** — indexed texture, 1409/1409 exact, see [pza.md](pza.md) |
| `.PZE` | 324 | **solved** — message table ([pze.md](pze.md)); also carries the binary tank roster ([tank-tables.md](tank-tables.md)) |
| `.TXT` | 217 | plain Shift-JIS, source for `.PZE` |
| `.ST` | 112 | partial — gunnery table, ranges and angles, see [st.md](st.md) |
| `.PZ` | 129 | **solved** — models load, assemble and texture — see [pz.md](pz.md) |
| `.PZD` | 57 | unknown — 84 bytes each, under the briefing tree |
| `.AMD` | 54 | unknown — "AMD" may be animation data |
| `.DAT` | 43 | unknown |
| `.PZC` / `.ZC` | 46 | **partial** — terrain grid, heightfield identified, world scale not — see [maptex.md](maptex.md) |
| `.TEX` | 20 | **partial** — 128x128 4bpp + mips + per-map palette; 691,616-byte tail unexplained — see [maptex.md](maptex.md) |
| `.EVT` | 19 | unknown — events |
| `.IRX` | 82 | Sony IOP modules, standard PS2 |
| `.WAV` | 16 | audio |

`.PZ` is solved: models load, assemble from the node hierarchy and texture correctly from
the matching `.PZA`. Remaining unknowns are decal placement on hulls and turrets, and the
`.T` map-prop textures.

Decal **selection** is solved — five sheets per map, chosen by the map index, see
[decals.md](decals.md). Decal **placement** on the hull is not.

# Format status

| extension | count | status |
|---|---|---|
| `.PAK` | 2 | **solved** — container, see [pak.md](pak.md) |
| `.PZA` | 1409 | **solved** — indexed texture, 1409/1409 exact, see [pza.md](pza.md) |
| `.PZE` | 324 | **solved** — message table, see [pze.md](pze.md) |
| `.TXT` | 217 | plain Shift-JIS, source for `.PZE` |
| `.ST` | 112 | partial — float stat table, see [st.md](st.md) |
| `.PZ` | 129 | **solved** — models load, assemble and texture — see [pz.md](pz.md) |
| `.PZD` | 57 | unknown |
| `.AMD` | 54 | unknown — "AMD" may be animation data |
| `.DAT` | 43 | unknown |
| `.PZC` / `.ZC` | 46 | unknown |
| `.TEX` | 20 | unknown — distinct from `.PZA` |
| `.EVT` | 19 | unknown — events |
| `.IRX` | 82 | Sony IOP modules, standard PS2 |
| `.WAV` | 16 | audio |

`.PZ` is solved: models load, assemble from the node hierarchy and texture correctly from
the matching `.PZA`. Remaining unknowns are decal placement on hulls and turrets, and the
`.T` / `.TEX` map-prop textures.

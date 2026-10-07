# TSET / TENTRY — the vehicle roster and the camouflage selector

These answer "which model, and which skin" for every tank in the game. They are `.PZE`
files, so they use the [message-table container](pze.md), but their records are binary
rather than text.

## Record

16 bytes, four `u32`:

```
[index]  [modelID, 6 digits]  [textureID, 8 digits]  [modelID again]
```

`textureID = modelID * 100 + variant` — see [pza.md](pza.md). The fourth field repeats the
model id; its purpose is unconfirmed.

## The two tables

| file | size | records | role |
|---|---|---|---|
| `\D\DI\TANK\TSET01.PZE` | 1040 | **65** | master list — one per vehicle model |
| `\D\DI\TANK\TANK2\TSET##.PZE` | 1296 | 81 | a longer variant set |
| `\D\DI\TANK\TENTRY##.PZE` | 176 | 11 | per-scenario roster, 19 of them |

65 records in `TSET01` matches exactly the 65 distinct 6-digit model ids on the disc.

A model appears more than once in `TSET01` when it has more than one skin:

```
3   110003   11000301   110003      <- Panzer III, grey
3   110003   11000303   110003      <- Panzer III, sand
7   110007   11000702   110007
7   110007   11000703   110007
```

## The camouflage selector

`TENTRY##` is where a scenario picks its vehicles, and the variant digits carry the theatre:

```
TENTRY01   11000101  11000501  11000901  11001201  14001801 ...   <- variant 01, GREY
TENTRY03   31005121  31004805  35006320  31005705  21003807 ...   <- high variants, SAND
```

`TENTRY01` is the grey / early-war roster; the rest are desert. This is the mechanism behind
the colour split measured across the atlases — variant 1 is the only grey one of 91.

**Chain: mission -> TENTRY## -> (model, texture) per tank.**

## Notes

* `9999 / 519999 / 51999998` appears as a null or placeholder row in at least one backup
  table (`TENTRY01.PZ_`).
* The `.PZ_`, `.PZE_`, `.PZE_mk1`, `.pze0107`, `.pze1219` files alongside these are dated
  developer backups left on the retail disc, and their contents differ from the live tables.
  Do not parse them as current data.
* **There is no decal field in a TENTRY record** — only four `u32`, all accounted for. The
  decal selector is elsewhere; the mission tree `\D\ME\nn\` and `\D\DI\TD\FP_nnn.DAT` are
  unopened and are the current suspects.

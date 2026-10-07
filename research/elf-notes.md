# ELF notes — locating the .PZ parser

Target: `SLES_529.84.ELF`, 1,489,712 bytes, fully stripped (`.symtab` and `.strtab` size 0),
built with Metrowerks CodeWarrior for PlayStation 2. One `PT_LOAD` at `0x00100000`.
`$gp = 0x00273570`. ~372,288 instructions.

## The ELF DOES contain path strings

An earlier note in this project said the ELF held no useful strings. **That was wrong** — it
was based on searching for control/UI words. There are **124 distinct path-like strings**,
including every asset path as a printf format:

```
0x00264890   \D\UN\PZ\%06d.PZ            vehicle models
0x00267040   \D\MA\OBJ\OBJ%03d.PZ        map objects
0x00265420   \D\OT\AS\INF\MDL\%s.PZ      infantry models
0x002648B0   \D\UN\PZA\%08d.PZA          vehicle textures
0x00264780   \D\UN\QPL\QA%06d.PZA        interior panels
0x002647C0   \D\UN\SHL\SL%06d.PZA        shell sprites
0x002648D0   \D\UN\ST\%06d.ST            per-vehicle statistics
0x00264420   \D\MA\GRD\%03d.PZC          terrain
0x00264400   \D\MA\GRD\MAP%03d.TEX       terrain textures
0x0026 42D0  \D\MA\GRD\CLD%02du.PZA      cloud layers
0x00264350   \D\OT\TH\CURSOR.PZ          UI cursor model
0x00264740   \D\OT\TH\SHELL.PZ           shell model
0x00263EC0   cdrom0:\D.PAK               the archive itself
```

This confirms the directory meanings inferred from the PAK listing, and gives a name for
every format in use.

## Searches that did NOT find the parser

- **`sll r,n,6` + `sll r,n,3`** (a shift-based x72 / x76 multiply): **0 candidates**.
- **immediate 72 or 76 near a `mult`**: two hits, both unrelated — `0x0010C038` is a CRT
  divide helper, `0x00237D30` writes a 76-byte struct with fields at +12/+20/+24/+30/+34/
  +38/+48/+52/+56.
- **`andi r,r,1` then `sll r,r,3`** (the `8 * (n & 1)` phase): two hits, both bit-field
  manipulation on a byte, not the phase.
- **`lui` / `addiu` loading a path string address**: **0 references**. Metrowerks uses
  `$gp`-relative addressing and pointer tables, not inline address construction.

## The live thread

`0x00264890` (the vehicle model path) is stored as a pointer at three places:

```
0x00242D80, 0x00242E00, 0x00242E40     (spacing 0x80, then 0x40)
```

That looks like entries in a **resource descriptor table**. Finding what reads that table
should lead to the loader, and from the loader to the parser.

`refscan.py` (gp-aware, in the DeepseekSABoW workspace) resolves gp-relative loads and is
the tool for the next step.

# PZ — model / scene graph

129 files, 37 MB, under `\D\MA\Obj` (map objects), `\D\UN\PZ` (vehicles) and
`\D\OT\AS\INF\MDL` (infantry). **Container solved, mesh payload only partly decoded.**

## Container — verified on all 129 files

```
0x00            u32       file size (equals the actual file length in all 129)
0x04            u32       node count N
0x08            N x u32   parent index, 0xFFFFFFFF = root
0x08 + 4N       N x u32   node ID (100000, 100001, 10090, 60010, 1101 ...)
0x08 + 8N       N x 64    4x4 float matrix, the node's local transform
0x08 + 72N      N x u32   payload offset, relative to the end of this table
0x08 + 76N      ...       per-node payloads, in order
```

Checked across the whole set: `word0 == filesize`, offsets ascending and starting at 0,
and the last payload ending exactly at EOF — **129 / 129 consistent**.

The parent array is a valid hierarchy: every entry is either `-1` or a node index below
`N`. A tank is typically 150-200 nodes, a map object 4-120. The matrices are frequently
identity with Z negated, i.e. a handedness flip.

Node IDs are semantic, not sequential — `100000` for the root, then codes like `100011`,
`10090`, `60010`, `1101`, `30000`. They group plausibly by part, but **no ID has been tied
to a named component**.

## Payloads — four streams identified, chunking still open

There is **no per-node header**; a payload begins immediately with float data.

### The four vertex streams

All are arrays of four 32-bit floats, 16 bytes per element:

| stream | shape | notes |
|---|---|---|
| position | `(x, y, z, 1.0)` | part-local space |
| normal | `(nx, ny, nz, 1.0)` | same shape as position; told apart by `\|xyz\| == 1` |
| vertex colour | `(r, g, b, 0.0)` | 0..255 as floats; `255,255,255` and `128,128,128` dominate |
| texture coords | `(1.0, 0.0, u, v)` | u,v in 0..1; consecutive rows form triangles, rows 1-3 and 4-6 of a quad sharing the expected corners |

Four streams x 16 bytes = **64 bytes per vertex**.

### The size rule

`payloadLength = 48 + 64 * V` holds for **84.9%** of the 10,038 payloads, which gives a
vertex count. The remaining 15% are `32`, `16` or `0` mod 64 — consistent with sub-meshes
that carry three streams rather than four, but this has not been confirmed.

Payload lengths are divisible by 16 in 99.6% of cases and by 24 in 100%.

### Sub-meshes

A payload holds **more than one sub-mesh**, and their vertex counts sum to `V`. Clearest
example, a 6624-byte payload giving `V = (6624-48)/64 = 102`:

```
C11  pad3  P60 N60 C120  pad3  P42 N42 C73
                 ^^^              ^^^
                 60      +        42   = 102 = V
```

Sub-meshes appear to be separated by three zero floats.

### What is still NOT known

- **The stream offsets.** Boundaries are found by classifying content, not by reading any
  count or tag. In one leaf the UV rows are split 40 at the start and 20 at the end of the
  payload with position, normal and colour data in between — a layout no simple
  `[UV][POS][NRM][COL]` model explains.
- **The sub-mesh header.** Each sub-mesh is preceded by a short run that classifies as
  colour-like, of varying length (11, 86, ...). Its contents have not been decoded.
- Material and texture bindings; which `.PZA` a sub-mesh uses.
- No index buffer has been found, so vertices are presumably listed per triangle.

A check worth recording as a *negative* result: predicting `positions + normals == 2V`
from the size rule matches only **21%** of payloads, always falling short by a multiple of
6. That is most likely the position/normal classifier mis-sorting rows whose length is
near 1, not a failure of the size rule — but it has not been run down, and until it is,
the vertex count cannot be trusted per sub-mesh.

**Still not enough to load a model.** The hierarchy, transforms, vertex format and total
vertex count are known; where each stream begins is not.

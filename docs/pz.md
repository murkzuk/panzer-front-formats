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

## Payloads — partly decoded

There is **no per-node header**; a payload begins immediately with float data. Payload
lengths are divisible by 24 in all 10,038 blocks examined, and by 16 and 48 in 99.6%.

Two data streams are identified, both arrays of four floats:

| stream | shape | notes |
|---|---|---|
| texture coordinates | `(1.0, 0.0, u, v)` | u,v in 0..1. Consecutive rows form triangles — rows 1-3 and 4-6 of a quad share the expected corners. |
| positions | `(x, y, z, 1.0)` | homogeneous, small magnitudes consistent with part-local space |

Streams are separated by runs of zero floats. The root node's payload is different again:
min/max float pairs and `+-100000` sentinels, i.e. a **bounding-volume tree**, not mesh.

## What is NOT known

- **The chunking rule.** Stream starts are found by inspecting content, not by reading a
  count or a type tag. In one leaf the UV stream runs 40 rows, then 10 zero floats, then
  positions begin at a byte offset that is 8-aligned but not 16-aligned. No header
  explaining that has been located.
- How UV rows correspond to position rows (no index buffer has been found).
- Normals, vertex colours, material or texture bindings.
- What the second header array (node IDs) means per part.

**This is not enough to load a model.** The hierarchy, transforms and the existence of UV
and position data are solid; the geometry cannot yet be reconstructed.

## Related, unexamined

| ext | count | note |
|---|---|---|
| `.PZD` | 57 | exactly 84 bytes each, all under `\D\ME\BRIEFING` — not geometry |
| `.AMD` | 54 | all under `\D\OT\AS\INF` — infantry, plausibly animation |
| `.PZC` | 23 | all exactly 657,096 bytes under `\D\MA\GRD` — terrain-sized |

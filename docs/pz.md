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

## Payloads — solved

There is **no per-node header**. 243 payloads of identical length were diffed byte by byte
and share **zero** constant bytes, so nothing sits at a fixed position. No VIF or GIF tags
are present either, so this is not stored DMA packet data.

### Vertex rows — 16 bytes, four types

| type | shape | notes |
|---|---|---|
| `T` texcoord | `(u, v, 1.0, 0.0)` | u,v in 0..1 |
| `P` position | `(x, y, z, 1.0)` | part-local space |
| `N` normal | `(nx, ny, nz, 1.0)` | same shape as position, told apart by `norm == 1` |
| `C` colour | `(r, g, b, 0.0)` | 0..255 as floats; `255,255,255` and `128,128,128` dominate |

**Correction to an earlier revision of this file:** the texcoord row was previously given as
`(1.0, 0.0, u, v)`. That was a framing error — the rows are `(u, v, 1.0, 0.0)` and the
earlier reading was shifted 8 bytes.

### The start offset — SOLVED

```
phase = 8 * (nodeCount % 2)
```

Vertex rows begin `phase` bytes into each payload. **4947 / 4947 payloads agree, 100%.**

The reason is structural: the header is `base = 8 + 76N` bytes long, so an odd node count
leaves the data 4 bytes off an 8-byte boundary and an 8-byte skip corrects it. The phase is
therefore **constant within a file** — checked on all 129, none mixed — and derivable from
the node count alone.

Every payload offset in the table is itself a multiple of 16.

### Supporting evidence

Segmenting a payload into 16-byte rows and classifying each, **96.3% of the 5,677 payloads
of 160 bytes or more classify with zero unrecognised rows** at one of the four possible
4-byte phases. The four types above account for essentially every row in the file set.
That is solid confirmation of the vertex format.

Typical shapes, with padding rows removed:

```
TPNC      TPNCT      CTPNC      NCTPN
```

The same four streams in a rotating order, consistent with a repeating `T -> P -> N -> C`
cycle that different payloads enter at different points. Counts within a payload agree:
one 3888-byte payload gives `T39 . 000 . P60 N60 C60 . T20`.

Payload length also satisfies `48 + 64*V` for 84.9% of payloads, 64 bytes being the four
16-byte rows of one vertex.

### Still not known

- **Triangle assembly.** Positions appear to be listed per triangle, but taking every three
  consecutive position rows gives clean results for simple map objects and a partly
  scrambled result for vehicles, so strips or per-sub-mesh restarts are likely.
- **Position / normal separation.** Both rows are `(x, y, z, 1.0)` and are currently told
  apart by testing whether the vector is unit length. A position that happens to lie on the
  unit sphere is mis-sorted, which breaks the triangle sequence after it. This is the most
  likely cause of the stray geometry on vehicles and wants a proper rule.
- Material and texture bindings — which `.PZA` a sub-mesh uses.
- What the per-node ID values mean.

## Loader

`tools/pz2obj.py` converts a `.PZ` to Wavefront OBJ, composing each node's local matrix up
the parent chain to place parts in model space.

```bash
python tools/pz2obj.py D_MA_Obj_OBJ011.PZ out.obj
```

![A decoded map object](img/pz-decoded.png)

*`\D\MA\Obj\OBJ011.PZ` — 4 nodes, 96 vertices, 32 triangles, three views. Walls and a
roof panel, assembled correctly from the hierarchy.*

Vehicles export with recognisable hull, turret and gun barrel but carry stray triangles,
for the reasons above. Simple static objects come out clean.

### Negative results worth keeping

- 243 same-length payloads share no constant bytes — there is no fixed header.
- No VIF UNPACK or GIF tags anywhere in the payloads.
- 16-byte file alignment does **not** predict the phase (35.2%); the node-count parity rule
  does (100%).

# Panzer Front Ausf.B — widescreen patch: handover

**Game:** Panzer Front Ausf.B (PAL, SLES-52984, CRC `F2694B94`, ELF MD5 `e2ca97cc97fd96d33dad151dbc937cb0`)
**Emulator:** PCSX2 2.8.2. The user's install folder is called `pcsx2-v1.7.3137-windows-64bit-AVX2-Qt` but the binary reports **v2.8.2**. A scratch copy is at `K:\DeepseekSABoW\pcsx2run\`.
**ISO:** `D:\Panzer Front Ausf B\s-pfab.iso`

---

## 1. Status in one screen

| item | state |
|---|---|
| Main 3-D view Hor+ 16:9 projection | **found, implemented, verified as a transform** — 6 bytes |
| Sky never drawn in the outer 8.3% | **found and FIXED** — 1 byte, verified |
| Geometry corruption ("polys mutating into large triangles") | **NOT FIXED** |
| Ruled out | stored FOV angle, focal, screen-matrix constants, PCSX2 VU speedhacks |
| Current install state | patch **disabled** (`cheats\F2694B94.pnach.OFF`); the game boots stock and clean |

The patch widens the horizontal FOV by exactly 4/3, leaves the vertical untouched, and keeps
the 2-D HUD pixel-identical. The user's verdict: *"Aspect is great but this makes it useless"* —
because of the corruption.

---

## 2. Your single biggest advantage: you can look at pictures

**Every conclusion here was derived without ever seeing the screen.** That is the direct cause
of every wrong turn: a corrupting patch was once reported as "working" on the strength of a
pixel statistic, and a bug that only appears in motion was twice read as "clean" from static
frames.

The user can produce an image in five seconds: **F8 writes a timestamped PNG** into
`D:\pcsx2-v1.7.3137-windows-64bit-AVX2-Qt\snaps\`, and **F1 writes a savestate** to
`sstates\SLES-52984 (F2694B94).01.p2s`. Ask for both, taken at the same instant, with the
corruption on screen. That pair answers in seconds what statistics could not answer in hours:
seam, chunk boundary, clipped polygon, separate render pass, or guard-band wrap.

Images you can look at right now (all under `K:\DeepseekSABoW\pfa\`):

- `binos\shot_binos_patched.png` / `shot_binos_unpatched.png` — same savestate, patch on vs off
- `drive\f_{unpatched,A_proj,A_plus_C}_{0..6}.png` — 7-frame driving sequences, 3 configurations
- `site\f_unpatched.png` plus `site\f_s1..s6_*.png` — one projection site patched at a time
- `sweep\shot_*.png` — the constant-family sweep that located the sky fix
- `PROOF_side_by_side.png` — evidence that the projection patch is a correct Hor+

---

## 3. Do these first, in this order

1. **Look at the images above** — especially `binos\shot_binos_patched.png` next to
   `shot_binos_unpatched.png`, and the `drive\` sequences. If the artefact is in those
   frames you will see it immediately.
2. **Ask the user for F8 + F1 at the moment of corruption.** Do not proceed without it.
3. **Before bisecting anything, verify determinism:** load the same savestate twice with the
   same code and confirm the two captures are byte-identical. If they are not, the scene
   animates and section 8 will bite you.
4. Only then bisect, using the candidate list in section 11.

---

## 4. What is verified working

### 4.1 The projection patch (6 bytes)

    patch=1,EE,0016E6DC,byte,40
    patch=1,EE,0016EA8C,byte,40
    patch=1,EE,0016EFB0,byte,40
    patch=1,EE,0016F22C,byte,40
    patch=1,EE,0016F5D4,byte,40
    patch=1,EE,002270DC,byte,40
    patch=1,EE,0017308C,byte,AA      <- sky camera, see 4.2

The projection builder is `0x001106A0`. With o32 float args it takes `f12` scale,
`f13` x-factor, `f14` y-factor, `f15`/`f16` translation,
`f17`/`f18`/`f19`, and a stack `far` argument. It builds
`P = diag(f12,f12,0,…)` with `m23 = 1.0, m32 = 1.0, m33 = 0` (so `w' = z`), and
`T = diag(f13,f14)` with translation `(f15,f16)` and `T[10] = f21`, then
multiplies. Result:

    m00 = f12 * f13     (horizontal)
    m11 = f12 * f14     (vertical)

All six callers with a literal pair pass **f14 = 1.95f** (`lui 0x3FF9 / ori 0x999A`) and
**f13 = 1.0f** (`lui rX,0x3F80`). That pair *is* the screen aspect. Changing only `f13`
to `0.75f` gives `0.75 : 1.95 = 1 : 2.6`, exactly `(16/9)/(4/3)` = 4/3 wider.

Each patched byte is the **low byte** of a `lui`: `0x3C023F80 -> 0x3C023F40`
(= 0.75f), likewise for `0x3C033F80` and `0x3C063F80`. In every case the destination
register is **dead** after the single `mtc1 rX,f13` that consumes it.

| site | instruction | consumed by |
|---|---|---|
| `0016E6DC` | `3C023F80 lui v0,0x3F80` | `mtc1 v0,f13` @ 0x16E6E4 |
| `0016EA8C` | `3C023F80 lui v0,0x3F80` | `mtc1 v0,f13` @ 0x16EA94 |
| `0016EFB0` | `3C063F80 lui a2,0x3F80` | `mtc1 a2,f13` @ 0x16EFC8 |
| `0016F22C` | `3C023F80 lui v0,0x3F80` | `mtc1 v0,f13` @ 0x16F234 |
| `0016F5D4` | `3C033F80 lui v1,0x3F80` | `mtc1 v1,f13` @ 0x16F5D8 |
| `002270DC` | `3C023F80 lui v0,0x3F80` | `mtc1 v0,f13` @ 0x2270E4 |

**Do NOT patch the 1.95f sites** (`0x16E6F0/4, 0x16EAA0/4, 0x16EFD0/4, 0x16F5DC/E0,
0x2270F0/4`, and separately `0x16F874/8`) — see section 6.1.

**Verification** (controlled savestate A/B: same state loaded twice, cheats disabled, the only
difference being the patched bytes inside the state's `eeMemory`, GS aspect forced to 4:3
so the raw framebuffer is compared):

- cropping the patched frame to its central 75% and rescaling reproduces the unpatched frame; the best-fit crop peaks **sharply at exactly 0.75**
- 2-D sweep: horizontal **0.75**, vertical **1.00** exactly
- the 2-D HUD is **pixel-identical**: correlation 1.0000, mean abs difference 0.00
- the outer 12.5% strips each side contain genuinely new world content

### 4.2 The sky/backdrop camera (1 byte)

**Symptom it fixed:** the outer ~8.3% of the sky on each side was never drawn and showed the
framebuffer clear colour `RGB(125,135,205)` — 4.863% of the frame, in vertical bands in
the sky rows only, whose lower edge follows the terrain silhouette (jagged; moves as you drive).

**Cause:** the sky is rendered by a **separate camera**, whose FOV is derived from the same
256.0/192.0 half-extents, in the function containing `0x0017308C`:

    0x00173088  lwc1 f0,5960(s0)          focal (618.0)
    0x0017308C  lui v0,0x4380             256.0        <-- THE SITE
    0x0017309C  div.s f0,f1,f0            256/focal
    0x001730A8  div.s f13,f12,f0          192/(256/focal)
    0x001730B4  jal 0x0020F568            -> angle
    0x001730D4  add.s f20,f0,f1           + 0.0349066 (2 degrees)

**Fix:** `0x0017308C`  `lui v0,0x4380 -> lui v0,0x43AA`  (256.0 -> 340.0). 340.0 is
`256 x 4/3 = 341.33` to within 0.4%, i.e. the identical 4/3.

**Measured:** undrawn area **4.863% -> 0.002%**; only 5.336% of pixels changed and **every one
lies inside the previously undrawn region**; on a different scene with no gap the frame is
byte-identical with and without it.

---

## 5. What is broken

User's words: *"The polys in the terrain and sky are mutating into large triangles. From the
terrain up and then from the sky down. This was introduced from going widescreen. There was no
corruption in stock panzer front."* Also: *"binos unuseable due to corruption"*, and *"the
corruption is in both views, bino's and regular"*.

So: both the regular and the binocular view, only with the patch. The transform itself is
provably correct (4.1), so the fault is in the **engine's own geometry handling — clipping,
culling or LOD — carrying limits derived from the original 4:3 field of view**. That is the
thing to find and widen by the same 4/3.

### 5.1 Which projection site belongs to which view (measured)

Patching **one site at a time** on the user's binoculars savestate, compared with unpatched
(raw mean abs difference, 0-255):

| site | addr | raw diff | verdict |
|---|---|---|---|
| s1 | `0016E6DC` | 0.24 | does not affect this view |
| s2 | `0016EA8C` | 0.24 | does not affect this view |
| s3 | `0016EFB0` | 0.24 | does not affect this view |
| s4 | `0016F22C` | 0.24 | does not affect this view |
| **s5** | **`0016F5D4`** | **14.61** | **this view's projection** |
| s6 | `002270DC` | 0.32 | does not affect this view |

Measured on a STATIC frame — repeat it **while driving** (section 11). Five of the six sites
are inert in the binocular view, so the corruption there comes from widening that view's own
projection, not from patching the wrong sites.

---

## 6. Ruled out — do not repeat these

### 6.1 `1.95 -> 2.6` at the six 1.95f sites — **THIS IS THE PATCH THAT CORRUPTS THE RIGHT HALF**

1.95f is *also* the scale of the NDC->GS screen matrix (`m00 = 2047.0`,
`m11 = 2047 x 1.95 = 3991.65`, translation 2048/2048), which lives in VU1 data memory at
offset `0x140` (`0x154` for m11) and is built by `0x0016F800`. Raising it pushes
the mapped y range past the framebuffer. Kept as `F2694B94.pnach.BROKEN-aspect74`.

### 6.2 The stored FOV angle at `camera+5964` — variant C, ZERO effect

`192.0 -> 256.0` at `0x16D8C8, 0x173094, 0x173314, 0x182DE0, 0x208704` (makes the
computed FOV 57.9 degrees instead of 45.0). Measured no effect on two static scenes (0.00% of
pixels) and no effect in motion (25.01% vs 25.05% — identical). **The clip frustum is not
derived from this value.** Kept as `F2694B94.C-engine-fov.pnach`.

### 6.3 The focal at `camera+5960`

Changing 618.0 -> 463.5 gives a **uniform zoom in both axes**. It is the sight magnification,
not a screen FOV control.

### 6.4 `0x0026BC7C` (110.0 degrees exactly) x 4/3

A "sight angle" in radians, written by `0x001C0F70` which adds 0.017453292 (1 degree).
Scaling it is a uniform-ish zoom, not Hor+.

### 6.5 The 2047.0 / 1049.74 constants

`2047.0 -> 1705.83` at the five sites (`0x16E758, 0x16EAFC, 0x16F65C, 0x16F850,
0x16F9F4`): 0.02% of pixels change — those matrices are not used by the frames tested.

### 6.6 Variant B — "spend the 4/3 differently"

`f13 = 0.91796875` (`lui 0x3F6B`), `f14 = 2.38671875` (`lui 0x4018 /
ori 0xC000`): horizontal x1.089, vertical x0.82. The ratio is still exactly 2.6, so the 16:9
picture is correct, and since 1.089 < the sky's own 1.125 margin the sky bands vanish — but it
costs 18% of the vertical view and the user reports the corruption remains.
`F2694B94.B-no-sky-gap.pnach`.

### 6.7 The PCSX2 VU speedhacks

The user's config (and a clone of it) had `vuThread = true`, `vu1Instant = true`,
`vuFlagHack = true`. "Instant VU1" is a documented-unsafe speedhack and a strong suspect,
since a wider FOV pushes more geometry through VU1. The test was re-run with all three **off**;
the user watched both runs and reports the corruption is **still there in both**. Not the cause.

### 6.8 The pre-existing patch from another agent

It overwrote **instructions** with float data: `0x0010BD18` is `jr ra` and it wrote
`0x426CCCCD`; `0x001001BC` is `addiu t0,t0,0x220` -> `0x42680000`;
`0x00133A10` is `daddu s3,a0,zero` -> `0x44550000`. Junk. Kept as
`F2694B94.pnach.minimax-guess.bak`.

---

## 7. Address reference

    $gp                      0x00273570
    camera/config pointer    *(u16)(gp-31108) = *(u16)0x0026BBEC  -> initially 0x00436F00
      +5952  163837.6 (0x4823D70A)
      +5956  40.0     (0x4220)
      +5960  focal, default 618.0 (0x441A8000)
      +5964  FOV in DEGREES, recomputed each camera update
    FOV computation          0x0016D8C8..0x0016D908:
                             f13 = 192/(256/focal);  jal 0x20F568 (angle);
                             jal 0x16FC30 (rad->deg); swc1 f0,5964(s4); then x2
                             => 2*atan(192/(0.75*618)) = 45.0 degrees
    helpers                  0x20F568 atan2-ish, 0x20F150 tan-ish, 0x1C0920 atan2 (32 callers),
                             0x16FC30 rad->deg, 0x1C0E50 angle normaliser
    projection builder       0x001106A0   (six callers: 0x16E724, 0x16EAC8, 0x16EFF4,
                                          0x16F260, 0x16F628, 0x16FADC)
    NDC->GS screen matrix    0x0016F800 builds m00 = 2047.0, m11 = 2047.0*1.95
    sky camera FOV site      0x0017308C
    other 256.0 sites        0x16D8D4, 0x17308C(fixed), 0x173348, 0x182DD0, 0x1C1730,
                             0x1D4084, 0x1D7B44, 0x1E2220, 0x2086F8, 0x20DFB0, 0x20E320,
                             0x20E690   <- the 12 non-projection ones; prime suspects for
                                          other passes' FOV companions
    projection-builder 256.0 0x16E740, 0x16EAE4, 0x16EF9C, 0x16F5B8, 0x16F644, 0x16F804

**VU1:** the game uses VU1 microcode (16 KB micro memory, 12 KB non-zero). The microprogram is
present in the ELF image at about **`0x0022B090`** (a 512-byte probe matches the live
`vu1MicroMem.bin` verbatim). VU1 **data** memory offset `0x140` holds the NDC->GS
screen matrix; offset `0x000` holds the view matrix whose rows are `0.75 x` a rotation.

**ELF:** `K:\DeepseekSABoW\pfa\SLES_529.84.ELF`, 1,489,712 bytes, **fully stripped**
(`.symtab`/`.strtab` size 0). Compiler: `.comment` = `MW MIPS C Compiler
(2.4.1.01)` + `PlayStation2` — Metrowerks CodeWarrior. ~1722 `jal` targets, ~1801
stack prologues -> about 1,700-1,800 functions. 275 `jalr`. 417 COP2 (VU0 macro mode) and
883 MMI instructions. One PT_LOAD `0x00100000`, filesz `0x16B900`, memsz
`0x272D00` (~1.08 MB BSS).

---

## 8. CRITICAL: the measurement method used is NOT reliable for this bug

This is the most important lesson in the document.

Captures of the **same** configuration — same savestate, same settings, same 1326x746 size, no
resampling anywhere — gave these residuals against their unpatched partners:

    drive test frame 0, Instant VU1 ON        25.01% >24  /  20.86% eroded
    binos A/B,         Instant VU1 ON         15.49% >24  /  10.97% eroded
    binos A/B,         Instant VU1 OFF        17.13% >24  /  12.41% eroded
    binos A/B, Instant VU1 ON, 3-D region      7.73% >24  /   4.06% eroded

**Run-to-run variance (25.0 vs 15.5 for the same configuration) is larger than any effect being
chased.** The scene animates, so two runs never land on the same frame. An earlier control
showing "two runs of the same state are byte-identical" was true only for a *static* scene, and
generalising it was a mistake. Every bisect attempted against this residual was measuring noise.

The sweep-and-bisect method **did** work for the sky camera, because that symptom was a stable,
unambiguous metric: a band of one flat colour occupying exactly 4.863% of the frame,
reproducible to three decimals. This bug has no such metric.

**Therefore: do not bisect until the measurement is deterministic.** Suggested routes: freeze or
pause the game; drive a fixed input script and compare frame N with frame N after proving that
two identical runs really do produce identical frames; or find a single-frame,
position-independent metric such as counting long straight edges or measuring a specific
polygon's screen position.

---

## 9. Test harness — and the traps that cost the most time

**Booting with a state:** `pcsx2-qt.exe -statefile <state.p2s> <iso>` — about 82 s to the
game window, then 40-55 s more before it is settled enough to capture.

**A `.p2s` is a ZIP whose entries use ZSTD (method 93)** — CPython's `zipfile` cannot
read them. Entries include `eeMemory.bin` (32 MB), `vu0/vu1Memory.bin`,
`vu1MicroMem.bin` (the VU1 microcode), `GS.bin`, `PAD.bin` and an embedded
`Screenshot.png` (useful for identifying what a state shows). Rebuilt states may be written
with entries as STORED; PCSX2 accepts that.

**Traps, in order of how much time each cost:**

1. **`SetForegroundWindow` alone silently drops every key and every F8.** You must do
   `ShowWindow(SW_RESTORE)`, then
   `AttachThreadInput(GetCurrentThreadId(), GetWindowThreadProcessId(GetForegroundWindow()), true)`,
   then `SetForegroundWindow`, `BringWindowToTop`, `SetFocus`, then detach.
2. **Always verify a NEW F8 filename appeared.** Taking "the newest file" silently re-reads a
   stale capture. This produced a confidently wrong "no effect" conclusion, and one whole
   per-site run where two captures turned out to be byte-identical.
3. **Compare frames of the same pixel size only.** Screenshot size follows the window/aspect;
   resizing to compare injects artefacts that swamped one measurement.
4. **PCSX2 writes only the LOW BYTE of a `patch=` line not marked `extended`.** Emit one
   byte per change. A pnach with a `[Section]` header plus `gsaspectratio` is **not**
   applied from `cheats\`; keep that form in `patches\`.
5. **Per-game settings override the global ini.** `gamesettings\SLES-52984_F2694B94.ini`
   had `AspectRatio = 4:3` overriding the global 16:9 — the game was rendering 4:3 the whole
   time, which is part of why the user found it "hard to tell".
6. **A code patch applied at ELF load is overwritten by a state load**, so with `-statefile`
   the bytes *inside the state* are what matter. That is exactly what makes the A/B possible:
   build two states differing only in those bytes.
7. User screenshots came out **1479x746 = 1.98:1 with no letterbox bars**, i.e. the picture was
   being stretched ~11% horizontally on screen. Check F6 / window size before trusting any
   visual judgement.

**Method that worked:** find a reproducible, measurable symptom -> sweep whole constant families
(one family per run, ~2.5 min each) -> bisect the family that moves the metric (it went
18 -> 12 -> 6 -> 3 -> 1) -> confirm the winner changes *only* the intended region versus
unpatched.

---

## 10. Files and state

**User install** `D:\pcsx2-v1.7.3137-windows-64bit-AVX2-Qt\`:

- `cheats\F2694B94.pnach.OFF` — the 7-byte patch, **currently disabled**
- `cheats\F2694B94.B-no-sky-gap.pnach`, `cheats\F2694B94.C-engine-fov.pnach`,
  `cheats\F2694B94.pnach.minimax-guess.bak`
- `patches\SLES-52984_F2694B94.pnach.OFF`
- `gamesettings\SLES-52984_F2694B94.ini` — `AspectRatio = 16:9` (was 4:3),
  `upscale_multiplier = 3`, `Renderer = 12`, `vuThread/vu1Instant = true`
- `sstates\SLES-52984 (F2694B94).01.p2s` — **the binoculars state, the key test bed**
- `sstates\SLES-52984 (F2694B94).02.p2s` — an earlier sky scene

To re-enable the patch:

    ren "D:\pcsx2-v1.7.3137-windows-64bit-AVX2-Qt\cheats\F2694B94.pnach.OFF" "F2694B94.pnach"

**Tooling** (`K:\DeepseekSABoW\`): `mips.py` (R5900 disassembler, `class Elf`,
`disasm`); `dis.py &lt;lo&gt; &lt;hi&gt;`; `refscan.py` (gp-aware xref scanner);
`pfa\p2s_extract.py`; `pfa\p2s_patch.py`. `PYTHONPATH` needs
`K:\DeepseekSABoW\pylibs` for `zstandard`.

**Pre-built test states** (`K:\DeepseekSABoW\pfa\`): `binos\{p,u}.p2s`
(patched/unpatched); `drive\{unpatched,A_proj,A_plus_C}.p2s`;
`site\{unpatched,s1_16E6DC,s2_16EA8C,s3_16EFB0,s4_16F22C,s5_16F5D4,s6_2270DC}.p2s`;
`ab2\{ground_A,ground_C,ground_NONE,sky_A,sky_C}.p2s`.

**Audit trail:** `HANDOFF.md` (505 lines, the chronological version), plus
`WIDESCREEN_FINAL.txt`, `WIDESCREEN_VARIANTS.txt`, `PC_PORT_PLAN.md`.

---

## 11. Candidate hypotheses, ranked

1. **VU1 microcode clip/guard constants.** The vertex transform *and clipping* happen in the
   12 KB VU program. If it clips against a fixed guard band, that is the parameter, and it is
   patchable — the microcode is uploaded from the ELF, so a pnach can patch the **source in EE
   RAM before the upload**, and no VU disassembler is needed for a constant hunt, only sweep and
   measure. Located near `0x0022B090`. **This is where I would look first.**

2. **FOV companions for the other passes.** The sky needed its own camera FOV widened
   (`0x0017308C`). There are very likely siblings for the regular view's other passes. The
   12 non-projection `256.0` sites in section 7 are the prime suspects, and the same
   sweep-and-bisect that found `0x17308C` applies — **provided** you first fix the
   measurement (section 8).

3. **A FOV-dependent draw distance / LOD.** Would explain geometry appearing/disappearing rather
   than stretching. Look for anything derived from `camera+5960` (focal) or `+5964`
   (FOV) that feeds a cull or LOD decision.

4. **Caller-specific treatment.** The six `0x1106A0` callers have different arguments
   (`f12` = 768.0 vs 576.0, different translations), so they are plausibly different render
   targets or insets. If one draws a pass that must not be widened, that pass is the corruption —
   though the user reports corruption in **both** views, which weakens this.

5. **The community patch database has no entry for this CRC at all** (checked
   `PCSX2/pcsx2_patches`). Consistent with this game not being cleanly patchable with a
   simple FOV hack. Worth knowing before promising a result.

---

## 12. Addendum, 2026-10-06 — the images were looked at, and section 5 is wrong

Section 3 said "look at the images first". That was done. Three results, in order of how
much they change the plan.

### 12.1 The artefact is in the STOCK frames

`drive/f_unpatched_0.png` and `binos/shot_binos_unpatched.png` both show it: the pale
trapezoid over the sky and the flat green wedge at the right edge. The user's description
("terrain up, sky down, large triangles") fits them exactly.

These states are genuinely unpatched — not assumed, read. All seven patch sites were read
straight out of each state's `eeMemory.bin`:

| state | s1..s6 | sky |
|---|---|---|
| `drive/unpatched.p2s` | 80 80 80 80 80 80 | 80 |
| `drive/A_proj.p2s` | 40 40 40 40 40 40 | 80 |
| `binos/u.p2s` | 80 80 80 80 80 80 | 80 |
| `binos/p.p2s` | 40 40 40 40 40 40 | 80 |
| `site/s5_16F5D4.p2s` | 80 80 80 80 **40** 80 | 80 |

(`80` = `3F80` = 1.0f, stock. Note the sky fix is in none of these.)

**So the patch does not create the artefact.** In stock it sits in the rightmost ~5-8% of
the frame — `x=1253/1326` in the drive scene, `x=913/995` in the binoculars scene — a
sliver at the margin, invisible under CRT overscan and easy to miss on an emulator. The
wider FOV pulls it inward to ~83% of the width, where it becomes a large obvious block.
The patch is **revealing** a pre-existing boundary, not producing a new one.

### 12.2 Its screen position scales by exactly 0.75 — and that does NOT discriminate

Measured as the strongest column-to-column jump in the sky band, centre `x=663`:

```
drive scene    unpatched 1253  ->  patched 1104     (1104-663)/(1253-663) = 0.747
binos scene    unpatched  913  ->  patched  810     ( 810-498)/( 913-498) = 0.750
```

Two independent scenes, both exactly the patch's 0.75. **Resist the obvious reading.** It
proves the edge goes through the patched projection matrix, and nothing more. Both live
candidates predict it:

- **A — real world geometry** (map edge, backdrop skirt, a large near object): screen x is
  `m00 * X/Z * halfwidth`, so scaling `m00` by 0.75 scales the offset by 0.75.
- **B — a cull/LOD boundary fixed in view space at angle θ**: screen x is
  `m00 * tan(θ) * halfwidth`. Same 0.75.

What it *does* rule out is a framebuffer, guard-band or display-stretch artefact, which
would have stayed at a fixed screen position. The thing is in the scene, before the
projection.

`edge_compare.png` (written alongside this file) stacks the two crops with the measured
edges marked; the two shapes are the same shape, just scaled inward.

### 12.3 The test that DOES discriminate, and it costs a minute

With the patch on, sit still and **rotate the turret/hull through 360 degrees**.

- the wedge stays at the same place on screen regardless of heading -> **B**, a cull or LOD
  angle derived from the 4:3 frustum. Fixable: find the constant, widen by 4/3. This is the
  prize, and section 11's hypotheses 1 and 3 are then the right place to dig.
- the wedge is anchored to one compass direction and sweeps off screen as you turn -> **A**.
  Not a patch bug at all, and not fixable by patching; it means widescreen is showing past
  the edge of the drawn world at this particular spot.

A weak hint toward A: in patched frames 2-6 a green strip appears at the far **left**
(`x=0..27`) where the unpatched frames have nothing — the same kind of object on the other
side. Weak, because the view pitched up in those frames as well as turned.

### 12.4 Section 5.1's per-site table is not evidence

`site/f_s1_16E6DC.png`, `f_s2_16EA8C.png`, `f_s3_16EFB0.png` and `f_s4_16F22C.png` are
**byte-identical** — one MD5, `ada9a7db...`, across all four. That is section 9 trap #2
(a stale capture re-read) having actually happened: four runs, one screenshot. The "0.24,
does not affect this view" reading for s1-s4 is one number copied four times, not four
measurements.

Separately, `site/f_unpatched.png` is 1326x746 while every `f_s*.png` is 995x746 — 16:9
against 4:3, section 9 trap #3. The whole table is a cross-aspect comparison.

**So "five of the six sites are inert in the binocular view" is unsupported.** s5 and s6
were genuinely captured (distinct MD5s); s1-s4 were not. Redo it if it matters.

### 12.5 Every capture on disk is one spot in one mission

`drive/f_*_0..6` is not a drive. Frames 0-1 look forward from the start position; by frame
2 the view has swung up into sky and fog and stays there for 2-6 — the tank never moved.
The binoculars states are the same position and the same scene (Panzer 211/221/411, the
same field and village). The per-site states too.

Which means the conclusion "widescreen breaks the game" currently rests on **one camera
position**. Before any more disassembly, get captures from the middle of a different map.
If the artefact is absent there, this is scene-specific and the patch may already be
shippable with a caveat.

### 12.6 What is still true

Sections 4.1, 4.2, 6 and 8-10 stand; nothing here touches the projection work, the sky
camera fix, or the ruled-out list. The measurement-noise warning in section 8 is
reinforced: 12.4 is the same disease in a different organ.

---

## 13. The 360-degree test was run — the patch is not the cause

Section 12.3 said one test would discriminate, and that it cost a minute. It was run
headless against the scratch copy; the user's install was not touched.

### 13.1 Harness

`pfalib.py` + `turn_sweep.py`. Improvements over `drive.py`, aimed at section 9's traps:

- **capture is `PrintWindow(PW_RENDERFULLCONTENT)` on the render window**, not F8 into
  `snaps\`. There is no "newest file" to re-read, so trap #2 cannot happen. Verified live:
  three successive grabs of a running frame gave means 102.9 / 100.2 / 91.1.
- the scratch copy's `cheats\*.pnach` were renamed `.OFF`, so the **savestate alone**
  decides whether the patch is in. Confirmed by reading the seven sites out of each state's
  `eeMemory.bin` before use.
- `-batch -nofullscreen`, window client area 1479x859, game area is `y >= 127` under the
  Qt toolbar.

Rotation: `Keyboard/L` = left-stick right. Probing eight candidate keys for 1.2 s each,
`L` and `J` moved the frame by 34.2 and 27.0 mean-abs; everything else 1-8. The compass in
the HUD reads out the heading directly (W at step 0, NW after one 1.2 s press, N by step 6),
so heading is observable per frame.

### 13.2 Result, green map (the user's own savestate position)

17 captures each, `drive/A_proj.p2s` (patched) and `drive/unpatched.p2s` (stock), same key
sequence: `turn/sheet_pairs_a.png`, `turn/sheet_pairs_b.png`.

**At every heading the stock build shows the same artefacts as the patched build.** The
flat green expanse that fills steps 4-10, the white fog bank at steps 2-3, the hard-edged
wedges at steps 0-1 and 11-12 — all present in both, in the same places, moving with the
heading in both. The only difference between the two columns is field of view.

So the answer to 12.3 is **neither A nor B as posed**: the boundary is not glued to the
screen (it sweeps with heading, which kills the view-space cull reading), and it is not
something the patch introduces (stock renders it identically). It is the map, drawn the way
this engine draws it, at this position.

### 13.3 One numeric test was attempted and is invalid — do not reuse it

Cropping the patched frame's central 75% and comparing against the unpatched frame at the
same step index gave no separation at any of the 17 steps (crop error 5-62, full-frame
difference 5-61, never the expected gap). **That is heading drift, not a failed Hor+.** The
two sweeps are separate emulator sessions and the same key sequence does not land on the
same angle twice, so step *i* of one run is not step *i* of the other.

This is section 8 again, in a new costume. A rigorous same-heading A/B needs both frames
from **one** state: rotate, save, then build the patched and unpatched variants of that
saved state — the method section 4.1 already used. Cross-run frame pairing does not work in
this game and no measurement should be built on it.

### 13.4 Standing caveat, now partly addressed

Section 12.5's objection was that everything rested on one camera position. The sweep
covers one position at 17 headings, which is better but still one position. A second map
(North Africa TRAINING, from `states/battle_view.p2s`) is being tested the same way; see
section 14.

---

## 14. Second map (North Africa): geometry is clean, and the only artefact is the known sky gap

### 14.1 Setup

`states/battle_view.p2s` (North Africa TRAINING, Pz III G "521") was verified stock at all
seven sites, then three variants were built and run through `africa_run3.py`:

| state | projection sites | sky site `0017308C` |
|---|---|---|
| `africa/U.p2s` | `80` x6 (stock) | `80` (256.0) |
| `africa/P.p2s` | `40` x6 | `80` (256.0) |
| `africa/P_sky.p2s` | `40` x6 | **`AA` (340.0)** |

Six headings each, measuring the fraction of the frame sitting within 14 of the
framebuffer clear colour `RGB(125,135,205)`.

### 14.2 Result

```
state       clear-colour fraction over six headings
stock       0.000  0.000  0.000  0.000  0.000  0.000
proj only   0.611  0.305  0.212  0.136  0.071  0.264     <- pale blue band
proj + sky  0.000  0.000  0.000  0.000  0.000  0.000     <- gone
```

`africa/sky_compare.png` shows all three at the same heading.

**On this map the widescreen patch produces no geometry corruption at all.** No large
triangles, no mutating polys, terrain down to the horizon, tank and HUD correct — just
wider. The only defect with the six-byte patch is the pale blue in the **top corners**,
which is section 4.2's sky gap: the backdrop camera is still 4:3-wide so the outer sky is
never painted and the clear colour shows through. The one-byte sky fix removes it
completely, measured at 0.000% on all six headings and confirmed visually.

This is the second map and the first one tested from a position that is not the user's own
savestate. Taken with section 13, the "corruption" is **not a general property of the
patch**.

### 14.3 The full seven-byte patch is the one to ship

Sections 4.1 + 4.2 together, i.e. the existing `cheats\F2694B94.pnach.OFF`. The six-byte
subset is not a safe halfway house — it is what produces the sky band.

### 14.4 Unexplained, and worth someone's attention

PCSX2 presents the **stock** run at 995 px of content width and **both patched** runs at
1326 px, identically across all six frames of each run. 1326/995 = 1.3327, i.e. exactly
4/3 — PCSX2 is switching its presentation between 4:3 and 16:9 depending only on six EE
code bytes inside the savestate.

Host display settings are not stored in a savestate and `GS.bin` is byte-identical between
the three states, so there is no obvious mechanism. One lead: `0x002270DC` is the one
patched site that lives in a different code region (`0x227xxx`, not `0x16Exxx`) and may sit
on the display-setup path rather than the world projection. **This is a lead, not a
conclusion** — it has not been tested. Until it is, do not treat "the window got wider" as
evidence that a patch worked.

### 14.5 Two instrument failures this session, both the same shape

1. "Is the tactical map still up?" was tested by looking for black pillarbox bars. The
   patch widens the map screen too, so the bars shrank, the check passed, and thirteen
   frames of a map screen were swept. **Validated on the unpatched path only.**
2. Replaced with a red-ammo-bar count in the bottom quarter, which was first checked
   against frames of both kinds already on disk: 418 on a map screen, 3366-13373 in 3-D.
   That one held — probe 0 caught the map, probe 1 passed after START + X.

The pattern to watch: any detector keyed on screen *geometry* is keyed on the very thing
this patch changes. Key them on content instead.

---

## 15. Patch enabled in the user's install (2026-10-06), and a settings audit

### 15.1 Enabled and verified

`cheats\F2694B94.pnach.OFF` -> `F2694B94.pnach`. The two sibling variants were renamed
`.OFF` as well (`B-no-sky-gap`, `C-engine-fov`) because PCSX2 matches cheat files on the
CRC prefix, so all three could have loaded together and fought each other.

Verified by a fresh boot rather than by the rename succeeding:

```
Found 1 cheats in ...\cheats\F2694B94.pnach.
OSD [LoadPatches]: 7 cheat patches are active.
```

Seven, i.e. the six projection bytes plus the sky fix. `patches\SLES-52984_F2694B94.pnach`
is deliberately left `.OFF` — one source of truth.

### 15.2 The per-game ini is overriding the global one with weaker settings

`gamesettings\SLES-52984_F2694B94.ini` wins over `inis\PCSX2.ini` (section 9 trap #5).
Current state:

| setting | per-game (what runs) | global | note |
|---|---|---|---|
| `Renderer` | **12 = OpenGL** | 15 = D3D12 | confirmed from emulog: `GL_RENDERER`, `OpenGL Context` |
| `upscale_multiplier` | **3** | 6 | |
| `accurate_blending_unit` | **1 (Basic)** | 4 (Full) | |
| `mipmap_hw` | **-1 (auto)** | 2 | |
| `AspectRatio` | 16:9 | 16:9 | correct, the patch needs it |

Hardware is a Ryzen 7 5700X (8c/16t), 64 GB, RTX 4070 Ti SUPER — the GPU is enormously
over-specified for a 2001 PS2 title, so the per-game downgrades buy nothing.

**Renderer = 12 is OpenGL, not D3D12.** The enum is `DX11=3, Null=11, OGL=12, SW=13,
VK=14, DX12=15`. Anyone reading `Renderer = 12` as Direct3D 12 will draw the wrong
conclusion about why something is slow.

### 15.3 No 60 fps patch exists for this game

Searched `PCSX2/pcsx2_patches`, `PeterDelta/PCSX2` and `Gabominated/PCSX2` for both
`SLES-52984` and `F2694B94`: zero hits in all six queries, and a direct listing of
PeterDelta's 685-file `patches/` directory has nothing for it either. The search method was
validated against a control (`SLES-53492` in the same repo returns 4 hits), so the zeros
are real and not an indexing artefact. This also re-confirms section 11.5.

A web search summary states the game is locked at 15-20 fps on both PAL and NTSC-J, which
would be an engine-side cap rather than anything a frame-limiter setting reaches —
**unverified at source**, because wiki.pcsx2.net and forums.pcsx2.net both sit behind a
Cloudflare bot check that returns 403 to fetching and will not clear in a browser. Treat it
as a lead. Raising `FrameratePAL` above 50 does not add frames, it just runs the game fast.

### 15.4 Settings applied (2026-10-06), verified by boot

Backup first: `gamesettings\SLES-52984_F2694B94.ini.bak-20261006`.

```
[EmuCore/GS]         Renderer               12 -> 15    (OpenGL -> Direct3D 12)
                     upscale_multiplier      3 -> 5
                     accurate_blending_unit  1 -> 4      (Basic -> Full)
                     mipmap_hw              -1 -> 2
[EmuCore]            HostFs               true -> false
[EmuCore/Speedhacks] vu1Instant           true -> false
                     vuFlagHack      (absent) -> false   (global had it true)
```

`vuThread` (MTVU) left on; `AspectRatio = 16:9` untouched, the patch needs it.

Verified by mirroring the settings and the pnach into the scratch copy and booting:
`D3D12: Creating a 1479x749 windowed swap chain`, `7 cheat patches are active`, no errors,
no renderer fallback, clean boot to the memory-card dialog. Scratch copy restored afterwards.

**When judging whether the picture is correct, drop `upscale_multiplier` to 1.** Upscaling
manufactures its own edge seams, and this project has already lost time to artefacts that
turned out not to be the game's.

---

## 16. SUBMITTED: PCSX2/pcsx2_patches#790 (2026-10-06)

https://github.com/PCSX2/pcsx2_patches/pull/790 — one file,
`patches/SLES-52984_F2694B94.pnach`, from `murkzuk:panzer-front-ausf-b-widescreen`.

`author=murkz (AI-assisted RE)` — the user's choice, disclosing the method.

### 16.1 What finally cleared it to ship

The blocker was the **binocular / gunsight view**, which was the user's original
complaint ("binos unuseable due to corruption") and had only ever been captured under
OpenGL + Basic blending. Re-checked by the user under D3D12 + Full blending with all seven
bytes: clean. Desert map, binoculars, enemy armour on the horizon, wire and bunker and an
armoured car at close range — correct geometry, sky clean to the frame edges, no wedges.

### 16.2 The renderer, not the patch

Combined with section 14, the picture is now:

**Every "corruption" capture in this project was made with `Renderer = 12` (OpenGL) and
`accurate_blending_unit = 1` (Basic)** — which is what the user's own install ran too,
until it was changed on 2026-10-06. The first clean widescreen frames on both the European
and desert maps arrive immediately after that change.

Not formally proven: the controlled same-savestate comparison across OpenGL / D3D12 /
software is scripted at `renderer_test.py` but has not been run. Run it before stating the
renderer as the cause in writing anywhere public.

### 16.3 Framerate: the emulator is not the bottleneck

OSD on the European map, patched, OpenGL, 1x:

```
FPS: 9.62 [P] | Speed: 100% (T: 100%)
Min 19.94ms | Avg 20.00ms | Max 20.09ms      (= exact 50 Hz PAL presentation)
24951 PRIM | 1646 DRW | 1660 DRWC
```

**Speed is 100 %.** PCSX2 is running the PS2 at full rate; the *game* renders 9.62 fps.
Renderer, upscale and blending therefore cannot raise the framerate — they are not what is
limiting it. The only lever is `EECycleRate` (EE overclock, 130/180/300 %).

`fps_sweep.py` was written to measure EECycleRate 0/1/2/3 plus `vu1Instant` on and off. It
**has not produced numbers** — see 16.4.

### 16.4 TRAP: the emulator dies if the user picks up their controller

Three runs died ~5 s after load with:

```
(VMManager) Pausing...
XInput controller 0 disconnected.
Releasing host memory for virtual systems...
```

The scratch instance and the user's own PCSX2 contend for the single XInput pad; when the
user starts playing, the headless instance loses the controller, pauses and shuts down.
**Never run the harness while the user is playing**, and treat any measurement taken during
an overlapping session as void.

### 16.5 Keyboard + mouse

`inputprofiles\PanzerFront_KBM.ini` in the user's install — opt-in, selected under
Settings > Controllers > Input Profile. Their main config is XInput-only and untouched.

Mouse drives the left stick (gun laying), LMB fires, RMB binoculars (L3), W/S/A/D on the
two track levers per the manual's L2/R2 forward and L1/R1 reverse, E/Q gearbox, 1-4 shell
select on the right stick. Mouse-to-turret verified live: 49.71 and 33.89 mean-abs frame
change for mouse right and left, against a 4.39 noise floor from a deliberately unbound
key — i.e. the control could fail and didn't.

**Unverified:** whether A and D turn the correct way. The manual's wording ("L2 moves the
tank forward left") is ambiguous between "left track" and "veer left". If they are swapped,
exchange the `L2`/`R2` and `L1`/`R1` key pairs.

---

## 17. FPS: measured, and it is a null result. Stop trying settings.

`fps_sweep2.py`, six configurations, three OSD readings each, 18/18 captured. Measured
under the user's own graphics settings (D3D12, 5x, Full blending), same savestate
(`drive/A_proj.p2s`), same scene, varying only EE Cycle Rate and Instant VU1.

```
config        readings            EE Cycle Rate   Instant VU1
ee0_vu1off    9.62  11.54 11.54   100%  (base)   off
ee1_vu1off    9.62   9.61  9.62   130%           off
ee2_vu1off    9.61  10.00 10.00   180%           off
ee3_vu1off    9.62   9.61  9.62   300%           off
ee0_vu1on     9.62  10.00  9.62   100%           on
ee3_vu1on     9.62   9.62 10.00   300%           on

Speed: 100% (T: 100%) on all eighteen readings.
```

### 17.1 Read it correctly

**Nothing beat the baseline.** The highest two readings in the whole sweep (11.54) are in
the unmodified configuration. The within-configuration spread — 9.62 to 11.54, a 20% range
on the baseline alone — is **larger than any difference between configurations**. There is
no signal here, in either direction.

In particular this does **not** show that overclocking hurts. It shows the measurement
cannot resolve anything smaller than its own noise, and nothing on offer is bigger than
that.

### 17.2 What it means

Speed is 100% in every reading: PCSX2 is running the emulated PS2 at full rate and has
spare capacity. The game renders ~10 fps because **that is what the game does** — roughly
one rendered frame per five 50 Hz vsyncs. EE overclock at 130/180/300% does not move it, so
the game is not EE-cycle-limited in a way `EECycleRate` reaches. Instant VU1 does not move
it either.

**No PCSX2 setting will raise this game's framerate.** Renderer, upscale, blending,
speedhacks and EE overclock are all ruled out by measurement now, not by argument. Combined
with section 15.3 (no 60 fps patch exists in any of the three community repos, with a
validated search), the only remaining route is an actual game patch: find the internal
frame cadence in the ELF and change it. That is a reverse-engineering project of the same
size as the widescreen work, not a configuration change.

### 17.3 Side effect: the VU settings cost nothing

`vu1Instant` made no measurable difference. Turning it and `vuFlagHack` off in the user's
install on accuracy grounds therefore costs no performance, and they can stay off.

### 17.4 Method note

This is `feedback_predict_before_measuring` playing out exactly: the noise floor should
have been established first. Three readings per config caught it. One reading per config
would have produced a confident, wrong story — baseline 11.54 against 300% at 9.62 reads
as "overclocking halves your framerate" if you only take the first sample of each.

---

## 18. CORRECTION to section 17: the lever is connected, it only works downward

Section 17 called the EE result a null and concluded "no PCSX2 setting will raise this
game's framerate". The first half of that was reasoning from a test that could only come
back "no change". Running the falsifying direction — **under**clocking the EE — gives a
large, clean, monotonic response.

`underclock_probe.py`, same savestate, same scene, three readings each:

```
EE Cycle Rate      FPS readings            mean
 50%  (-3)         6.00   8.00   5.77      6.59
 75%  (-1)        10.00   7.69   7.69      8.46
100%  ( 0)         9.62  11.54  10.00     10.39
130/180/300%       no change from 100%  (section 17)
```

Speed stayed 100% throughout, so this is the game's internal rate, not emulation
shortfall.

### 18.1 What that shapes into

The EE **is** the bottleneck below 100% — starve it and the framerate falls 37%. Above
100% it stops mattering entirely. That is the signature of a second ceiling that the EE
reaches at roughly stock speed and cannot be pushed past.

The readings cluster hard on **10.00**, and `10.00 = 50 / 5` exactly — one rendered frame
per five PAL fields. The 9.62 and 11.54 values are almost certainly sampling artefacts of
PCSX2's averaging window around a true 10.0 (they are 125/13 and 150/13; the window, not
the game, supplies the 13).

**Working hypothesis: the game renders on a fixed cadence of one frame per five vsyncs,
i.e. a hard-coded ~10 fps.** It fits every observation — pinned at 10 whenever the EE can
make the deadline, falling below only when the EE cannot, and immune to overclocking
because you cannot beat a cadence by arriving early.

**This is a hypothesis, not a measured fact.** It has not been confirmed in the code.

### 18.2 Why this matters

If the cadence is a vsync-wait count in the ELF, it is **patchable** — that is exactly what
a 60 fps patch is. It turns "no 60 fps patch exists" (section 15.3) from a dead end into a
specific, bounded target: find the frame-pacing loop, find the 5, see what happens at 2
or 1.

Scope honestly: a reverse-engineering job comparable to the widescreen work, and games
pinned this way often tie logic to the cadence, so halving it can double animation and
physics rates. Not a quick win, but no longer a mystery.

### 18.3 Note on the load probe (`cap_probe.py`)

13 headings from one boot, reading fps and primitive count together. Inconclusive **as a
load test**: the primitive count only moved 18095 -> 20202 (11%), because terrain dominates
the draw list and rotating the turret barely changes it. fps showed no relationship to
load, but with a swing that small that is not evidence either way. The underclock test is
what carried the conclusion. Do not cite the heading sweep as proof of a cap.

### 18.4 Oddity worth a look

Primitive count goes **up** when the EE is underclocked — 25340 at 50% against 18334 at
100%, with render passes 13 vs 10 and texture-cache entries 17 vs 11. Slower CPU, more
geometry submitted per frame. Possibly a time-based LOD or culling decision misjudging
when frame times stretch. Unexplained; may be a thread worth pulling if anyone revisits
the pacing.

---

## 19. CONFIRMED: the game renders one frame per five vsyncs. 10 fps is hard-coded.

Section 18's hypothesis is now a measured fact. `cadence.py` pauses the VM and uses
**Frame Advance** to step exactly one vsync at a time, comparing the 3-D region of
consecutive captures. This discards PCSX2's averaged FPS counter entirely — that counter
is what produced 9.62 and 11.54, neither of which is 50/N, and it was smearing the answer.

```
CONTROL (two grabs, no advance):  mean 0.000000, max pixel delta 0
steps where any pixel changed:    0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55
gaps:                             [5,5,5,5,5,5,5,5,5,5,5]
gap histogram:                    {5: 11}
mean gap:                         5.000 vsyncs  ->  10.000 fps at 50 Hz
max diff on a NON-change step:    0.000000
```

The result is binary. Every non-rendering step is **bit-identical** — not one pixel moves.
Every fifth step changes. There is no jitter, no load dependence, no ambiguity.

`50 / 5 = 10.000`, which is exactly where the OSD readings clustered.

### 19.1 This explains every earlier observation

- **EE overclock at 130/180/300% does nothing** — you cannot beat a fixed cadence by
  arriving early.
- **EE underclock drops the rate** — the EE stops making the deadline and misses slots.
- **9.62 and 11.54** are artefacts of PCSX2's averaging window around a true 10.000, not
  real framerate variation.
- **No relationship to scene load** (section 18.3) — correct, and now expected.

### 19.2 Method notes

The control matters: two captures with no advance returned a max pixel delta of **0**, so
the instrument can distinguish "same frame held" from "new frame drawn" with certainty.
Without that, a period-5 pattern in noisy captures would have been unconvincing.

The automatic gap analysis inside `cadence.py` did **not** fire — its threshold was set to
`max(0.5, control*4)` and the real per-render change is only ~0.064 mean-abs, because the
scene is nearly static. The pattern was read from the raw diffs and then recomputed at full
precision. **Fix the threshold before reusing that script**: with a control of exactly 0,
any non-zero diff is a change, so the test is `> 0`, not `> 0.5`.

### 19.3 The target is now specific

Find whatever counts those five vsyncs. Candidates: a counter compared against 5 (or
masked), or five calls to a vblank wait per frame.

**Proposed next step, and it uses the harness rather than blind disassembly:** frame-advance
in single vsync steps, saving a savestate at each, then diff `eeMemory.bin` across them and
look for words that cycle with period 5 or change exactly once per five steps. That hands
over the counter's address directly; `refscan.py` then finds what writes it, and the
pacing code is around that write.

---

## 20. CORRECTION to section 19: the `5` is a FLOOR, not a cadence. Patching it does not help.

Section 19 said "10 fps is hard-coded" and section 19.3 proposed finding the constant. The
constant was found, it is exactly where predicted, and **changing it does not raise the
framerate**. Section 19's conclusion was wrong in the way that matters.

### 20.1 What was found (this part stands)

The counter is a `$gp`-relative global at **`0x0026BC2C`** (`gp-31044`), found by diffing
`eeMemory.bin` across 11 consecutive vsync-stepped savestates: out of 8.4M words, 389 were
period-5 and non-constant, 27 of those counter-like, and one was unmistakable —

```
0026BC2C : 4 5 1 2 3 4 5 1 2 3 4
```

`refscan.py` gives **five** references in the whole ELF, all in one function:

```
0017A6F4  lhu  v0,-31044(gp)     read
0017A720  sw   zero,-31044(gp)   reset after the wait
0017A8C0  sw   zero,-31044(gp)   init, different function
0017A9B0  lhu  v0,-31044(gp)     vblank ISR: read
0017A9BC  sw   v0,-31044(gp)     vblank ISR: store counter+1
```

The vblank handler at `0017A9A0` increments it once per vsync. The frame function (a long
run of render `jal`s from ~`0017A630`) ends in a spin loop:

```
0017A6E8  jal  0010C720
0017A6FC  slti v0,v0,5          <- the constant, byte at 0017A6FC (word 28420005)
0017A700  bne  v0,zero,0017A6E8  loop while counter < 5
0017A720  sw   zero,-31044(gp)  reset, then render
```

### 20.2 Why it does not work

Savestates built with that byte set to 2 and to 1 (verified in the file:
`28420002`, `28420001`):

```
immediate   gaps between rendered frames        mean      fps
5 (stock)   5 5 5 5 5 5 5 5 5 5 5              5.000     10.00   locked, zero jitter
2           3 5 5 5 5 6 5 5                    4.875     10.26   jitter appears
1           6 5                                5.500      9.09   (short sample, see below)
```

**The lock disappears and the average does not move.** That is a floor being removed, not a
cadence being changed: with the floor at 5 the frame is held to exactly 5 vsyncs every
time; with it at 1 the game is free to render as fast as it likes and still takes ~5
because **that is what a frame actually costs**.

The floor and the true cost are nearly identical, which is exactly why the stock cadence
looked like a perfect hard lock in section 19.

This also explains section 18 properly: EE underclock hurts because below 100% the EE
becomes the limit; EE overclock does nothing because above 100% the cost is somewhere else
in the pipeline that EE cycles do not buy.

### 20.3 Caveat on the `1` run

It produced only two gaps before a capture failed at step 16, so it is a weak sample on its
own. It is consistent with the `2` run (8 gaps), and the two together support the
conclusion; neither would carry it alone. Re-run with more steps if this is ever revisited.

### 20.4 What this closes, and what it leaves

**Closed:** there is no one-byte framerate patch for this game. The pacing constant exists,
is understood, and is not the binding constraint. Do not spend time on it again.

**Left open:** the ~5 vsyncs of actual per-frame cost. Raising the framerate means reducing
the work — draw distance, object count, LOD — which is game-data territory, not a code
constant. Whether PCSX2's timing model for VU1/VIF/GIF transfers is itself conservative
here is unexamined; `vu1Instant` and MTVU were both tested and neither moved it.

### 20.5 Method note

The error in section 19 was writing the conclusion before running the test that could
falsify it. The period-5 measurement was real and clean, and "a lock at exactly 5" genuinely
does imply a cadence — but it equally fits a floor that matches the cost, and distinguishing
them needed exactly one experiment: change the constant and look. Measure first, write the
section afterwards.

---

## 21. DISPROVED: the renderer is NOT the cause of the green-field artefact

Sections 14.2 and 16.2 proposed that every "corruption" capture was made under
`Renderer = 12` (OpenGL) + Basic blending, and that this was the likely cause. Both flagged
it as unproven pending `renderer_test.py`. That test has now been run and **the hypothesis
is wrong**.

Same savestate (`drive/A_proj.p2s`), three boots, upscale pinned to 1x:

```
pairwise mean abs difference over the 3-D region (0-255)
  ogl_basic   vs d3d12_full   1.084    (3.57% of pixels differ by >24)
  ogl_basic   vs sw_native    1.255    (0.92%)
  d3d12_full  vs sw_native    2.175    (4.37%)

right-hand green wedge, mean RGB / std
  ogl_basic   (17, 35, 16)  38.4
  d3d12_full  (17, 35, 16)  38.4
  sw_native   (17, 35, 16)  38.4
```

The pale wedge and the flat green wedge are present and identical in all three. The
residual 1-2 mean-abs is the OSD overlay, whose text differs per backend.

**`sw_native` is the decisive one.** The software renderer is PCSX2's reference
implementation of the PS2 Graphics Synthesizer and does not use the GPU at all. An artefact
that survives it is in the game's own output.

### 21.1 Where that leaves the artefact

Back to sections 13 and 14, which were measured and stand:

- it is present in **stock** bytes at this position (verified from `eeMemory.bin`, all `80`)
- it appears at **every heading** in a 360-degree sweep, in stock and patched alike
- the **North Africa** map is completely clean, patched, at six headings
- the user's own live play is clean

So it is a property of **that map position**, faithfully reproduced by every renderer, and
is not caused by the widescreen patch, the graphics backend, or the blending setting. What
the engine actually draws there has not been identified and is no longer worth chasing
unless it shows up somewhere it matters.

### 21.2 Why the wrong conclusion looked right

Three things changed at once between the corrupted captures and the first clean ones: the
renderer, the blending unit, **and the scene**. Only the third mattered. The correlation was
real and the inference was reasonable, which is exactly why it needed the test rather than
the argument — and why both earlier sections said so in writing before this was run.

Keep `renderer_test.py`; it is a clean three-way harness and took eight minutes.

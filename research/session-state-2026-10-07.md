# Session state — 2026-10-07

First state capture for this repo. Covers the whole session, since the repo itself was
created today.

---

## 1. Repos

### murkzuk/panzer-front-formats — the deliverable

```
local      K:\panzer-front-formats
remote     https://github.com/murkzuk/panzer-front-formats.git
branch     main          visibility: public
identity   murkz <152478121+murkzuk@users.noreply.github.com>   (noreply, deliberate)
```

Created today. Every commit, oldest first:

```
a1bc35c  04:31  Panzer Front Ausf.B file formats and tools
289a0cb  04:38  README: show what the PZA decoder actually produces
519f189  04:44  PZ: scene graph solved, mesh payload partial
f35027c  04:54  PZ: identify all four vertex streams and the size rule
6461fe7  04:59  PZ: vertex format confirmed; texcoord row corrected
1a4e37a  05:04  PZ: derive the start offset, add an OBJ exporter
7f87ae7  05:08  PZ: fix position/normal split by changepoint; it was not the bug
18c5245  05:11  PZ: sub-mesh delimiter found — three zero rows
fcf2795  05:13  PZ: derive the vertex count structurally — hypothesis confirmed
eea335d  05:18  PZ: no index list; sub-meshes span payloads; matrices are row-vector
db0b0d9  05:29  PZ: the prefix is bounding-volume data, not a primitive table
17ddd29  05:32  research: ELF notes — path strings found, parser not yet
3ad8842  05:34  research: the pointer table is the localised string table
d9d64ae  11:31  PZ solved: AABB table, 2V rule, redundant shell — and three retractions
e1fdcc0  11:38  README: lead with the decoded Panzer III
1216687  11:52  TSET/TENTRY: the vehicle roster and camouflage selector
```

Commits 519f189 through 3ad8842 record a line of investigation that was **largely wrong**
and is retracted in docs/pz.md. They are kept deliberately: the dead ends are the point.

### murkzuk/DeepseekSABoW — the working scratch repo

```
local   K:\DeepseekSABoW     branch main, in sync with origin
```

K:\DeepseekSABoW\pfa\ is the working folder. It holds **many untracked** one-off probe
scripts and extracted game assets that must never be committed. Nothing needs pushing.

### Not repos, but modified

```
D:\pcsx2-v1.7.3137-windows-64bit-AVX2-Qt   the user's PCSX2 install — changed, see section 3
K:\DeepseekSABoW\pcsx2run                  scratch PCSX2 copy, used for all automation
C:\Users\Jeff\.claude\projects\...\memory  memory repo, one entry added
```

---

## 2. Git status right now

```
K:\panzer-front-formats     clean, main == origin/main, nothing ahead or behind
```

22 files tracked including this one. Verified live on GitHub.

---

## 3. Files touched, and why

### Published in this repo

| file | what |
|---|---|
| README.md | Panzer III render leads, then the texture sheet; "no usable game data" wording |
| docs/pak.md | PAK container, 0x48 entries, name at +8 — credits derplayer's 2022 script |
| docs/pza.md | texture format; **corrected** to 1409/1409 after the palette-count field |
| docs/pze.md | message tables, the MessageConv.exe story, the uninitialised-buffer warning |
| docs/pz.md | **rewritten** with the verified spec; "Superseded — do not resurrect" section |
| docs/st.md | **reclassified** from "statistics" to gunnery table |
| docs/tank-tables.md | **new** — TSET/TENTRY roster and camouflage selector |
| docs/formats-status.md | per-extension status table |
| docs/img/*.png | 4 illustrative images (deliberate exception to the no-game-data rule) |
| tools/paklist.py | inventory both archives from the ISO |
| tools/pakx.py | extract by wildcard |
| tools/pza2png.py | texture decoder |
| tools/pz2obj.py | model loader / OBJ exporter |
| tools/pfa_iso.py | ISO9660 reader (dependency) |
| research/pcsx2-widescreen-research.md | widescreen workstream log, sections 12-21 added today |
| research/elf-notes.md | ELF path strings, five failed parser searches, the live thread |
| SLES-52984_F2694B94.pnach | the widescreen patch |
| .gitignore | blocks every asset extension **including \*.txt** — see section 5 |

### The user's PCSX2 install

```
cheats\F2694B94.pnach                    ENABLED (was .OFF) — 7 patches confirmed active
cheats\F2694B94.B-no-sky-gap.pnach.OFF   disabled (CRC-prefix conflict)
cheats\F2694B94.C-engine-fov.pnach.OFF   disabled (same)
inputprofiles\PanzerFront_KBM.ini        NEW, opt-in keyboard+mouse profile
gamesettings\SLES-52984_F2694B94.ini     backup at .bak-20261006
```

Settings now live: Renderer = 15 (D3D12, was 12 = OpenGL), upscale_multiplier = 5 (was 3),
accurate_blending_unit = 4 (was 1), mipmap_hw = 2, HostFs = false, vu1Instant = false,
vuFlagHack = false, vuThread = true, AspectRatio = 16:9.

### Memory

memory/project_panzer_front_widescreen.md added, indexed in MEMORY.md.

---

## 4. Current task

**The decal thread**, handed over from the parallel DeepSeek session. Her brief is
K:\DeepseekSABoW\pfa\DECAL_HANDOVER.md (117 lines) — read it, it is good.

### Exact state

Her section 3 open question — *does a marking appear, and does any variant differ from the
control?* — is **ANSWERED: yes.** I diffed and then looked at the four renders in
K:\DeepseekSABoW\pfa\renders\DECALTEST_110003_*.png:

* all three variants differ from the control: ~1% of pixels, max delta ~185
* **DCL001_0 draws two properly formed Balkenkreuz on the hull side**, correct size and
  position, plus yellow turret numerals below
* DCL002_0 is the magenta TEST-TYPE placeholder family
* comparison image: K:\DeepseekSABoW\pfa\obj\decal_zoom.png

**This corrects her section 2.** She wrote *the .PZ contains no decal geometry and no decal
reference*. The **reference** half holds. The **geometry half does not** — her own geometric
classifier found real decal quads and the crosses land on them correctly.

It also undercuts her "DCL lives under the map tree so these may be map markers" note:
crosses landing correctly on a 3-D hull side is strong evidence they are vehicle decals.

### Next concrete action

1. **Tighten the classifier** using DCL001_0 as ground truth. It currently over-selects:
   diagonal strips across the road wheels take decal texture in DCL002_0 / DCL006_2 and
   should not. Separate genuine decal quads from running-gear geometry that merely happens
   to be thin and planar.
2. **Then the selector** — scenario/nation to DCL sheet. Ranked suspects, hers:
   \D\ME\BRIEFING\*.PZD (57 files, the only place .PZD exists, never opened) first, then
   \D\NE\nn\, then \D\DI\DIV\nn.PZE, then the 19 loose \D\ME\*.PZA.

---

## 5. Decisions and corrections since the start

**Corrections to my own published claims** (all now retracted in-repo by name):

* "sub-meshes are delimited by three all-zero rows" — **wrong**. Measured 99.5% and still
  wrong: an all-black colour stream is a legitimate zero run. OBJ011 node 2 is
  P(30) N(30) C(30, all zero) T(30).
* "phase = 8\*(n%2) is part of the format" — **wrong**. Held at 100% but it is a *symptom* of
  the 24n-byte AABB table landing 8 bytes past a 16-byte boundary when n is odd.
* "±100000 sentinels contaminate the position stream" — **wrong**, that is the AABB table's
  empty-box value, in front of the mesh.
* "the ELF contains no useful strings" — **wrong**, it has 124 path strings.
* PZA "1404 of 1405, font is an exception" — **wrong**, missed the palette **count** field at
  0x0C. It is 1409/1409 with no exceptions.
* The .ST steer I gave DeepSeek (look for small-integer indices in the non-float remainder)
  — **wrong**. It is a -1 sentinel plus ranges in metres and angles in degrees. .ST is a
  gunnery table. The negative result is still useful and is published.

**Things that held up:** no index list in .PZ; matrices are row-vector with translation in
row 3; composition is child-first.

**Deliberate choices:**

* Commit identity is the GitHub **noreply** address, not the real one — a real email in
  public git history is permanent.
* .gitignore blocks \*.txt as well as the binaries. Found by copying real assets in and
  asking git, not by reading the file: .txt was the one gap, and it is where the game's
  dialogue lives.
* Illustrative thumbnails are the one deliberate exception to "no game data", and the README
  says so rather than carrying a claim that is no longer true.
* Dead ends are kept in the docs on purpose.

---

## 6. Known issues

| | |
|---|---|
| ~~**PR #790**~~ | **CLOSED as an issue — out of our hands, stop tracking.** https://github.com/PCSX2/pcsx2_patches/pull/790 is OPEN, MERGEABLE, 0 checks, because a first-time contributor needs a maintainer to approve CI. Nothing is wrong with it and there is no action available to us. Do not re-raise it as a task; if it merges, it merges. |
| ~~**A/D turn direction**~~ | **RESOLVED 2026-10-07 — the mapping is correct, no fix needed.** The user drove it: "it drives and steers but is clunky compared to the analogue levers, as it would be." So the manual's "L2 moves the tank forward left" meant the *left track*, which is how `PanzerFront_KBM.ini` already binds it. The remaining clunkiness is inherent: L2/R2 are pressure-sensitive analogue buttons on the PS2 and the game uses them as proportional track levers, so any keyboard key gives an all-or-nothing lever. That is the control scheme, not the binding. |
| **Duplicate images** | docs/img/pz-panzer3.png and pz-textured.png differ only by a burnt-in caption. One should go. |
| **Decal classifier over-selects** | see section 4 |
| **.PZ parser not found in the ELF** | five search strategies failed, all tabulated in research/elf-notes.md. Live thread: whatever reads the resource table. |
| **Unsolved formats** | decals; .T / .TEX map-prop textures; QPL / SHL; .ST beyond identification |
| **fps** | closed, not fixable. The game renders ~10 fps at 100% emulation speed; no PCSX2 setting and no one-byte patch moves it. |

---

## 7. Resume instructions

```
cd K:\panzer-front-formats && git pull          # should be clean and current
```

Read in this order:

1. K:\DeepseekSABoW\pfa\DECAL_HANDOVER.md — the open task
2. K:\DeepseekSABoW\pfa\PZ_HANDOVER.md — the full .PZ spec (authoritative)
3. docs/pz.md in this repo — the same spec plus what was retracted
4. Section 4 above — where the decal thread actually stands, which is further than her
   handover says

Working folder is K:\DeepseekSABoW\pfa. Her tools (pz.py, pzexport.py, texmap.py,
decaltest2.py) work as-is; decode_pza returns a **tuple** (rgba, w, h) and palette entry 0
is a **transparency key** — do not force alpha to 255 globally.

ISO is D:\Panzer Front Ausf B\s-pfab.iso. Never write to game data. Never run the emulator
while the user is playing — the XInput pad is contended and the headless instance pauses and
exits.

**Method note worth carrying forward:** where a format holds redundant data, test against the
redundancy, not against a statistic. The .PZ AABB table is independent of the mesh, so a
correct decode must reproduce it exactly — that check (5671/5671) settles in seconds what
three separate 99%-plus statistics got wrong.

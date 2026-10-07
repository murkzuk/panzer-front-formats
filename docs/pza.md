# PZA — indexed texture

1409 files, 102 MB. Every texture in the game: vehicle skins, shell sprites, clouds,
briefing maps, national markings, interior panels.

## Layout

```
0x00  u32   bpp flag   0 = 4bpp (16-colour), 1 = 8bpp (256-colour)
0x04  u32   width
0x08  u32   height
0x0C  u32   0
0x10        palette, RGBA8888, 16 or 256 entries
 ...        indexed pixels, 4bpp low-nibble-first, or 8bpp
```

Alpha follows the PS2 convention: **0x80 is fully opaque**, so double it for 8-bit alpha.

Self-check, true for every file: `16 + palette + (width * height * bpp / 8) == filesize`

## Verified

1404 of 1405 decode cleanly and render as correct images. Observed sizes 128x128 up to
512x512, both depths.

The single exception is `\D\FO\font.pza`: header says 256x256 but the file is 73,744
bytes, about 7 KB more than the format allows. Presumably glyph metrics appended after
the bitmap. Not yet decoded.

## Tool

```
python tools/pza2png.py <files...> outdir/
```

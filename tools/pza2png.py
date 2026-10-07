"""Decode Panzer Front .PZA textures.

Deduced layout:
    0x00 u32  bpp flag (0 = 4bpp/16-colour, 1 = 8bpp/256-colour)
    0x04 u32  width
    0x08 u32  height
    0x0C u32  0
    0x10      palette, RGBA8888, 16 or 256 entries (alpha 0x80 = opaque, PS2 convention)
    then      indexed pixels, 4bpp (low nibble first) or 8bpp
Check: 16 + pal + w*h*bpp/8 == file size
"""
import sys, os, struct
from PIL import Image

def decode(path):
    d = open(path, 'rb').read()
    flag, w, h, z = struct.unpack_from('<4I', d, 0)
    for ncol, bpp in ((16, 4), (256, 8)):
        pal_sz = ncol * 4
        px_sz = w * h * bpp // 8
        if 16 + pal_sz + px_sz == len(d):
            pal = []
            for i in range(ncol):
                r, g, b, a = d[16 + i*4: 20 + i*4]
                pal.append((r, g, b, min(255, a * 2)))
            px = d[16 + pal_sz:]
            img = Image.new('RGBA', (w, h))
            out = []
            if bpp == 4:
                for byte in px:
                    out.append(pal[byte & 0x0F]); out.append(pal[byte >> 4])
            else:
                for byte in px:
                    out.append(pal[byte])
            img.putdata(out[:w*h])
            return img, flag, w, h, bpp, ncol
    return None, flag, w, h, None, None

if __name__ == '__main__':
    files = sys.argv[1:-1]; outdir = sys.argv[-1]
    os.makedirs(outdir, exist_ok=True)
    for f in files:
        img, flag, w, h, bpp, ncol = decode(f)
        if img:
            dst = os.path.join(outdir, os.path.basename(f) + '.png')
            img.save(dst)
            print('OK   %-34s flag=%d %4dx%-4d %dbpp/%d  -> %s' % (os.path.basename(f), flag, w, h, bpp, ncol, os.path.basename(dst)))
        else:
            print('FAIL %-34s flag=%d w=%d h=%d size=%d' % (os.path.basename(f), flag, w, h, os.path.getsize(f)))

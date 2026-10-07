"""Extract named files out of D.PAK / D1.PAK straight from the ISO."""
import sys, struct, os, fnmatch
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'K:\DeepseekSABoW')
from pfa_iso import ISO

ISO_PATH = r"D:\Panzer Front Ausf B\s-pfab.iso"
SS = 2048
pattern = sys.argv[1]
outdir  = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

iso = ISO(ISO_PATH)
lba, size = iso.root()
roots = {e['name'].split(';')[0].upper(): (e['lba'], e['size']) for e in iso.listdir(lba, size)}

for pak in ('D.PAK', 'D1.PAK'):
    plba, psz = roots[pak]
    iso.f.seek(plba * SS)
    nfiles, ghl = struct.unpack('<II', iso.f.read(8))
    tbl = iso.f.read(nfiles * 0x48)
    for i in range(nfiles):
        rec = tbl[i * 0x48:(i + 1) * 0x48]
        off, sz = struct.unpack_from('<II', rec, 0)
        raw = rec[8:].split(b'\x00')[0]
        nm = ''.join(chr(c) if 32 <= c < 127 else '.' for c in raw)
        if not fnmatch.fnmatch(nm.upper(), pattern.upper()):
            continue
        iso.f.seek(plba * SS + off)
        data = iso.f.read(sz)
        base = nm.replace(chr(92), '_').lstrip('_')
        dst = os.path.join(outdir, base)
        open(dst, 'wb').write(data)
        print('%-44s %9d -> %s' % (nm, sz, dst))

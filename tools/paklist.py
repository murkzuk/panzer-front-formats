"""List Panzer Front Ausf.B's D.PAK / D1.PAK contents straight from the ISO.

Container format per derplayer's QuickBMS script (gist d825a75a99e9844d9e643596c006099c):
    0x00  u32  file count
    0x04  u32  global header length
    0x08       entry table, 0x48 (72) bytes per entry: u32 offset, u32 size, char name[]
"""
import sys, struct, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'K:\DeepseekSABoW')
from pfa_iso import ISO

ISO_PATH = r"D:\Panzer Front Ausf B\s-pfab.iso"
OUTDIR   = r"K:\DeepseekSABoW\pfa"
SS = 2048

iso = ISO(ISO_PATH)
lba, size = iso.root()
entries = {}
for e in iso.listdir(lba, size):
    entries[e['name'].split(';')[0].upper()] = (e['lba'], e['size'])
for k, v in sorted(entries.items()):
    print('  %-16s lba=%-8d size=%s' % (k, v[0], format(v[1], ',')))

for pak in ('D.PAK', 'D1.PAK'):
    if pak not in entries:
        print('\n%s not in root' % pak); continue
    plba, psz = entries[pak]
    print('\n================ %s  (%s bytes) ================' % (pak, format(psz, ',')))
    iso.f.seek(plba * SS)
    nfiles, ghl = struct.unpack('<II', iso.f.read(8))
    print('file count = %d   global header length = 0x%X' % (nfiles, ghl))
    tbl = iso.f.read(nfiles * 0x48)
    rows, bad = [], 0
    for i in range(nfiles):
        rec = tbl[i * 0x48:(i + 1) * 0x48]
        off, sz = struct.unpack_from('<II', rec, 0)
        raw = rec[8:].split(b'\x00')[0]
        nm = ''.join(chr(c) if 32 <= c < 127 else '.' for c in raw)
        if off > psz or sz > psz:
            bad += 1
        rows.append((off, sz, nm))
    print('entries with out-of-range offset/size: %d' % bad)
    exts = {}
    for off, sz, nm in rows:
        e = nm.rsplit('.', 1)[-1].upper() if '.' in nm else '(none)'
        exts[e] = exts.get(e, 0) + 1
    print('extensions: %s' % dict(sorted(exts.items(), key=lambda x: -x[1])))
    print('total bytes referenced: %s' % format(sum(r[1] for r in rows), ','))
    print('first 30 entries:')
    for off, sz, nm in rows[:30]:
        print('   %08X  %9d  %s' % (off, sz, nm))
    dst = os.path.join(OUTDIR, 'pak_' + pak.replace('.', '_') + '.txt')
    with open(dst, 'w', encoding='utf-8') as fh:
        for off, sz, nm in rows:
            fh.write('%08X\t%d\t%s\n' % (off, sz, nm))
    print('full listing -> %s' % dst)

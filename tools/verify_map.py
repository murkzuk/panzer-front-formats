"""Re-run every claim in docs/maptex.md against the ISO. No arguments.

Prints PASS / FAIL per claim. Four of the original findings were generalised from a
single map and are checked here across the whole set, which is how they were caught.

    python verify_map.py
"""
import sys, os, struct, hashlib
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pzexport import open_iso

B = chr(92)
GRD = B + 'MA' + B + 'GRD' + B

ok = fail = 0


def check(name, passed, detail=''):
    global ok, fail
    if passed:
        ok += 1
    else:
        fail += 1
    print('  %-4s %-44s %s' % ('PASS' if passed else 'FAIL', name, detail))


def safe(s):
    return ''.join(c if 32 <= ord(c) < 127 else '?' for c in s)


def main():
    ent, load = open_iso()
    keys = sorted(k for k in ent if GRD in k)
    zc = [k for k in keys if k.endswith('.ZC')]
    pzc = [k for k in keys if k.endswith('.PZC')]
    tex = [k for k in keys if k.endswith('.TEX')]
    print('ZC %d   PZC %d   TEX %d' % (len(zc), len(pzc), len(tex)))
    print()

    # ---- 1. ZC / PZC pairing -------------------------------------------------
    print('1. .ZC vs .PZC')
    common = [k for k in zc if k[:-3] + '.PZC' in ent]
    differ = [k for k in common if load(k) != load(k[:-3] + '.PZC')]
    check('001 pair is byte-identical',
          load(GRD.join([k for k in zc if k.endswith('001.ZC')][0].rsplit(GRD, 1))) is not None
          and load([k for k in zc if k.endswith(B + '001.ZC')][0])
              == load([k for k in pzc if k.endswith(B + '001.PZC')][0]),
          'the original sample')
    check('ALL pairs byte-identical', not differ,
          '%d of %d pairs differ: %s' % (len(differ), len(common),
                                         [safe(k.split(B)[-1]) for k in differ]))
    orphan_zc = [k for k in zc if k[:-3] + '.PZC' not in ent]
    orphan_pz = [k for k in pzc if k[:-4] + '.ZC' not in ent]
    print('       orphans: .ZC only %s | .PZC only %s'
          % ([safe(k.split(B)[-1]) for k in orphan_zc],
             [safe(k.split(B)[-1]) for k in orphan_pz]))
    print()

    # ---- 2. header ----------------------------------------------------------
    print('2. grid header')
    hdrs = {}
    for k in zc + pzc:
        d = load(k)
        hdrs.setdefault((struct.unpack_from('<6I', d, 0), len(d)), []).append(k)
    check('header identical in all files', len(hdrs) == 1,
          '%d distinct classes' % len(hdrs))
    for (h, n), v in sorted(hdrs.items(), key=lambda x: -len(x[1])):
        print('       %-32s size %-9d %2d files' % (str(h), n, len(v)))
    sizes_ok = all(h[0] + h[2] * h[3] * 3 == n for (h, n) in hdrs)
    check('header_size + w*h*3 == filesize', sizes_ok, 'for every class')
    steps = sorted(set((h[2], h[1], h[1] * h[2]) for (h, n) in hdrs))
    print('       cell-step hypothesis: ' +
          ' | '.join('%d cells x %d = %d' % s for s in steps))
    if len(steps) > 1:
        spread = max(s[2] for s in steps) / min(s[2] for s in steps) - 1
        check('dim * field1 is near-constant', spread < 0.05,
              'spread %.1f%% across grid sizes' % (100 * spread))
    print()

    # ---- 3. duplicates ------------------------------------------------------
    print('3. duplicate maps')
    md5 = {k: hashlib.md5(load(k)).hexdigest() for k in zc}
    c = Counter(md5.values())
    dup = [sorted(safe(k.split(B)[-1]) for k in zc if md5[k] == h)
           for h, n in c.items() if n > 1]
    check('22 distinct of 23 .ZC', len(c) == 22, 'duplicate group %s' % dup)
    print()

    # ---- 4. plane-major vs interleaved --------------------------------------
    print('4. body layout')
    k001 = [k for k in zc if k.endswith(B + '001.ZC')][0]
    d = load(k001)
    h = struct.unpack_from('<6I', d, 0)
    w, ht = h[2], h[3]
    N = w * ht
    body = np.frombuffer(d, dtype=np.uint8, offset=h[0])
    pm = [body[i * N:(i + 1) * N] for i in range(3)]
    il = [body.reshape(-1, 3)[:, i] for i in range(3)]

    def adj(a):
        return float(np.abs(np.diff(a.astype(np.int16))).mean())

    pm_spread = max(a.mean() for a in pm) - min(a.mean() for a in pm)
    il_spread = max(a.mean() for a in il) - min(a.mean() for a in il)
    check('plane-major planes differ from each other', pm_spread > 10,
          'mean spread %.2f' % pm_spread)
    check('interleaved channels are near-identical', il_spread < 1.0,
          'mean spread %.2f  <- the tell that interleaved is wrong' % il_spread)
    for i, a in enumerate(pm):
        g = a.reshape(ht, w).astype(np.int16)
        print('       plane %d  min %3d max %3d mean %7.2f  adjdiff x %6.3f y %6.3f  '
              'zero%% %5.1f  distinct %d'
              % (i, a.min(), a.max(), a.mean(),
                 np.abs(np.diff(g, axis=1)).mean(), np.abs(np.diff(g, axis=0)).mean(),
                 100.0 * (a == 0).mean(), len(np.unique(a))))
    print()

    # ---- 5. the planes ------------------------------------------------------
    print('5. plane identification (map 001)')
    hm = pm[1].reshape(ht, w).astype(np.int16)
    check('plane 1 smooth in BOTH axes',
          np.abs(np.diff(hm, axis=1)).mean() < 1 and np.abs(np.diff(hm, axis=0)).mean() < 1,
          'adjdiff x %.3f y %.3f' % (np.abs(np.diff(hm, axis=1)).mean(),
                                     np.abs(np.diff(hm, axis=0)).mean()))
    f = [p.astype(np.float64) for p in pm]
    r0 = np.corrcoef(f[0], f[1])[0, 1]
    r2 = np.corrcoef(f[2], f[1])[0, 1]
    r02 = np.corrcoef(f[0], f[2])[0, 1]
    check('planes 0 and 2 uncorrelated with height', abs(r0) < 0.2 and abs(r2) < 0.2,
          'pearson %.3f / %.3f' % (r0, r2))
    check('planes 0 and 2 correlated with each other', r02 > 0.4, 'pearson %.3f' % r02)
    check('plane 0 is SPARSE (71% zero)', (pm[0] == 0).mean() > 0.5,
          'actually %.1f%% zero -> plane 0 is DENSE' % (100 * (pm[0] == 0).mean()))
    check('plane 2 is sparse', (pm[2] == 0).mean() > 0.5,
          '%.1f%% zero' % (100 * (pm[2] == 0).mean()))
    print()

    # ---- 6. plane 2 across maps --------------------------------------------
    print('6. plane 2 is not populated on every map')
    for nm in ('001', '011', '018', '020'):
        hits = [k for k in zc if k.endswith(B + nm + '.ZC')]
        if not hits:
            continue
        dd = load(hits[0])
        hh = struct.unpack_from('<6I', dd, 0)
        NN = hh[2] * hh[3]
        bb = np.frombuffer(dd, dtype=np.uint8, offset=hh[0])
        p2 = bb[2 * NN:3 * NN]
        print('       %s  %dx%d  plane2 zero%% %5.1f  distinct %d'
              % (nm, hh[2], hh[3], 100.0 * (p2 == 0).mean(), len(np.unique(p2))))
    print()

    # ---- 7. 002 vs 003 ------------------------------------------------------
    print('7. maps 002 vs 003')
    a = load([k for k in zc if k.endswith(B + '002.ZC')][0])
    b = load([k for k in zc if k.endswith(B + '003.ZC')][0])
    check('002 and 003 are the same terrain', a == b, 'they are NOT identical')
    if a != b:
        da = np.frombuffer(a, dtype=np.uint8, offset=24)
        db = np.frombuffer(b, dtype=np.uint8, offset=24)
        for i in range(3):
            pa, pb = da[i * N:(i + 1) * N], db[i * N:(i + 1) * N]
            print('       plane %d  %d differing bytes (%.3f%%)'
                  % (i, int((pa != pb).sum()), 100.0 * (pa != pb).mean()))
    print()

    # ---- 8. TEX header ------------------------------------------------------
    print('8. MAP*.TEX header is an offset chain')
    th = {}
    for k in tex:
        t = load(k)
        th.setdefault(struct.unpack_from('<5I', t, 0), []).append((k, len(t)))
    check('TEX header identical in all 20', len(th) == 1, '%d distinct' % len(th))
    for hh, v in th.items():
        print('       %s  -> w,h = %d,%d' % (str(hh), hh[0] & 0xFFFF, hh[0] >> 16))
        chain = [hh[1], hh[1] + 8192, hh[1] + 8192 + 2048, hh[1] + 8192 + 2048 + 512]
        check('offsets chain by exact level sizes', list(hh[1:]) == chain,
              '%s vs computed %s' % (list(hh[1:]), chain))
        print('       tail at 0x%X, %d bytes in MAP001' % (hh[4], v[0][1] - hh[4]))
    print()

    print('%d passed, %d failed' % (ok, fail))
    print('A FAIL here is the point: those four lines are the published corrections.')


if __name__ == '__main__':
    main()

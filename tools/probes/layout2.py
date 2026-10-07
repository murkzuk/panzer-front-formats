import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
d=load(D+'001.ZC'); body=np.frombuffer(d[24:],dtype=np.uint8)
P=[body[i*W*H:(i+1)*W*H].reshape(H,W) for i in range(3)]
p2=P[2]
print('=== plane 2 as two nibbles ===')
lo=p2&0x0F; hi=(p2>>4)&0x0F
print('   low  nibble: %s' % dict(sorted(Counter(lo.ravel().tolist()).items())))
print('   high nibble: %s' % dict(sorted(Counter(hi.ravel().tolist()).items())))
print()
print('   distinct (hi,lo) pairs: %d' % len(set(map(tuple,np.unique(p2.reshape(-1,1),axis=0).tolist()))))
print('   joint top 12: %s' % Counter(zip(hi.ravel().tolist(),lo.ravel().tolist())).most_common(12))
print()
print('=== plane 2 as bit flags (which bits are set?) ===')
for b in range(5):
    print('   bit %d set in %5.2f%% of cells' % (b,100*np.mean((p2>>b)&1)))
print()
print('=== plane 0: relationship to plane 2 ===')
p0=P[0]
print('   p0 >> 4 range %d..%d ; p2 high nibble range %d..%d' % ((p0>>4).min(),(p0>>4).max(),hi.min(),hi.max()))
print('   equal: %.1f%%' % (100*np.mean((p0>>4)==hi)))
print('   p0 & 15 vs p2 low nibble equal: %.1f%%' % (100*np.mean((p0&15)==lo)))
print('   p0 dist: %s' % dict(sorted(Counter((p0>>4).ravel().tolist()).items())[:12] if False else sorted(Counter((p0>>4).ravel().tolist()).items())))
print()
print('=== terrain visual grid candidates ===')
n=468
for div in (2,3,4,6,9,12,13,18,26,36,39,52,78,117,156,234):
    print('   468/%3d = %6.2f   (vs texture 128 -> ratio %.3f)' % (div,n/div,128/(n/div)))
print()
print('=== does plane 2 vary at a scale matching a 128 or 117 grid? ===')
def blockvar(p,bs):
    hh,ww=p.shape
    m=hh//bs*bs
    q=p[:m,:m].reshape(m//bs,bs,m//bs,bs).astype(np.float64)
    return float(q.var(axis=(1,3)).mean())
for bs in (3,4,6,9,13,18,26,39,52,117,156,234):
    if 468%bs==0:
        print('   block %3d (%d blocks across) : within-block variance %8.2f' % (bs,468//bs,blockvar(p2,bs)))

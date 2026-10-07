import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
d=load(D+'001.ZC'); body=np.frombuffer(d[24:],dtype=np.uint8)
P=[body[i*W*H:(i+1)*W*H].reshape(H,W) for i in range(3)]
for i in (0,2):
    p=P[i]
    c=np.bincount(p.ravel(),minlength=256)
    nz=[(int(v),int(n)) for v,n in enumerate(c) if n]
    print('=== plane %d : %d distinct values, range %d..%d ===' % (i,len(nz),p.min(),p.max()))
    print('   top 10: %s' % sorted(nz,key=lambda x:-x[1])[:10])
    print('   share of the single commonest value: %.1f%%' % (100*max(n for _,n in nz)/p.size))
    # spatial: blobs or lines?
    dx=np.abs(np.diff(p.astype(np.int32),axis=1))
    dy=np.abs(np.diff(p.astype(np.int32),axis=0))
    print('   adjacent-diff  x %.2f  y %.2f  (low = large uniform regions)' % (dx.mean(),dy.mean()))
    # autocorrelation at a few lags to find a tile period
    f=p.astype(np.float64)-p.mean()
    ac=[]
    for lag in (2,3,4,6,8,12,13,16,18,26,36,39,52,117,128,156,234):
        if lag>=W: continue
        a=f[:,:-lag].ravel(); b=f[:,lag:].ravel()
        dnm=(np.linalg.norm(a)*np.linalg.norm(b))
        ac.append((lag, float(np.dot(a,b)/dnm) if dnm>0 else 0.0))
    print('   autocorrelation (x): %s' % ' '.join('%d:%.3f'%(l,v) for l,v in ac))
    print()
print('=== do the layout planes correlate with the heightmap or each other? ===')
for i,j in ((0,1),(2,1),(0,2)):
    a=P[i].astype(np.float64).ravel(); b=P[j].astype(np.float64).ravel()
    print('   plane %d vs %d : pearson %.3f' % (i,j,float(np.corrcoef(a,b)[0,1])))
print()
print('=== are plane 0 and plane 2 related? (e.g. same info at different resolution) ===')
print('   plane0 // 8 vs plane2 equal: %.1f%%' % (100*np.mean((P[0]//8)==P[2])))
print('   plane0 >> 3 mean %.1f ; plane2 mean %.1f' % ((P[0]>>3).mean(),P[2].mean()))
print()
print('=== grid divisors of 468 ===')
n=468
print('   468 = 2^2 x 3^2 x 13 ; divisors: %s' % [x for x in range(1,235) if n%x==0])
print('   468/128 = %.4f  (texture mapping is not an integer ratio)' % (n/128))

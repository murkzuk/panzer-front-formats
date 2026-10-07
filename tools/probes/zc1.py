import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
for nm in ('001.ZC','001.PZC'):
    d=load(D+nm); n=len(d)
    print('=== %s : %d bytes ===' % (nm,n))
    print('   hex +0:  %s' % ' '.join('%02X'%b for b in d[:48]))
    u32=np.frombuffer(d[:64],dtype='<u4'); u16=np.frombuffer(d[:64],dtype='<u2'); f32=np.frombuffer(d[:64],dtype='<f4')
    print('   u32: %s' % [int(x) for x in u32[:12]])
    print('   u16: %s' % [int(x) for x in u16[:16]])
    print('   f32: %s' % [round(float(x),4) for x in f32[:12]])
    print('   offsets < size: %s' % [(i,int(v)) for i,v in enumerate(u32[:24]) if 0<v<n][:10])
    # dimensions?
    for w,h in ((128,128),(64,64),(256,256),(128,64)):
        for bpp in (8,16,32):
            if 16+w*h*bpp//8==n: print('   == 16 + %dx%d %dbpp'%(w,h,bpp))
            if w*h*bpp//8==n: print('   == %dx%d %dbpp'%(w,h,bpp))
    print()
print('=== .ZC vs .PZC : are they the same data? ===')
z=load(D+'001.ZC'); p=load(D+'001.PZC')
print('   identical? %s   differing bytes: %d' % (z==p, sum(1 for i in range(min(len(z),len(p))) if z[i]!=p[i])))
print()
print('=== all 23 ZC/PZC sizes and first u32 ===')
zs=sorted(k for k in ent if k.startswith(D) and (k.endswith('.ZC') or k.endswith('.PZC')))
for k in zs[:10]:
    dd=load(k); u=struct.unpack_from('<4I',dd,0)
    print('   %-40s %8d  %s' % (k.split(B)[-1],ent[k][1],u))
print()
print('=== georeference hunt: any plausible world coordinates? ===')
d=load(D+'001.ZC')
f=np.frombuffer(d[:min(len(d),400000)//4*4],dtype='<f4')
ok=np.isfinite(f)&(np.abs(f)>1)&(np.abs(f)<20000)
print('   finite floats in 1..20000: %.1f%%' % (100*ok.mean()))
print('   sample: %s' % np.round(f[ok][:16],2).tolist())

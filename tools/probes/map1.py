import sys, struct
from collections import Counter
import numpy as np
sys.path.insert(0,'K:/DeepseekSABoW/pfa')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
print('=== \\D\\MA\\GRD contents ===')
grd=[(k.split(B)[-1],ent[k][1]) for k in sorted(ent) if k.startswith(B+'D'+B+'MA'+B+'GRD'+B)]
byext=Counter()
for n,s in grd: byext[n.rsplit('.',1)[-1]]+=1
print('   %d files; by ext: %s' % (len(grd),dict(byext.most_common())))
for ext in ('TEX','PZC','ZC','PZA'):
    x=[ (n,s) for n,s in grd if n.endswith('.'+ext)][:6]
    print('   %-4s: %s' % (ext,[(n,s) for n,s in x]))
print()
k=B+'D'+B+'MA'+B+'GRD'+B+'MAP001.TEX'
d=load(k); n=len(d)
print('=== MAP001.TEX : %d bytes ===' % n)
# factorisation
m=n; fac=[]
p=2
while p*p<=m:
    while m%p==0: fac.append(p); m//=p
    p+=1
if m>1: fac.append(m)
print('   factorisation: %s' % ' x '.join(str(x) for x in fac))
for w,h in ((128,128),(256,256),(512,512),(64,64),(128,64)):
    for bpp in (4,8,16):
        need=16+w*h*bpp//8
        if need==n: print('   == 16 + %dx%d %dbpp' % (w,h,bpp))
        need2=w*h*bpp//8
        if need2==n: print('   == %dx%d %dbpp (no header)' % (w,h,bpp))
print()
print('   first 128 bytes hex:')
for i in range(0,128,16):
    print('      +%03d  %s' % (i,' '.join('%02X'%b for b in d[i:i+16])))
print()
u16=np.frombuffer(d[:256],dtype='<u2')
u32=np.frombuffer(d[:256],dtype='<u4')
print('   first 32 u16: %s' % [int(x) for x in u16[:32]])
print('   first 32 u32: %s' % [int(x) for x in u32[:32]])
print('   first 16 f32: %s' % [round(float(x),4) for x in np.frombuffer(d[:64],dtype='<f4')])
print()
print('   u32 values in the first 512 bytes that are < filesize (offset candidates): %s'
      % [ (i,int(v)) for i,v in enumerate(np.frombuffer(d[:512],dtype='<u4')) if 0<v<n ][:20])

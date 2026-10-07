import sys, struct
import numpy as np
sys.path.insert(0,'K:/DeepseekSABoW/pfa')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
maps=[(k.split(B)[-1],ent[k][1],k) for k in sorted(ent) if k.startswith(B+'D'+B+'MA'+B+'GRD'+B+'MAP') and k.endswith('.TEX')]
print('=== headers of all %d MAP*.TEX ===' % len(maps))
print('%-14s %9s  %-22s %-30s %s' % ('file','size','hdr u32[0..4]','palette first/last entry','sections'))
for nm,sz,k in maps:
    d=load(k)
    h=struct.unpack_from('<5I',d,0)
    pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)
    secs=[96,h[2],h[3],h[4],sz]
    sizes=[secs[i+1]-secs[i] for i in range(len(secs)-1)]
    print('%-14s %9d  %-22s (%3d,%3d,%3d)-(%3d,%3d,%3d)  %s' % (nm,sz,str(h),
          pal[0][0],pal[0][1],pal[0][2],pal[15][0],pal[15][1],pal[15][2],
          ' '.join(str(x) for x in sizes)))
print()
print('=== do all 20 share the same header shape? ===')
shapes={}
for nm,sz,k in maps:
    d=load(k); h=struct.unpack_from('<5I',d,0)
    shapes.setdefault(tuple(h[:5]),[]).append(nm)
for s,ns in shapes.items():
    print('   %s  x%d  %s' % (str(s),len(ns),ns[:6]))
print()
print('=== palette family per map (mean RGB of the 16 entries) ===')
for nm,sz,k in maps[:20]:
    d=load(k)
    pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)[:,:3].astype(float)
    mono=float(np.abs(pal[:,0]-pal[:,2]).mean())
    print('   %-14s mean %s   R-B spread %.1f' % (nm,np.round(pal.mean(axis=0),0).tolist(),mono))

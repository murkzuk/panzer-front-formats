import sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0,'K:/DeepseekSABoW/pfa')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
d=load(B+'D'+B+'MA'+B+'GRD'+B+'MAP001.TEX'); n=len(d)
W=H=128
pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)
print('palette (16 RGBA):')
for i,c in enumerate(pal): print('   [%2d] %3d %3d %3d %3d' % (i,c[0],c[1],c[2],c[3]))
raw=np.frombuffer(d[96:8288],dtype=np.uint8).reshape(H,W//2)
idx=np.empty((H,W),dtype=np.uint8)
idx[:,0::2]=raw&0x0F
idx[:,1::2]=(raw>>4)&0x0F
print()
print('4bpp index map 128x128: distinct indices %d ; used: %s' % (len(np.unique(idx)),sorted(np.unique(idx).tolist())))
print('index histogram: %s' % dict(zip(*[x.tolist() for x in np.unique(idx,return_counts=True)])))
rgba=pal[idx]
print()
print('decoded top colours: %s' % [tuple(int(v) for v in c) for c in pal[np.argsort(-np.bincount(idx.ravel(),minlength=16))][:6]])
Image.fromarray(rgba,'RGBA').resize((512,512),Image.NEAREST).save('K:/DeepseekSABoW/pfa/renders/MAP001_4bpp.png')
print('wrote MAP001_4bpp.png')
print()
print('=== what is in the other sections? ===')
for off,label in ((32,'palette'),(96,'idx map'),(8288,'B'),(10336,'C'),(10848,'D')):
    seg=d[off:off+48]
    print('  +%-6d %-8s %s' % (off,label,' '.join('%02X'%b for b in seg)))
    u=np.frombuffer(d[off:off+32],dtype='<u4')
    f=np.frombuffer(d[off:off+32],dtype='<f4')
    print('           u32 %s' % [int(x) for x in u[:8]])
    print('           f32 %s' % [round(float(x),3) for x in f[:8]])
print()
print('=== section sizes ===')
secs=[(0,96),(96,8288),(8288,10336),(10336,10848),(10848,n)]
for a,b in secs:
    print('   %7d .. %7d  = %8d bytes  (%s)' % (a,b,b-a,'/128 = %.2f'%((b-a)/128) if (b-a)%128 else '= %d x 128'%((b-a)//128)))

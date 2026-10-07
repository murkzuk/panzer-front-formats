import sys, struct
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
d=load(D+'001.ZC')
h=struct.unpack_from('<6I',d,0)
print('header: %s' % (h,))
W,H=h[2],h[3]
n=24
print('24 + %d x %d x 3 = %d   (file %d)  match=%s' % (W,H,24+W*H*3,len(d),24+W*H*3==len(d)))
cell=np.frombuffer(d[n:n+W*H*3],dtype=np.uint8).reshape(H,W,3)
print()
print('=== per-plane statistics (which is the heightmap?) ===')
names=['byte0','byte1','byte2']
for i in range(3):
    p=cell[:,:,i].astype(np.int32)
    dx=np.abs(np.diff(p,axis=1)).mean()
    dy=np.abs(np.diff(p,axis=0)).mean()
    print('  %s: min %3d max %3d mean %6.1f std %6.1f   adj-diff x %.2f  y %.2f   distinct %d'
          % (names[i],p.min(),p.max(),p.mean(),p.std(),dx,dy,len(np.unique(p))))
print()
print('  (a heightfield is SMOOTH: small adjacent-difference)')
print()
# combine byte0+byte1 as u16 height?
u16=cell[:,:,0].astype(np.int32)|(cell[:,:,1].astype(np.int32)<<8)
print('  byte0|byte1<<8 as u16: min %d max %d mean %.1f std %.1f  adj-diff x %.2f y %.2f'
      % (u16.min(),u16.max(),u16.mean(),u16.std(),np.abs(np.diff(u16,axis=1)).mean(),np.abs(np.diff(u16,axis=0)).mean()))
# which plane is smoothest -> height
sm=[np.abs(np.diff(cell[:,:,i].astype(np.int32),axis=1)).mean()+np.abs(np.diff(cell[:,:,i].astype(np.int32),axis=0)).mean() for i in range(3)]
hi=int(np.argmin(sm))
print()
print('  SMOOTHEST plane = byte%d  -> the heightfield' % hi)
hm=cell[:,:,hi]
print('  height range: %d .. %d' % (hm.min(),hm.max()))
# render it
v=hm.astype(np.float64); v=(v-v.min())/max(1e-9,(v.max()-v.min()))
im=Image.fromarray((v*255).astype(np.uint8)).resize((560,560),Image.NEAREST)
im.save('K:/DeepseekSABoW/pfa/renders/TERRAIN_height_001.png')
print('  wrote TERRAIN_height_001.png')
# the other two planes
for i in range(3):
    if i==hi: continue
    p=cell[:,:,i]
    print('  plane byte%d: top values %s' % (i,np.bincount(p.ravel(),minlength=256).argsort()[-6:][::-1].tolist()))
# composite of the two non-height planes
oth=[i for i in range(3) if i!=hi]
rgb=np.stack([cell[:,:,oth[0]],cell[:,:,oth[1]],np.zeros_like(hm)],axis=2)
Image.fromarray(rgb).resize((560,560),Image.NEAREST).save('K:/DeepseekSABoW/pfa/renders/TERRAIN_planes_001.png')
print('  wrote TERRAIN_planes_001.png (the two non-height planes as R,G)')

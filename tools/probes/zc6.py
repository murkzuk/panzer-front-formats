import sys, struct
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
d=load(D+'001.ZC')
h=struct.unpack_from('<6I',d,0)
W=H=468
body=np.frombuffer(d[24:],dtype=np.uint8)
print('header %s ; body %d = 3 x %d' % (h,len(body),W*H))
print()
planes=[]
for i in range(3):
    p=body[i*W*H:(i+1)*W*H].reshape(H,W)
    planes.append(p)
    ad=0.5*(np.abs(np.diff(p.astype(np.int32),axis=1)).mean()+np.abs(np.diff(p.astype(np.int32),axis=0)).mean())
    print('plane %d: min %3d max %3d mean %6.2f std %6.2f  adj-diff %6.2f  distinct %3d' %
          (i,p.min(),p.max(),p.mean(),p.std(),ad,len(np.unique(p))))
print()
print('  (adj-diff near 0 = extremely smooth gradient; a heightfield should be low but not ~0)')
print()
tiles=[]
for i,p in enumerate(planes):
    v=p.astype(np.float64)
    lo,hi=v.min(),v.max()
    n=(v-lo)/max(1e-9,hi-lo)
    im=Image.fromarray((n*255).astype(np.uint8)).convert('RGB').resize((420,420),Image.NEAREST)
    tiles.append((('plane %d  %d..%d'%(i,lo,hi)),im))
# also a colour composite
comp=np.stack([planes[0],planes[1],planes[2]],axis=2)
tiles.append(('RGB composite',Image.fromarray(comp).resize((420,420),Image.NEAREST)))
sheet=Image.new('RGB',(420*4+50,420+30),(20,20,24)); dr=ImageDraw.Draw(sheet)
for i,(nm,im) in enumerate(tiles):
    x=10+i*420
    dr.text((x,10),nm,fill=(245,245,140))
    sheet.paste(im,(x,28))
sheet.save('K:/DeepseekSABoW/pfa/renders/ZC_planes_001.png')
print('wrote ZC_planes_001.png')
print()
print('=== is plane 0 the heightfield? vertical/horizontal profile ===')
p0=planes[0]
print('   row 234 (middle), cols 0,60,120,...: %s' % p0[234,::60].tolist())
print('   col 234 (middle), rows 0,60,120,...: %s' % p0[::60,234].tolist())
print()
print('=== do the three planes differ between maps? (001 vs 002) ===')
d2=load(D+'002.ZC'); b2=np.frombuffer(d2[24:],dtype=np.uint8)
for i in range(3):
    a=body[i*W*H:(i+1)*W*H]; b=b2[i*W*H:(i+1)*W*H]
    print('   plane %d: identical=%s  mean abs diff=%.2f' % (i,a.tobytes()==b.tobytes(),np.abs(a.astype(int)-b.astype(int)).mean()))

import sys, struct
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
hm=np.frombuffer(load(D+'001.ZC')[24:],dtype=np.uint8)[W*H:2*W*H].reshape(H,W).astype(np.float64)
# texture
d=load(D+'MAP001.TEX')
pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)
raw=np.frombuffer(d[96:8288],dtype=np.uint8).reshape(128,64)
idx=np.empty((128,128),dtype=np.uint8)
idx[:,0::2]=raw&0x0F; idx[:,1::2]=(raw>>4)&0x0F
lum=pal[idx][:,:,:3].astype(np.float64).mean(axis=2)
print('heightmap %dx%d ; texture %dx%d ; ratio %.4f' % (H,W,128,128,468/128))
print()
def downsample(a,out):
    h,w=a.shape
    ys=(np.arange(out)*h//out); xs=(np.arange(out)*w//out)
    ys2=np.append(ys[1:],h); xs2=np.append(xs[1:],w)
    r=np.zeros((out,out))
    for i in range(out):
        for j in range(out):
            r[i,j]=a[ys[i]:ys2[i],xs[j]:xs2[j]].mean()
    return r
hm128=downsample(hm,128)
print('=== correlation: heightmap (downsampled to 128x128) vs texture luminance ===')
def pear(a,b):
    a=a.ravel(); b=b.ravel()
    return float(np.corrcoef(a,b)[0,1])
print('   pearson(height, texture lum)      = %+.3f' % pear(hm128,lum))
print('   pearson(height, texture palette idx) = %+.3f' % pear(hm128,idx.astype(float)))
for sh in ((0,0),(32,32),(64,64),(96,96),(-32,-32)):
    a=np.roll(np.roll(hm128,sh[0],axis=0),sh[1],axis=1)
    print('   pearson(height rolled %s, lum)    = %+.3f' % (str(sh),pear(a,lum)))
print()
print('=== is the texture self-tiling? (edge continuity) ===')
lr=np.abs(lum[:,0]-lum[:,-1]).mean()
tb=np.abs(lum[0,:]-lum[-1,:]).mean()
print('   mean |left-right edge| = %.2f   |top-bottom edge| = %.2f   (low = tiles)' % (lr,tb))
print('   interior mean |adjacent diff| = %.2f' % (np.abs(np.diff(lum,axis=1)).mean()))
print()
print('=== spatial frequency: is it a big picture or fine detail? ===')
def ac(a,lag,axis):
    f=a-a.mean()
    if axis==1: x,y=f[:,:-lag],f[:,lag:]
    else: x,y=f[:-lag,:],f[lag:,:]
    return float(np.dot(x.ravel(),y.ravel())/(np.linalg.norm(x)*np.linalg.norm(y)))
print('   texture   ac(1)=%.3f ac(4)=%.3f ac(16)=%.3f ac(32)=%.3f ac(64)=%.3f' % tuple(ac(lum,l,1) for l in (1,4,16,32,64)))
print('   heightmap ac(1)=%.3f ac(4)=%.3f ac(16)=%.3f ac(32)=%.3f ac(64)=%.3f' % tuple(ac(hm128,l,1) for l in (1,4,16,32,64)))
print()
print('   (if the texture were a 1:1 albedo of the terrain its autocorrelation would track the heightmap)')

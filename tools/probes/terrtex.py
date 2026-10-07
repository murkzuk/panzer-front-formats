import sys, struct
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
hm=np.frombuffer(load(D+'001.ZC')[24:],dtype=np.uint8)[W*H:2*W*H].reshape(H,W).astype(np.float64)
d=load(D+'MAP001.TEX')
pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)
raw=np.frombuffer(d[96:8288],dtype=np.uint8).reshape(128,64)
idx=np.empty((128,128),dtype=np.uint8)
idx[:,0::2]=raw&0x0F; idx[:,1::2]=(raw>>4)&0x0F
tex=pal[idx][:,:,:3].astype(np.float64)/255.0
th,tw=tex.shape[:2]
K=0.10           # derived height scale
TILE=8           # terrain cells per texture repeat
S=3
h0=hm[::S,::S]; hh,ww=h0.shape
XX,ZZ=np.meshgrid(np.arange(ww)*S, np.arange(hh)*S)   # cell coords
hv=(h0-h0.min())*K
sx=(XX-ZZ)*np.cos(np.deg2rad(38.0)); base=(XX+ZZ)*np.sin(np.deg2rad(38.0))*0.5
sy=base-hv
PW,PH=1180,760
sc=min((PW-20)/(sx.max()-sx.min()),(PH-20)/(sy.max()-sy.min()))
PX=sx*sc+(10-sx.min()*sc); PY=sy*sc+(10-sy.min()*sc)
img=np.full((PH,PW,3),0.60); zb=np.full((PH,PW),1e30)
L=np.array([-0.5,0.62,-0.60]); L=L/np.linalg.norm(L)
gy,gx=np.gradient(h0)
for j in range(hh-1):
    for i in range(ww-1):
        p=[(PX[j,i],PY[j,i]),(PX[j,i+1],PY[j,i+1]),(PX[j+1,i+1],PY[j+1,i+1]),(PX[j+1,i],PY[j+1,i])]
        x0=max(int(min(q[0] for q in p)),0); x1=min(int(max(q[0] for q in p))+1,PW-1)
        y0=max(int(min(q[1] for q in p)),0); y1=min(int(max(q[1] for q in p))+1,PH-1)
        if x1<x0 or y1<y0: continue
        X,Y=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
        def e(a,bb): return (X-a[0])*(bb[1]-a[1])-(Y-a[1])*(bb[0]-a[0])
        e0=e(p[0],p[1]); e1=e(p[1],p[2]); e2=e(p[2],p[3]); e3=e(p[3],p[0])
        m=((e0>=0)&(e1>=0)&(e2>=0)&(e3>=0))|((e0<=0)&(e1<=0)&(e2<=0)&(e3<=0))
        if not m.any(): continue
        zq=-hv[j,i]
        sub=zb[y0:y1+1,x0:x1+1]; upd=m&(zq<sub)
        if not upd.any(): continue
        sub[upd]=zq
        # tiled texture lookup on cell coords
        u=((X/S)/TILE); v=((Y/S)/TILE)
        cu=np.clip((np.mod(u,1.0)*tw).astype(np.int32),0,tw-1)
        cv=np.clip((np.mod(v,1.0)*th).astype(np.int32),0,th-1)
        n=np.array([-gx[j,i]*4,1.0,gy[j,i]*4]); n=n/np.linalg.norm(n)
        sh=0.35+0.65*abs(float(np.dot(n,L)))
        img[y0:y1+1,x0:x1+1][upd]=tex[cv,cu][upd]*sh
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
dr=ImageDraw.Draw(im)
dr.text((12,10),'MAP001 terrain: heightmap (ZC plane 1, K=0.10) + MAP001.TEX tiled every %d cells'%TILE,fill=(255,255,120))
im.save('K:/DeepseekSABoW/pfa/renders/TERRAIN_TEXTURED_001.png')
print('wrote TERRAIN_TEXTURED_001.png  (%s)' % (im.size,))
# also a top-down textured view (what a map editor would show)
S2=2
h2=hm[::S2,::S2]
def tileview(hh_,tile):
    o=468//S2
    u=np.mod(np.arange(o)/tile,1.0); v=np.mod(np.arange(o)/tile,1.0)
    cu=np.clip((u*tw).astype(int),0,tw-1); cv=np.clip((v*th).astype(int),0,th-1)
    return tex[np.ix_(cv,cu)]
top=tileview(h2,8)
gy2,gx2=np.gradient(h2)
sh=0.5+0.5*np.clip(1.0-np.hypot(gx2,gy2)*2.0,0,1)
out=(top*sh[:,:,None])
Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).save('K:/DeepseekSABoW/pfa/renders/TERRAIN_TOPDOWN_001.png')
print('wrote TERRAIN_TOPDOWN_001.png (textured top-down, tiled every 8 cells)')

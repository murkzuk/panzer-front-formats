import sys, struct
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
def planes(nm):
    d=load(D+nm)
    b=np.frombuffer(d[24:],dtype=np.uint8)
    return [b[i*W*H:(i+1)*W*H].reshape(H,W) for i in range(3)]
print('=== plane-1 (heightmap) stats across maps ===')
for nm in ('001.ZC','002.ZC','003.ZC','006.ZC','013.ZC'):
    p=planes(nm)[1]
    print('   %-8s min %3d max %3d mean %6.1f  relief %3d levels' % (nm,p.min(),p.max(),p.mean(),int(p.max())-int(p.min())))
print()
p0,p1,p2 = planes('001.ZC')
hm = p1.astype(np.float64)
print('=== heightmap 001: is it smooth in BOTH axes? ===')
print('   adj-diff  x %.3f   y %.3f' % (np.abs(np.diff(hm,axis=1)).mean(), np.abs(np.diff(hm,axis=0)).mean()))
print('   => a real heightfield')
print()
# hillshade
gy,gx=np.gradient(hm)
az=np.deg2rad(315); alt=np.deg2rad(45)
slope=np.arctan(np.hypot(gx,gy)*4.0)
aspect=np.arctan2(-gx,gy)
shade=(np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect))
shade=np.clip(shade,0,1)
Image.fromarray((shade*255).astype(np.uint8)).save('K:/DeepseekSABoW/pfa/renders/TERRAIN_hillshade_001.png')
print('wrote TERRAIN_hillshade_001.png')
# 3D isometric render with z-buffer
S=2   # downsample factor
h=hm[::S,::S]
hh,ww=h.shape
xs=np.arange(ww); zs=np.arange(hh)
XX,ZZ=np.meshgrid(xs,zs)
ang=np.deg2rad(35.0)
sx=(XX-ZZ)*np.cos(ang)
sy=(XX+ZZ)*np.sin(ang)*0.5 - h*2.2
sx=sx-sx.min(); sy=sy-sy.min()
PW,PH=1100,700
sc=min((PW-40)/max(sx.max(),1),(PH-40)/max(sy.max(),1))
img=np.full((PH,PW,3),0.55); zb=np.full((PH,PW),1e30)
L=np.array([-0.5,0.6,-0.62]); L=L/np.linalg.norm(L)
for j in range(hh-1):
    for i in range(ww-1):
        quad=((j,i),(j,i+1),(j+1,i+1),(j+1,i))
        pts=[]
        for (a,b) in quad:
            px=sx[a,b]*sc+20; py=sy[a,b]*sc+20
            pts.append((px,py, -((a+b)*0.5) - h[a,b]*0.01))
        nx=(h[j,i+1]-h[j,i]); nz=(h[j+1,i]-h[j,i])
        n=np.array([-nx*3,1.0,-nz*3]); n=n/np.linalg.norm(n)
        sh=0.25+0.75*abs(float(np.dot(n,L)))
        col=(sh*(0.55+0.6*(h[j,i]/205.0)), sh*(0.62+0.5*(h[j,i]/205.0)), sh*0.45)
        xs_=[p[0] for p in pts]; ys_=[p[1] for p in pts]
        x0=max(int(min(xs_)),0); x1=min(int(max(xs_))+1,PW-1)
        y0=max(int(min(ys_)),0); y1=min(int(max(ys_))+1,PH-1)
        if x1<x0 or y1<y0: continue
        X,Y=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
        def edge(a,b):
            return (X-a[0])*(b[1]-a[1])-(Y-a[1])*(b[0]-a[0])
        e0=edge(pts[0],pts[1]); e1=edge(pts[1],pts[2]); e2=edge(pts[2],pts[3]); e3=edge(pts[3],pts[0])
        m=((e0>=0)&(e1>=0)&(e2>=0)&(e3>=0))|((e0<=0)&(e1<=0)&(e2<=0)&(e3<=0))
        if not m.any(): continue
        zq=np.mean([p[2] for p in pts])
        sub=zb[y0:y1+1,x0:x1+1]; upd=m&(zq<sub)
        if upd.any():
            sub[upd]=zq
            img[y0:y1+1,x0:x1+1][upd]=col
im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
dr=ImageDraw.Draw(im); dr.text((12,10),'MAP001 terrain from ZC plane 1  (heightmap, %dx%d, downsample x%d)'%(W,H,S),fill=(255,255,120))
im.save('K:/DeepseekSABoW/pfa/renders/TERRAIN_3D_001.png')
print('wrote TERRAIN_3D_001.png')
print()
print('=== scale cross-check against the vehicle models ===')
print('   ZC header says 468x468 cells. Tank model 110003 is 5.58 long in MODEL units.')
print('   If a Pz III is ~5.9 m, 1 model unit ~= 1.06 m, so 468 cells x 10 (header) = 4680 units ~= 4950 m map.')
print('   heightmap relief 001 = %d levels => %d levels x 10 units = %d model units = %.0f m of relief.'
      % (int(p1.max())-int(p1.min()), int(p1.max())-int(p1.min()), (int(p1.max())-int(p1.min()))*10, (int(p1.max())-int(p1.min()))*10*1.06))

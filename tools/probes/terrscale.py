import sys, struct
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
d=load(D+'001.ZC'); b=np.frombuffer(d[24:],dtype=np.uint8)
hm=b[W*H:2*W*H].reshape(H,W).astype(np.float64)
S=3
h0=hm[::S,::S]
hh,ww=h0.shape
xs=np.arange(ww); zs=np.arange(hh)
XX,ZZ=np.meshgrid(xs,zs)
ang=np.deg2rad(38.0)
sx=(XX-ZZ)*np.cos(ang)
base=(XX+ZZ)*np.sin(ang)*0.5
PW,PH=640,470
L=np.array([-0.5,0.62,-0.60]); L=L/np.linalg.norm(L)
def panel(h,K):
    hh2=(h-h.min())*K
    sy=base-hh2
    minx,maxx=sx.min(),sx.max(); miny,maxy=sy.min(),sy.max()
    sc=min((PW-20)/(maxx-minx),(PH-20)/(maxy-miny))
    img=np.full((PH,PW,3),0.62); zb=np.full((PH,PW),1e30)
    ox=10-minx*sc; oy=10-miny*sc
    PX=sx*sc+ox; PY=sy*sc+oy
    gy,gx=np.gradient(h0)
    for j in range(hh-1):
        for i in range(ww-1):
            p=[(PX[j,i],PY[j,i]),(PX[j,i+1],PY[j,i+1]),(PX[j+1,i+1],PY[j+1,i+1]),(PX[j+1,i],PY[j+1,i])]
            nx=gx[j,i]; nz=gy[j,i]
            n=np.array([-nx*3,1.0,nz*3]); n=n/np.linalg.norm(n)
            sh=0.30+0.70*abs(float(np.dot(n,L)))
            t=(h0[j,i]-h0.min())/max(1.0,(h0.max()-h0.min()))
            col=(sh*(0.45+0.75*t), sh*(0.55+0.55*t), sh*(0.35+0.25*t))
            x0=max(int(min(q[0] for q in p)),0); x1=min(int(max(q[0] for q in p))+1,PW-1)
            y0=max(int(min(q[1] for q in p)),0); y1=min(int(max(q[1] for q in p))+1,PH-1)
            if x1<x0 or y1<y0: continue
            X,Y=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
            def e(a,bb): return (X-a[0])*(bb[1]-a[1])-(Y-a[1])*(bb[0]-a[0])
            e0=e(p[0],p[1]); e1=e(p[1],p[2]); e2=e(p[2],p[3]); e3=e(p[3],p[0])
            m=((e0>=0)&(e1>=0)&(e2>=0)&(e3>=0))|((e0<=0)&(e1<=0)&(e2<=0)&(e3<=0))
            if not m.any(): continue
            zq=-hh2[j,i]
            sub=zb[y0:y1+1,x0:x1+1]; upd=m&(zq<sub)
            if upd.any():
                sub[upd]=zq; img[y0:y1+1,x0:x1+1][upd]=col
    return img
Ks=[0.03,0.08,0.20,2.2]
labels=['K=0.03 (relief %d cells)'%(int(170*0.03)),'K=0.08 (relief %d cells)'%(int(170*0.08)),
        'K=0.20 (relief %d cells)'%(int(170*0.20)),'K=2.2  <- what I shipped (ravines)']
sheet=Image.new('RGB',(PW*2+30, (PH+26)*2+10),(22,22,26)); dr=ImageDraw.Draw(sheet)
for i,(K,lab) in enumerate(zip(Ks,labels)):
    im=panel(h0,K)
    r=i//2; c=i%2
    x=10+c*(PW+10); y=10+r*(PH+26)
    dr.text((x,y),lab,fill=(250,250,130))
    sheet.paste(Image.fromarray((np.clip(im,0,1)*255).astype(np.uint8)),(x,y+18))
sheet.save('K:/DeepseekSABoW/pfa/renders/TERRAIN_SCALE_SWEEP.png')
print('wrote TERRAIN_SCALE_SWEEP.png')
print()
print('map 001: heightmap range %d..%d (%d levels); map is %d cells across' % (hm.min(),hm.max(),int(hm.max()-hm.min()),W))
for K in Ks:
    imp=int(170*K/3)  # downsample S=3
    print('   K=%-5s -> relief %3d cells over %d  => avg slope %.2f%%' % (K,int(170*K),W,100*170*K/W))
print()
print('for reference, Panzer Front maps are driven over by tanks; a 4-5 km map with')
print('rolling terrain is ~2-5% average slope, which corresponds to K ~ 0.05-0.15')

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
h0=hm[::S,::S]; hh,ww=h0.shape
XX,ZZ=np.meshgrid(np.arange(ww),np.arange(hh))
ang=np.deg2rad(38.0)
sx=(XX-ZZ)*np.cos(ang); base=(XX+ZZ)*np.sin(ang)*0.5
PW,PH=620,455
L=np.array([-0.5,0.62,-0.60]); L=L/np.linalg.norm(L)
gy,gx=np.gradient(h0)
def panel(h,K):
    hv=(h-h.min())*K
    sy=base-hv
    sc=min((PW-20)/(sx.max()-sx.min()),(PH-20)/(sy.max()-sy.min()))
    img=np.full((PH,PW,3),0.62); zb=np.full((PH,PW),1e30)
    PX=sx*sc+(10-sx.min()*sc); PY=sy*sc+(10-sy.min()*sc)
    for j in range(hh-1):
        for i in range(ww-1):
            p=[(PX[j,i],PY[j,i]),(PX[j,i+1],PY[j,i+1]),(PX[j+1,i+1],PY[j+1,i+1]),(PX[j+1,i],PY[j+1,i])]
            n=np.array([-gx[j,i]*3,1.0,gy[j,i]*3]); n=n/np.linalg.norm(n)
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
            zq=-hv[j,i]
            sub=zb[y0:y1+1,x0:x1+1]; upd=m&(zq<sub)
            if upd.any():
                sub[upd]=zq; img[y0:y1+1,x0:x1+1][upd]=col
    return img
cfg=[(0.08,'K=0.08  (yours)    relief 13/468  2.9%'),
     (0.10,'K=0.10  DERIVED     relief 17/468  3.6%'),
     (0.13,'K=0.13  upper band  relief 22/468  4.7%')]
sheet=Image.new('RGB',(PW*3+40,PH+26),(22,22,26)); dr=ImageDraw.Draw(sheet)
for i,(K,lab) in enumerate(cfg):
    im=panel(h0,K); x=10+i*(PW+10)
    dr.text((x,8),lab,fill=(250,250,130))
    sheet.paste(Image.fromarray((np.clip(im,0,1)*255).astype(np.uint8)),(x,24))
sheet.save('K:/DeepseekSABoW/pfa/renders/TERRAIN_SCALE_DERIVED.png')
print('wrote TERRAIN_SCALE_DERIVED.png  (0.08 | 0.10 derived | 0.13)')
print()
print('derivation recap:')
print('  5.58 model units = ~5.9 m  -> 1 unit ~= 1.06 m')
print('  cell = 10 units (header)   -> 10.6 m ; map = 468 x 10.6 = 4960 m')
print('  1 height level = 1 unit    -> relief 170 units = 180 m -> 3.6% slope')
print('  in cell units: K = 1/10 = 0.10')

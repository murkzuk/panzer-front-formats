import sys, struct
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,'K:/DeepseekSABoW/pfa')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
def secs(d):
    h=struct.unpack_from('<5I',d,0)
    return h[1],h[2],h[3],h[4],len(d)
def idx4(buf,H,W,swap=False):
    raw=np.frombuffer(buf,dtype=np.uint8).reshape(H,W//2)
    a=np.empty((H,W),dtype=np.uint8)
    if swap:
        a[:,0::2]=(raw>>4)&0x0F; a[:,1::2]=raw&0x0F
    else:
        a[:,0::2]=raw&0x0F; a[:,1::2]=(raw>>4)&0x0F
    return a
tiles=[]
for nm in ('MAP001','MAP003','MAP006','MAP015'):
    d=load(D+nm+'.TEX')
    a,b,c,e,sz=secs(d)
    pal=np.frombuffer(d[32:96],dtype=np.uint8).reshape(16,4)
    img=pal[idx4(d[a:b],128,128)]
    tiles.append((nm,Image.fromarray(img,'RGBA').resize((384,384),Image.NEAREST)))
    # also the 64x64 mip
    img2=pal[idx4(d[b:c],64,64)]
    tiles.append((nm+'_mip64',Image.fromarray(img2,'RGBA').resize((384,384),Image.NEAREST)))
sheet=Image.new('RGB',(384*4+30, 384*2+50),(20,20,24)); dr=ImageDraw.Draw(sheet)
for i,(nm,im) in enumerate(tiles):
    r=i//4; cc=i%4
    x=10+cc*384; y=10+r*(384+22)
    dr.text((x,y),nm,fill=(245,245,140))
    sheet.paste(im.convert('RGB'),(x,y+18))
sheet.save('K:/DeepseekSABoW/pfa/renders/MAPS_4bpp.png')
print('wrote MAPS_4bpp.png  (top row = 128x128 level, bottom = 64x64 mip)')
print()
print('=== section D analysis (the remaining block) ===')
for nm in ('MAP001','MAP003'):
    d=load(D+nm+'.TEX'); a,b,c,e,sz=secs(d)
    Dd=d[e:]
    print('%s : section D = %d bytes' % (nm,len(Dd)))
    print('   first 48 bytes: %s' % ' '.join('%02X'%x for x in Dd[:48]))
    lo=(Dd&0x0F); hi=(Dd>>4)&0x0F
    print('   nibble hist: low %s' % dict(sorted(Counter(lo.tolist()).items())))
    print('                high %s' % dict(sorted(Counter(hi.tolist()).items())))
    u=np.frombuffer(Dd[:64],dtype='<u4'); f=np.frombuffer(Dd[:64],dtype='<f4')
    print('   u32: %s' % [int(x) for x in u[:10]])
    print('   f32: %s' % [round(float(x),3) for x in f[:10]])
    # any structure? look for a repeated stride
    for stride in (4,8,16,32,64,128,256,512,1024):
        if len(Dd)%stride==0:
            M=np.frombuffer(Dd[:len(Dd)//stride*stride],dtype=np.uint8).reshape(-1,stride)
            v=float(M.astype(np.float64).var(axis=0).mean())
            print('      stride %4d : %6d rows  mean col variance %.1f' % (stride,len(M),v))
    print()

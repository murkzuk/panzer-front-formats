import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
for nm in ('MAP001','MAP013'):
    d=load(D+nm+'.TEX')
    h=struct.unpack_from('<5I',d,0)
    e=h[4]; sz=len(d)
    arr=np.frombuffer(d[e:],dtype=np.uint8)
    print('%s : section D = %d bytes ; %d even' % (nm,len(arr),len(arr)%2))
    print('   first 32 bytes: %s' % ' '.join('%02X'%x for x in arr[:32]))
    lo=arr&0x0F; hi=(arr>>4)&0x0F
    print('   low  nibble hist: %s' % dict(sorted(Counter(lo.tolist()).items())))
    print('   high nibble hist: %s' % dict(sorted(Counter(hi.tolist()).items())))
    print('   byte  hist (top10): %s' % Counter(arr.tolist()).most_common(10))
    u=np.frombuffer(d[e:e+64],dtype='<u4'); f=np.frombuffer(d[e:e+64],dtype='<f4')
    print('   u32: %s' % [int(x) for x in u[:8]])
    print('   f32: %s' % [round(float(x),3) for x in f[:8]])
    for stride in (16,32,64,128,256,512,1024,2048):
        if len(arr)%stride==0:
            M=arr[:len(arr)//stride*stride].reshape(-1,stride)
            print('      stride %5d : %6d rows  mean col variance %7.1f' % (stride,len(M),float(M.astype(np.float64).var(axis=0).mean())))
    # is the section homogeneous, or does it change character partway?
    print('   character by 1/8ths (mean abs diff between adjacent bytes):')
    step=len(arr)//8
    for i in range(8):
        seg=arr[i*step:(i+1)*step].astype(np.int16)
        print('      [%d] mean %6.1f  std %6.1f  adj-diff %5.2f' % (i,seg.mean(),seg.std(),np.abs(np.diff(seg)).mean()))
    print()

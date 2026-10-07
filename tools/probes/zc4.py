import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
d=load(D+'001.ZC')
body=np.frombuffer(d[24:],dtype=np.uint8)
print('body %d bytes' % len(body))
print()
print('=== byte periodicity over the whole body ===')
for p in (1,2,3,4,5,6,8,12,16,24,48,468,936,1404,1872,2808):
    if p<len(body):
        print('   period %5d : %6.2f%% match' % (p,100*float(np.mean(body[:-p]==body[p:]))))
print()
print('=== where does the initial regularity stop? ===')
same4 = (body[:-4]==body[4:]).astype(np.int8)
# find the first run break
run=0
for i in range(len(same4)):
    if same4[i]: run+=1
    else:
        if i>0: print('   first mismatch at byte %d (after %d matching)' % (i+4,i+4)); break
print('   first 0.1%% of body is period-4: %.1f%%' % (100*float(np.mean(same4[:len(same4)//1000]))))
for frac in (0.001,0.01,0.1,0.25,0.5,0.75,0.99):
    i=int(len(same4)*frac)
    print('   at %5.1f%% in : period-4 match %.1f%%' % (100*frac,100*float(np.mean(same4[max(0,i-5000):i+5000]))))
print()
print('=== value distribution over the whole body ===')
c=np.bincount(body,minlength=256)
print('   distinct values: %d' % int((c>0).sum()))
print('   top 16: %s' % [(int(v),int(n)) for v,n in sorted(enumerate(c),key=lambda x:-x[1])[:16]])
print('   values > 63 : %.2f%%' % (100*float(np.mean(body>63))))
print('   values > 127: %.2f%%' % (100*float(np.mean(body>127))))
print()
print('=== does the body look like a 468x468 grid of u16 + tag? try other splits ===')
n=len(body)
for cellsz in (1,2,3,4,6,8):
    c2=n//cellsz
    r=int(c2**0.5)
    flag=' <== PERFECT SQUARE' if r*r==c2 else ''
    print('   %d bytes/cell -> %d cells, sqrt %.2f%s' % (cellsz,c2,c2**0.5,flag))
print()
print('=== first 64 bytes of body, and the same at several later offsets ===')
for off in (0, 64, 1024, 10000, 100000, 300000, 600000):
    seg=body[off:off+32]
    print('   +%-7d %s' % (off,' '.join('%02X'%x for x in seg)))

import sys, struct
from collections import Counter
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
d=load(D+'001.ZC')
body=d[24:]
W=H=468
cell=np.frombuffer(body,dtype=np.uint8).reshape(H,W,3)
print('planes identical?')
print('   b0==b1 : %.2f%%' % (100*np.mean(cell[:,:,0]==cell[:,:,1])))
print('   b1==b2 : %.2f%%' % (100*np.mean(cell[:,:,1]==cell[:,:,2])))
print('   all eq : %.2f%%' % (100*np.mean((cell[:,:,0]==cell[:,:,1])&(cell[:,:,1]==cell[:,:,2]))))
print()
print('first 4x4 cells (b0 b1 b2):')
for i in range(4):
    print('   ' + '  '.join('%3d,%3d,%3d'%tuple(cell[i,j]) for j in range(4)))
print()
print('=== byte periodicity in the first 512 bytes of the body ===')
b0=body[:512].astype(np.int32)
for p in range(1,9):
    same=np.mean(b0[:-p]==b0[p:])
    print('   period %d : %.1f%% of bytes match' % (p,100*same))
print()
print('=== whole-body periodicity ===')
a=body.astype(np.int32)
for p in (1,2,3,4,6,8,12,16,468,936,1404,1872):
    if p<len(a):
        print('   period %6d : %6.2f%% match' % (p,100*np.mean(a[:-p]==a[p:])))
print()
print('=== how many distinct 3-byte cells? ===')
flat=body.reshape(-1,3)
u,cnt=np.unique(flat,axis=0,return_counts=True)
print('   distinct triples: %d of %d' % (len(u),len(flat)))
print('   most common: %s' % [(tuple(int(x) for x in u[i]),int(cnt[i])) for i in np.argsort(-cnt)[:8]])
print()
print('=== header fields again, with 468 in mind ===')
print('   file %d ; body %d ; 468*468 = %d' % (len(d),len(body),468*468))
print('   body/468^2 = %.4f' % (len(body)/(468*468)))
print('   other factorisations of body:')
n=len(body)
for f in (1,2,3,4,6,8,12,16,24,48):
    if n%f==0:
        c=n//f
        r=int(c**0.5)
        if r*r==c: print('      %d bytes/cell -> %dx%d grid' % (f,r,r))

import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92)
D=B+'D'+B+'MA'+B+'GRD'+B
body=np.frombuffer(load(D+'001.ZC')[24:],dtype=np.uint8)
n=len(body)
W=8192
print('body %d bytes ; scanning in %d-byte windows' % (n,W))
print('%-9s %7s %7s %8s %9s %9s  %s' % ('offset','mean','std','adjdiff','%>63','%>127','character'))
prev=None
for o in range(0,n,W):
    seg=body[o:o+W].astype(np.float64)
    ad=float(np.abs(np.diff(seg)).mean())
    m=float(seg.mean()); s=float(seg.std())
    p63=100*float(np.mean(seg>63)); p127=100*float(np.mean(seg>127))
    ch='SMOOTH/terrain' if ad<20 else ('patterned' if ad<45 else 'high-entropy')
    if prev!=ch:
        print('%-9d %7.1f %7.1f %8.2f %8.1f%% %8.1f%%  %s   <== boundary' % (o,m,s,ad,p63,p127,ch))
        prev=ch
    else:
        print('%-9d %7.1f %7.1f %8.2f %8.1f%% %8.1f%%  %s' % (o,m,s,ad,p63,p127,ch))

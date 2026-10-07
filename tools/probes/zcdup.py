import sys
import numpy as np
sys.path.insert(0,'K:/DeepseekSABoW/pfa')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pzexport import open_iso
ent,load=open_iso(); B=chr(92); D=B+'D'+B+'MA'+B+'GRD'+B
W=H=468
def pl(nm):
    d=load(D+nm); b=np.frombuffer(d[24:],dtype=np.uint8)
    return [b[i*W*H:(i+1)*W*H].reshape(H,W) for i in range(3)]
z2=load(D+'002.ZC'); z3=load(D+'003.ZC')
print('002.ZC vs 003.ZC byte-identical? %s' % (z2==z3))
a=pl('002.ZC'); b=pl('003.ZC')
for i in range(3):
    print('   plane %d identical: %s' % (i,a[i].tobytes()==b[i].tobytes()))
print()
print('=== do any other ZC files duplicate? (md5 across all) ===')
import hashlib
from collections import Counter
ks=sorted(k for k in ent if k.startswith(D) and k.endswith('.ZC'))
h={}
for k in ks: h.setdefault(hashlib.md5(load(k)).hexdigest(),[]).append(k.split(B)[-1])
dup=[v for v in h.values() if len(v)>1]
print('   %d .ZC files, %d distinct contents' % (len(ks),len(h)))
for v in dup: print('      duplicate: %s' % v)

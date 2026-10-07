"""Panzer Front .PZ -> Wavefront OBJ.

Container:
    u32 size, u32 N, N x u32 parent, N x u32 id, N x 64 matrix, N x u32 offset, payloads
Payload vertex rows are 16 bytes, starting at  phase = 8 * (N % 2)  into the payload:
    (u,v,1,0) texcoord | (x,y,z,1) position | (nx,ny,nz,1) normal | (r,g,b,0) colour
Positions are listed per triangle; three consecutive position rows make one face.
"""
import struct, sys, os, math

def load(path):
    d = open(path,'rb').read()
    size, n = struct.unpack_from('<II', d, 0)
    par = struct.unpack_from('<%dI' % n, d, 8)
    ids = struct.unpack_from('<%dI' % n, d, 8+4*n)
    mats = [struct.unpack_from('<16f', d, 8+8*n+i*64) for i in range(n)]
    tbl = 8 + 72*n
    offs = struct.unpack_from('<%dI' % n, d, tbl)
    base = tbl + 4*n
    phase = 8 * (n % 2)
    ends = list(offs[1:]) + [size - base]
    nodes = []
    for i,(o,e) in enumerate(zip(offs, ends)):
        at = base + o + phase
        L = (e - o) - phase
        rows = max(0, L // 16)
        pos = []
        if rows:
            f = struct.unpack_from('<%df' % (rows*4), d, at)
            for r in range(rows):
                a,b,c,w = f[r*4:r*4+4]
                if w == 1.0 and abs(math.sqrt(a*a+b*b+c*c) - 1.0) > 0.01 and all(abs(x) < 1000 for x in (a,b,c)):
                    pos.append((a,b,c))
        nodes.append(dict(i=i, id=ids[i], par=par[i], mat=mats[i], pos=pos))
    return n, nodes

def world(nodes, i):
    """compose local matrices up the parent chain"""
    M = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    chain = []
    k = i
    while k != 0xFFFFFFFF and len(chain) < 64:
        chain.append(k); k = nodes[k]['par']
    for k in reversed(chain):
        m = nodes[k]['mat']
        M = [sum(M[r*4+t]*m[t*4+c] for t in range(4)) for r in range(4) for c in range(4)]
    return M

def xf(M, p):
    x,y,z = p
    return (M[0]*x+M[4]*y+M[8]*z+M[12],
            M[1]*x+M[5]*y+M[9]*z+M[13],
            M[2]*x+M[6]*y+M[10]*z+M[14])

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    n, nodes = load(src)
    V = []; F = []
    for nd in nodes:
        if len(nd['pos']) < 3: continue
        M = world(nodes, nd['i'])
        b = len(V)
        for p in nd['pos']: V.append(xf(M, p))
        for t in range(len(nd['pos']) // 3):
            F.append((b+t*3+1, b+t*3+2, b+t*3+3))
    with open(dst, 'w') as fh:
        fh.write('# %s  %d nodes\n' % (os.path.basename(src), n))
        for v in V: fh.write('v %.6f %.6f %.6f\n' % v)
        for f in F: fh.write('f %d %d %d\n' % f)
    print('%-34s %3d nodes  %6d verts  %6d tris -> %s' % (os.path.basename(src), n, len(V), len(F), dst))

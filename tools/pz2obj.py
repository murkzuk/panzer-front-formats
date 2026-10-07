"""Panzer Front Ausf.B .PZ -> Wavefront OBJ.

Container (verified on all 129 files):
    u32 size, u32 N, N x u32 parent, N x u32 id, N x 64 matrix, N x u32 offset, payloads

Vertex rows are 16 bytes and start  phase = 8 * (N % 2)  into the payload region:
    (u,v,1,0) texcoord   (x,y,z,1) position   (nx,ny,nz,1) normal   (r,g,b,0) colour

Sub-meshes are delimited by three all-zero rows; after a delimiter comes positions,
then normals, then colours, then texcoords. A sub-mesh is four equal streams, so
V = (rows to the next delimiter) / 4.

Sub-meshes SPAN node payload boundaries — a delimiter sits at a payload start in only
60 of 11,401 cases — so the payload region is read as one continuous row stream and each
sub-mesh is attributed to the node whose offset range contains its first row.

Matrices use the row-vector convention: translation in the last row (m12..m14), the
fourth column is zero in all 129 files.

KNOWN LIMITATION: simple map objects assemble correctly; vehicles do not. See docs/pz.md.
"""
import struct, sys, os, math

def load(path):
    d = open(path, 'rb').read()
    size, n = struct.unpack_from('<II', d, 0)
    par  = struct.unpack_from('<%dI' % n, d, 8)
    ids  = struct.unpack_from('<%dI' % n, d, 8 + 4*n)
    mats = [struct.unpack_from('<16f', d, 8 + 8*n + i*64) for i in range(n)]
    tbl  = 8 + 72*n
    offs = struct.unpack_from('<%dI' % n, d, tbl)
    base = tbl + 4*n
    start = base + 8 * (n % 2)
    rows = (size - start) // 16
    f = struct.unpack_from('<%df' % (rows*4), d, start)

    def zero(r): return all(f[r*4+t] == 0.0 for t in range(4))
    def w1(r):   return f[r*4+3] == 1.0

    dl = []; r = 0
    while r < rows:
        if zero(r):
            j = r
            while j < rows and zero(j): j += 1
            if j - r == 3: dl.append((r, j))
            r = j
        else:
            r += 1

    subs = []
    for k, (z0, z1) in enumerate(dl):
        end = dl[k+1][0] if k + 1 < len(dl) else rows
        R = end - z1
        if R < 8 or not w1(z1): continue
        j = z1
        while j < rows and w1(j): j += 1
        V = min(R // 4, j - z1)
        if V < 3: continue
        byte = start + z1*16 - base
        node = max((i for i in range(n) if offs[i] <= byte), default=0)
        subs.append((node, [tuple(f[(z1+q)*4+t] for t in range(3)) for q in range(V)]))
    return dict(n=n, par=par, ids=ids, mats=mats, subs=subs)

def world(m, i):
    """Row-vector convention: v_world = v_local * M_child * M_parent * ... * M_root."""
    M = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    chain = []; k = i
    while k != 0xFFFFFFFF and len(chain) < 64:
        chain.append(k); k = m['par'][k]
    for k in chain:
        a = m['mats'][k]
        M = [sum(M[r*4+t]*a[t*4+c] for t in range(4)) for r in range(4) for c in range(4)]
    return M

def xf(M, p):
    x, y, z = p
    return (M[0]*x+M[4]*y+M[8]*z+M[12], M[1]*x+M[5]*y+M[9]*z+M[13], M[2]*x+M[6]*y+M[10]*z+M[14])

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    m = load(src)
    V = []; F = []
    for node, sub in m['subs']:
        M = world(m, node); b = len(V)
        for p in sub: V.append(xf(M, p))
        for t in range(len(sub) // 3):
            F.append((b+t*3+1, b+t*3+2, b+t*3+3))
    with open(dst, 'w') as fh:
        fh.write('# %s  %d nodes  %d sub-meshes\n' % (os.path.basename(src), m['n'], len(m['subs'])))
        for v in V: fh.write('v %.6f %.6f %.6f\n' % v)
        for f2 in F: fh.write('f %d %d %d\n' % f2)
    print('%-30s %3d nodes  %4d sub-meshes  %5d verts  %5d tris -> %s' % (
        os.path.basename(src), m['n'], len(m['subs']), len(V), len(F), dst))

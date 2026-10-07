"""Panzer Front Ausf.B .PZ -> Wavefront OBJ.

Container:
    u32 size, u32 N, N x u32 parent, N x u32 id, N x 64 matrix, N x u32 offset, payloads

Vertex rows are 16 bytes and begin  phase = 8 * (N % 2)  bytes into each payload:
    (u,v,1,0) texcoord   (x,y,z,1) position   (nx,ny,nz,1) normal   (r,g,b,0) colour

Positions and normals share the shape (x,y,z,1) and arrive as one contiguous run,
positions first. The split is found by changepoint rather than by testing each row for
unit length, because a position lying on the unit sphere would otherwise be mis-sorted.
"""
import struct, sys, os, math

def split_run(f, start, run):
    """Return the index within the run where normals begin."""
    unit = [1 if abs(math.sqrt(sum(f[(start+k)*4+t]**2 for t in range(3))) - 1.0) < 0.02 else 0
            for k in range(run)]
    total_unit = sum(unit)
    best_k, best_s = run, sum(1 for u in unit if not u)      # default: all positions
    pre_nonunit = 0; post_unit = total_unit
    for k in range(run + 1):
        s = pre_nonunit + post_unit
        if s > best_s: best_s, best_k = s, k
        if k < run:
            pre_nonunit += 0 if unit[k] else 1
            post_unit   -= unit[k]
    return best_k

def submeshes(f, rows):
    """Split a payload into sub-meshes and return each one's position list.

    Sub-meshes are delimited by three all-zero rows. After a delimiter comes the
    position run, then normals, then colours, then texcoords — P follows a delimiter
    in 99.5% of 11,401 cases, T precedes one in 99.0%.

    A sub-mesh is four equal streams, so the vertex count is STRUCTURAL:

        V = (rows between this delimiter and the next) / 4

    not inferred from vector lengths. Checked independently: the colour run length
    equals that V in 8,996 of 11,053 sub-meshes (81.4%). A changepoint on the
    position/normal run disagrees with it 34.6% of the time, and using the changepoint
    is what previously corrupted the triangles.
    """
    def zero(r): return all(f[r*4+t] == 0.0 for t in range(4))
    def w1(r):   return f[r*4+3] == 1.0
    dl = []
    r = 0
    while r < rows:
        if zero(r):
            j = r
            while j < rows and zero(j): j += 1
            if j - r == 3: dl.append((r, j))
            r = j
        else:
            r += 1
    out = []
    for k, (z0, z1) in enumerate(dl):
        end = dl[k+1][0] if k + 1 < len(dl) else rows
        R = end - z1
        if R < 8 or not w1(z1): continue
        V = R // 4
        # the position run must be at least V long for this to be coherent
        j = z1
        while j < rows and w1(j): j += 1
        if j - z1 < V: V = split_run(f, z1, j - z1)
        if V < 3: continue
        out.append([tuple(f[(z1+q)*4+t] for t in range(3)) for q in range(V)])
    return out

def load(path):
    d = open(path, 'rb').read()
    size, n = struct.unpack_from('<II', d, 0)
    par  = struct.unpack_from('<%dI' % n, d, 8)
    ids  = struct.unpack_from('<%dI' % n, d, 8 + 4*n)
    mats = [struct.unpack_from('<16f', d, 8 + 8*n + i*64) for i in range(n)]
    tbl  = 8 + 72*n
    offs = struct.unpack_from('<%dI' % n, d, tbl)
    base = tbl + 4*n
    phase = 8 * (n % 2)
    ends = list(offs[1:]) + [size - base]
    nodes = []
    for i, (o, e) in enumerate(zip(offs, ends)):
        at = base + o + phase
        rows = max(0, ((e - o) - phase) // 16)
        subs = []
        if rows:
            f = struct.unpack_from('<%df' % (rows*4), d, at)
            subs = submeshes(f, rows)
        nodes.append(dict(i=i, id=ids[i], par=par[i], mat=mats[i], subs=subs))
    return n, nodes

def world(nodes, i):
    M = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    chain = []; k = i
    while k != 0xFFFFFFFF and len(chain) < 64:
        chain.append(k); k = nodes[k]['par']
    for k in reversed(chain):
        m = nodes[k]['mat']
        M = [sum(M[r*4+t]*m[t*4+c] for t in range(4)) for r in range(4) for c in range(4)]
    return M

def xf(M, p):
    x, y, z = p
    return (M[0]*x+M[4]*y+M[8]*z+M[12], M[1]*x+M[5]*y+M[9]*z+M[13], M[2]*x+M[6]*y+M[10]*z+M[14])

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    n, nodes = load(src)
    V = []; F = []
    for nd in nodes:
        if not nd['subs']: continue
        M = world(nodes, nd['i'])
        for sub in nd['subs']:
            b = len(V)
            for p in sub: V.append(xf(M, p))
            for t in range(len(sub) // 3):
                F.append((b+t*3+1, b+t*3+2, b+t*3+3))
    with open(dst, 'w') as fh:
        fh.write('# %s  %d nodes\n' % (os.path.basename(src), n))
        for v in V: fh.write('v %.6f %.6f %.6f\n' % v)
        for f in F: fh.write('f %d %d %d\n' % f)
    print('%-32s %3d nodes  %6d verts  %6d tris -> %s' % (os.path.basename(src), n, len(V), len(F), dst))

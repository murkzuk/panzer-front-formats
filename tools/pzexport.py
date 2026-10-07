"""Export Panzer Front Ausf B .PZ models to Wavefront OBJ (+MTL +PNG textures)."""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, 'K:/DeepseekSABoW/pfa')
from pz import PZ

ISO = r"D:\Panzer Front Ausf B\s-pfab.iso"
SS = 2048
SGN = np.array([1.0, -1.0, -1.0])          # confirmed display orientation

def open_iso(path=ISO):
    f = open(path, 'rb'); f.seek(16 * SS); pvd = f.read(SS)
    root = pvd[156:156 + 34]
    rlba = struct.unpack('<I', root[2:6])[0]; rsz = struct.unpack('<I', root[10:14])[0]
    def listdir(lba, size):
        f.seek(lba * SS); data = f.read((size + SS - 1) // SS * SS); out = []; off = 0
        while off < len(data):
            ln = data[off]
            if ln == 0:
                off = (off // SS + 1) * SS
                if off >= len(data): break
                continue
            rec = data[off:off + ln]
            nm = rec[33:33 + rec[32]].decode('ascii', 'replace')
            if nm not in ('\x00', '\x01'):
                out.append((nm, struct.unpack('<I', rec[2:6])[0], struct.unpack('<I', rec[10:14])[0]))
            off += ln
        return out
    roots = {n.split(';')[0].upper(): (l, s) for n, l, s in listdir(rlba, rsz)}
    plba, psz = roots['D.PAK']
    f.seek(plba * SS); nf, _ = struct.unpack('<II', f.read(8)); tb = f.read(nf * 0x48)
    ent = {}
    for i in range(nf):
        rec = tb[i * 0x48:(i + 1) * 0x48]; o, s = struct.unpack_from('<II', rec, 0)
        ent[rec[8:].split(b'\x00')[0].decode('latin1').upper()] = (o, s)
    def load(name):
        o, s = ent[name]; f.seek(plba * SS + o); return f.read(s)
    return ent, load

def decode_pza(d):
    f0, w, h, f3 = struct.unpack_from('<4I', d, 0)
    bpp = 8 if f0 == 1 else 4
    ncol = 256 if bpp == 8 else 16
    pals = f3 if f3 else 1
    off = 16
    pal = np.frombuffer(d[off:off + ncol * 4], dtype=np.uint8).reshape(ncol, 4)
    off += pals * ncol * 4
    if bpp == 8:
        idx = np.frombuffer(d[off:off + w * h], dtype=np.uint8).reshape(h, w)
    else:
        raw = np.frombuffer(d[off:off + (w * h) // 2], dtype=np.uint8).reshape(h, w // 2)
        idx = np.empty((h, w), dtype=np.uint8)
        idx[:, 0::2] = raw & 0x0F
        idx[:, 1::2] = (raw >> 4) & 0x0F
    rgba = pal[idx].copy()
    # Stored alpha is 128 on essentially every non-zero entry (a 50% default), and
    # palette entry 0 is (0,0,0,0) -- a TRANSPARENCY KEY. Forcing 255 makes index-0
    # texels opaque black, which fills the commander's cupola and the drive-sprocket
    # gaps. Map per entry instead: 0 stays 0, everything else goes opaque.
    a = rgba[:, :, 3].astype(np.int32)
    rgba[:, :, 3] = np.where(a == 0, 0, np.minimum(255, a * 2)).astype(np.uint8)
    return rgba, w, h

def find_textures(ent, model_path):
    d, base = model_path.rsplit(chr(92), 1)
    stem = base.rsplit('.', 1)[0]
    hits = [k for k in ent if k.endswith('.PZA') and k.split(chr(92))[-1].startswith(stem)]
    hits = [k for k in hits if k.split(chr(92))[-1][len(stem):len(stem) + 2].isdigit()]
    return sorted(hits)

def export(name, ent, load, outdir):
    os.makedirs(outdir, exist_ok=True)
    pz = PZ(load(name))
    stem = name.split(chr(92))[-1].rsplit('.', 1)[0]

    texs = find_textures(ent, name)
    tex_png = []
    for t in texs:
        rgba, w, h = decode_pza(load(t))
        p = '%s_%s.png' % (stem, t.split(chr(92))[-1].rsplit('.', 1)[0][len(stem):])
        Image.fromarray(rgba, 'RGBA').save(os.path.join(outdir, p))
        tex_png.append(p)

    v, vt, vn, faces, groups = [], [], [], [], []
    mat_of = {}
    cache = {}
    for sm in pz.submeshes:
        i = sm['node']
        if i not in cache:
            M = pz.world_matrix(i)
            R = np.array([[M[0], M[1], M[2]], [M[4], M[5], M[6]], [M[8], M[9], M[10]]])
            try: NR = np.linalg.inv(R).T
            except Exception: NR = R
            cache[i] = (np.array(M), R, NR)
        M, R, NR = cache[i]
        P = (np.array(sm['P']) @ R.T + M[12:15]) * SGN
        N = (np.array(sm['N']) @ NR.T) * SGN
        L = np.linalg.norm(N, axis=1, keepdims=True); L[L == 0] = 1.0
        N = N / L
        T = np.array(sm['T'])
        base = len(v)
        v.extend(P.tolist()); vn.extend(N.tolist())
        vt.extend([[t[0], 1.0 - t[1]] for t in T])
        groups.append(i)
        mat = 'mat_%s_%d' % (stem, 0)
        for k in range(0, len(P) - 2, 3):
            faces.append((mat, base + k + 1, base + k + 2, base + k + 3))

    objp = os.path.join(outdir, stem + '.obj')
    mtlp = os.path.join(outdir, stem + '.mtl')
    with open(objp, 'w') as o:
        o.write('# Panzer Front Ausf.B  %s\n' % name)
        o.write('# %d sub-meshes, %d triangles, %d textures\n' % (len(pz.submeshes), len(faces), len(tex_png)))
        o.write('mtllib %s.mtl\n' % stem)
        for p in v:  o.write('v %.6f %.6f %.6f\n' % tuple(p))
        for t in vt: o.write('vt %.6f %.6f\n' % tuple(t))
        for n in vn: o.write('vn %.6f %.6f %.6f\n' % tuple(n))
        cur = None
        for mat, a, b, c in faces:
            if mat != cur:
                o.write('usemtl %s\n' % mat); cur = mat
            o.write('f %d/%d/%d %d/%d/%d %d/%d/%d\n' % (a, a, a, b, b, b, c, c, c))
    with open(mtlp, 'w') as m:
        m.write('# Panzer Front Ausf.B materials\n')
        m.write('newmtl mat_%s_0\n' % stem)
        m.write('Ka 1.000 1.000 1.000\nKd 1.000 1.000 1.000\nKs 0.000 0.000 0.000\nd 1.0\nillum 2\n')
        if tex_png:
            m.write('map_Kd %s\n' % tex_png[0])
    return objp, len(v), len(faces), tex_png

if __name__ == '__main__':
    ent, load = open_iso()
    B = chr(92)
    targets = ['110003', '610088', '110001', '160077', '330059']
    out = 'K:/DeepseekSABoW/pfa/export'
    for t in targets:
        nm = B.join(['', 'D', 'UN', 'PZ', t + '.PZ'])
        if nm not in ent:
            nm = B.join(['', 'D', 'UN', t + '.PZ'])
        if nm not in ent:
            print('%-10s not found' % t); continue
        p, nv, nf, tex = export(nm, ent, load, out)
        print('%-10s -> %-34s  verts=%5d  tris=%5d  textures=%s'
              % (t, os.path.basename(p), nv, nf, [x.split('/')[-1] for x in tex] or 'NONE'))
    nm = B.join(['', 'D', 'MA', 'OBJ', 'OBJ011.PZ'])
    p, nv, nf, tex = export(nm, ent, load, out)
    print('%-10s -> %-34s  verts=%5d  tris=%5d  textures=%s' % ('OBJ011', os.path.basename(p), nv, nf, [x.split('/')[-1] for x in tex] or 'NONE'))

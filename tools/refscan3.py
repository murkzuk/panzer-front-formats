import struct, re, sys
BS = bytes([0x5C])
ELF = chr(75)+":/DeepseekSABoW/pfa/SLES_529.84.ELF"
d = open(ELF,'rb').read()
P_OFF, P_VA, P_SZ = 0x80, 0x00100000, 0x0016B900
def f2v(fo): return P_VA + (fo - P_OFF)

# every \D... path-like string, keyed by TRUE vaddr
pat = re.escape(BS + b'D' + BS) + rb'[ -~]{2,60}'
strs = {}
for m in re.finditer(pat, d):
    strs[f2v(m.start())] = m.group(0).decode('latin1')
# also the cdrom0: one
for m in re.finditer(rb'cdrom0:[ -~]{2,40}', d):
    strs[f2v(m.start())] = m.group(0).decode('latin1')
print("path-like strings: %d" % len(strs))

# ---- pointers in data
ptr = {}
for fo in range(0, P_SZ-4, 4):
    w = struct.unpack_from('<I', d, fo)[0]
    if w in strs: ptr.setdefault(w, []).append(f2v(fo))
print("data words pointing at one: %d words -> %d targets" % (sum(len(v) for v in ptr.values()), len(ptr)))
for va, locs in sorted(ptr.items()):
    print("   %08X %-30s <- %s" % (va, strs[va][:30], " ".join("%08X"%l for l in locs)))

# ---- lui/addiu immediates
hits = []
st = {}
for fo in range(0, P_SZ-4, 4):
    w = struct.unpack_from('<I', d, fo)[0]
    op = w >> 26
    if op == 0x0F:
        st[(w>>16)&31] = (w & 0xFFFF, fo)
    elif op == 0x09:
        rs=(w>>21)&31
        imm = w & 0xFFFF
        if imm & 0x8000: imm -= 0x10000
        if rs in st:
            a = (st[rs][0] << 16) + imm
            if a in strs: hits.append((f2v(st[rs][1]), f2v(fo), a, strs[a][:30]))
print("\nlui/addiu building one: %d" % len(hits))
for h in hits: print("   lui@%08X addiu@%08X -> %08X %s" % h)

# ---- stride structure
al = sorted(strs)
on20 = [v for v in al if v % 0x20 == 0]
print("\non a 0x20 boundary: %d of %d" % (len(on20), len(al)))
from collections import Counter
gaps = Counter(al[i+1]-al[i] for i in range(len(al)-1))
print("gap histogram (top):", gaps.most_common(8))

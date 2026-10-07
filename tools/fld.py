import struct, sys
d = open(chr(75)+":/DeepseekSABoW/pfa/SLES_529.84.ELF",'rb').read()
P_OFF,P_VA,P_SZ = 0x80,0x00100000,0x0016B900
def f2v(fo): return P_VA+(fo-P_OFF)
MEM={0x20:"lb",0x21:"lh",0x23:"lw",0x24:"lbu",0x25:"lhu",0x28:"sb",0x29:"sh",0x2b:"sw",0x37:"ld",0x3f:"sd"}
R=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
   "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
target = int(sys.argv[1],16)
for fo in range(0,P_SZ-4,4):
    w=struct.unpack_from('<I',d,fo)[0]
    op=w>>26
    if op in MEM:
        imm=w&0xFFFF
        if imm&0x8000: imm-=0x10000
        if imm==target:
            rs=(w>>21)&31; rt=(w>>16)&31
            if R[rs] in ("sp","gp"): continue
            print("%08X  %-4s %s,%d(%s)"%(f2v(fo),MEM[op],R[rt],imm,R[rs]))

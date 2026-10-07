import struct, re, sys
BS = bytes([0x5C])
d = open(chr(75)+":/DeepseekSABoW/pfa/SLES_529.84.ELF",'rb').read()
P_OFF, P_VA = 0x80, 0x00100000
def v2f(va): return va - P_VA + P_OFF
def f2v(fo): return P_VA + (fo - P_OFF)
R=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
   "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
def sx(i): return i-0x10000 if i&0x8000 else i
SPECIAL={0x20:"add",0x21:"addu",0x22:"sub",0x23:"subu",0x24:"and",0x25:"or",0x26:"xor",
 0x27:"nor",0x2a:"slt",0x2b:"sltu",0x00:"sll",0x02:"srl",0x03:"sra",0x04:"sllv",0x06:"srlv",
 0x07:"srav",0x08:"jr",0x09:"jalr",0x18:"mult",0x19:"multu",0x1a:"div",0x1b:"divu",
 0x10:"mfhi",0x12:"mflo",0x0c:"syscall",0x0d:"break",0x0b:"movn",0x0a:"movz"}
OPS={0x08:"addi",0x09:"addiu",0x0a:"slti",0x0b:"sltiu",0x0c:"andi",0x0d:"ori",0x0e:"xori",
 0x0f:"lui",0x20:"lb",0x21:"lh",0x23:"lw",0x24:"lbu",0x25:"lhu",0x28:"sb",0x29:"sh",
 0x2b:"sw",0x31:"lwc1",0x39:"swc1",0x37:"ld",0x3f:"sd",0x04:"beq",0x05:"bne",0x06:"blez",
 0x07:"bgtz",0x01:"regimm",0x02:"j",0x03:"jal",0x14:"beql",0x15:"bnel",0x11:"cop1"}
def dis1(w, va):
    op=w>>26
    rs=(w>>21)&31; rt=(w>>16)&31; rd=(w>>11)&31; sh=(w>>6)&31; fn=w&63
    imm=w&0xFFFF
    if w==0: return "nop"
    if op==0:
        m=SPECIAL.get(fn,"spec.%02x"%fn)
        if m in("sll","srl","sra"): return "%-6s %s,%s,%d"%(m,R[rd],R[rt],sh)
        if m in("jr",): return "%-6s %s"%(m,R[rs])
        if m in("jalr",): return "%-6s %s,%s"%(m,R[rd],R[rs])
        if m in("mult","multu","div","divu"): return "%-6s %s,%s"%(m,R[rs],R[rt])
        if m in("mfhi","mflo"): return "%-6s %s"%(m,R[rd])
        return "%-6s %s,%s,%s"%(m,R[rd],R[rs],R[rt])
    m=OPS.get(op,"op.%02x"%op)
    if m=="lui": return "%-6s %s,0x%04x"%(m,R[rt],imm)
    if m in("j","jal"): return "%-6s 0x%08X"%(m,(va&0xF0000000)|((w&0x3FFFFFF)<<2))
    if m in("beq","bne","beql","bnel"): return "%-6s %s,%s,0x%08X"%(m,R[rs],R[rt],va+4+sx(imm)*4)
    if m in("blez","bgtz"): return "%-6s %s,0x%08X"%(m,R[rs],va+4+sx(imm)*4)
    if m=="regimm":
        n={0:"bltz",1:"bgez",16:"bltzal",17:"bgezal"}.get(rt,"regimm.%d"%rt)
        return "%-6s %s,0x%08X"%(n,R[rs],va+4+sx(imm)*4)
    if m in("addi","addiu","slti","sltiu"): return "%-6s %s,%s,%d"%(m,R[rt],R[rs],sx(imm))
    if m in("andi","ori","xori"): return "%-6s %s,%s,0x%04x"%(m,R[rt],R[rs],imm)
    if m=="cop1": return "cop1   0x%07x"%(w&0x3FFFFFF)
    return "%-6s %s,%d(%s)"%(m,R[rt],sx(imm),R[rs])
def dump(lo,hi):
    for va in range(lo,hi,4):
        w=struct.unpack_from('<I',d,v2f(va))[0]
        print("%08X  %08X  %s"%(va,w,dis1(w,va)))
if __name__=="__main__":
    dump(int(sys.argv[1],16), int(sys.argv[2],16))

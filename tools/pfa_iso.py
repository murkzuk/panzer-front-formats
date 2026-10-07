import sys, struct, os

SS=2048
class ISO:
    def __init__(self, path):
        self.f = open(path,'rb')
        self.path = path
    def sector(self, lba, count=1):
        self.f.seek(lba*SS)
        return self.f.read(count*SS)
    def pvd(self):
        return self.sector(16)
    def root(self):
        pvd = self.pvd()
        assert pvd[1:6]==b'CD001', "not iso9660"
        root = pvd[156:156+34]
        return struct.unpack('<I', root[2:6])[0], struct.unpack('<I', root[10:14])[0]
    def listdir(self, lba, size):
        data = self.sector(lba, (size+SS-1)//SS)
        out=[]; off=0
        while off < len(data):
            ln = data[off]
            if ln == 0:
                off = (off//SS+1)*SS
                if off >= len(data): break
                continue
            rec = data[off:off+ln]
            e = dict(lba=struct.unpack('<I', rec[2:6])[0],
                     size=struct.unpack('<I', rec[10:14])[0],
                     flags=rec[25], name=rec[33:33+rec[32]].decode('ascii','replace'))
            if e['name'] not in ('\x00','\x01'): out.append(e)
            off += ln
        return out
    def read(self, lba, size):
        return self.sector(lba, (size+SS-1)//SS)[:size]

if __name__ == '__main__':
    iso = ISO(sys.argv[1])
    if len(sys.argv) > 2:
        name = sys.argv[2]
        outpath = sys.argv[3]
        lba, size = iso.root()
        for e in iso.listdir(lba, size):
            if e['name'].split(';')[0].upper() == name.upper():
                d = iso.read(e['lba'], e['size'])
                open(outpath,'wb').write(d)
                print("wrote", outpath, len(d))
                break
        else:
            print("not found")
    else:
        lba, size = iso.root()
        print(iso.path)
        for e in iso.listdir(lba, size):
            print(f"{'D' if e['flags']&2 else 'F'} {e['name']:24s} lba={e['lba']:8d} size={e['size']}")

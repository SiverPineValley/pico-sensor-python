import machine

class Utility():
    def convert(self, parts):
        if (parts[0] == 0):
            return None
            
        data = parts[0]+(parts[1]/60.0)
        if (parts[2] == 'S'):
            data = -data
        if (parts[2] == 'W'):
            data = -data

        data = '{0:.1f}'.format(data) # to 6 decimal places
        return str(data)

    def getUniqueDeivcieId(self) -> str:
        s = machine.unique_id()
        ul = []
        u = ""
        for b in s:
            ul.append(hex(b)[2:])
        u = ":".join(ul)
        return u

    def removeNonAsciiBytes(self, s):
        o = b""
        for b in s:
          if b < 0x7F:
            o += bytes(chr(b), "ascii")
        return o

    def removeAsciiBytes(self, s):
        o = b""
        for b in s:
          if b < 0x7F:
            continue
          else:
            o += bytes(chr(b), "ascii")
        return o

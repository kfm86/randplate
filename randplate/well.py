

# ident: [A-Z][0-9]{1,2}
class Well:
    def __init__(self, ident, row=None, col=None):
        self.row=row
        self.col=col
        self.ident=ident
        self.value = 0

        if not row or col:
            self.row=ident[:-2]
            self.col=ident[1:]
        if type(self.row) == type(str()):
            self.row=ord(self.row)
            self.col=int(self.col)

    def distance(self, w2):
        return (w2.row-self.row, w2.col-self.col)

    def print(self):
        print(f"{self.ident}: r={self.row}c={self.col}")

    def __str__(self):
        return f"{self.ident}[{self.value}]"


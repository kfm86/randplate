

# ident: [A-Z][0-9]{1,2}
class Well:
    """Class to represent a well in a plate"""
    def __init__(self, ident, row=None, col=None):
        """Initialise self. If row/col nums not already parsed, do so."""
        self.row=row
        self.col=col
        self.ident=ident
        self.assigned = False
        self.group = "_"

        if not row or not col:
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
        return f"{self.ident}[{self.group}]"
    


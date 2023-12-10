import pandas as pd
import logging as lg

import randplate as rp

class DrugList:
    def __init__(self, filename):
        self.drugs = pd.read_csv(filename, delimiter=";")

    def print(self, level=lg.DEBUG):
        msg = f"\n{rp.utils.print_sep()}\nAssigning drugs:\n{self.drugs}\n{rp.utils.print_sep()}"
        lg.log(level, msg)




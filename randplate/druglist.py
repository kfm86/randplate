import pandas as pd
import logging as lg

import randplate as rp

class DrugList:
    def __init__(self, filename):
        self.drugs = pd.read_csv(filename, delimiter=";")

    def print(self, level=lg.DEBUG):
        lg.log(level, rp.utils.print_sep())
        lg.log(level, "Assigning drugs:")
        lg.log(level, self.drugs)
        lg.log(level, rp.utils.print_sep())




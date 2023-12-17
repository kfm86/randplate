import pandas as pd
import logging as lg

import randplate as rp

def well_list(names):
    my_list = []
    for name in names:
        well = rp.Well(name)
        my_list.append(well)
        #well.print()

    return my_list

class Plate:
    wells = []

    def __init__(self, filename):
        # read the file, using the 1th column as the indexes.
        # Then pivot, so that the other column values are used as the row names.
        # This could probably be done better/in one step.
        lg.debug(f"Loading plate file: {filename}")
        self.filename = filename
        self.plate = pd.read_csv(filename, index_col=1, header=None)
        self.plate = self.plate.pivot(columns=self.plate.columns[1]).loc[:,0]
        row_names = self.plate.index.values
        col_names = self.plate.columns.values
        self.shape = self.plate.shape

        (self.rows, self.cols) = self.shape

        # replace the values in each position with a Well object
        # this could probably be done in a pandier way
        for row in row_names:
            self.plate.loc[row] = well_list(self.plate.loc[row])
            #print(plate.loc[row])


    def print(self, level=lg.DEBUG):
        msg = f"\n{rp.utils.print_sep()}\nPlate {self.filename}:\n{self.plate}\n[{self.rows} rows x {self.cols} columns]\n{rp.utils.print_sep()}"
        lg.log(level, msg)

    def fill(self, row, col):
        #lg.debug(f"Filling plate well at {row}x{col}")
        self.plate.iloc[row,col].value = 1
        #print(f"well {self.plate.iloc[row,col]}={self.plate.iloc[row,col].value}")
        #self.plate.loc[row,col].value = 1


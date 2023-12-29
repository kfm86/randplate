import logging as lg
import randplate as rp


class Coordinates:
    """Class to handle two lists of column and row indices and store them in a plate."""
    def __init__(self, plate: rp.Plate):
        self.plate = plate
        self.rows = self.plate.shape[0]
        self.cols = self.plate.shape[1]
        self.shape = (self.rows, self.cols)

    def store(self, row_indices: list, col_indices: list) -> rp.Plate:
        # if len(row_indices != self.rows):
        #     raise ValueError("len(row_indices) != self.rows")
        # if len(col_indices != self.cols):
        #     raise ValueError("len(col_indices) !+ self.cols")
        if len(row_indices) != len(col_indices):
            raise ValueError("row and col indices must be equal")
        for i in range(len(row_indices)):
            self.plate.fill(row_indices[i], col_indices[i])
        self.plate.print(lg.INFO)
        return self.plate
    
    def get_list(self):
        pass

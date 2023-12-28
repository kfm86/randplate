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
    "Class representing the plate described by the plate input file"
    wells = []

    def __init__(self, filename: str):
        """Reads given plate definition file and stores it as a pd.Dataframe"""
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


    def print(self, level: int = lg.DEBUG) -> None:
        """'Nicely' print plate layout, with target group names"""
        msg = f"\n{rp.utils.print_sep()}\nPlate {self.filename}:\n{self.plate}\n[{self.rows} rows x {self.cols} columns]\n{rp.utils.print_sep()}"
        lg.log(level, msg)

    def store(self, row_indices: list, col_indices: list, group: str) -> None:
        """Store the coordinates obtained from combining the two lists of row and col indices."""
        # if len(row_indices != self.rows):
        #     raise ValueError("len(row_indices) != self.rows")
        # if len(col_indices != self.cols):
        #     raise ValueError("len(col_indices) !+ self.cols")
        if len(row_indices) != len(col_indices):
            raise ValueError("row and col indices must be equal")
        for i in range(len(row_indices)):
            self.plate.iloc[row_indices[i], col_indices[i]].assigned = True
            self.plate.iloc[row_indices[i], col_indices[i]].group = group
        self.print(lg.INFO)
    

    # assigned_coords -> Plate
    # df -> dataframe of drugs to position
    #       for each drug, we need to generate a position on the assigned_coords Plate
    #       we assume this dataframe has already been randomised, and can therefore assign them
    #       row and column indices, up to the shape of assigned_coords
    # goal -> how many each (row,column) should have on average
    # The generated coordinates are stored in assigned_coords object. 
    # Returns a pd.Dataframe (modified from input df).
    def generate_coordinates(self, df: pd.DataFrame, goal: (float, float), group_name: str) -> pd.DataFrame:
        """Generate the position matrix for the items in a target group."""
        rows = self.plate.shape[0]
        cols = self.plate.shape[1]

        redo = [True] * len(df)
        print(len(redo))
        while any(redo):
            # 1. get a list of row numbers for each row in df
            row_indices = rp.utils.gen_single_axis_index_list(rows, goal[0], len(df))
            # for each item in list, check that there are enough free spaces in that row
            for i in range(len(df)):
                row = row_indices[i]
                num_assigned = 0
                for col in range(cols):
                    if self.is_assigned(row,col):
                        num_assigned += 1
                #print(f"{row}: {num_assigned}")
                if num_assigned >= cols:
                    redo[i]=True
                else:
                    redo[i]=False
            print("Redo:",redo)
                #all assigned, need to redo this index.

        # 2. get a list of column numbers and hence coordinates
        df.cols = rp.utils.gen_single_axis_index_list(cols, goal[1], len(df))
        #df.cols_done = [False] * len(df)

        # for each item, check the coordinate is free. If not try again...
        df.cols_done = [True] * len(df)

        

        lg.debug(f"row_indices[{len(row_indices)}]: {row_indices}")
        lg.debug(f"col_indices:[{len(df.cols)}] {df.cols}")

        self.store(row_indices, df.cols, group_name)

        return df

    def is_assigned(self, row: int or str, col: int = None) -> bool:
        """Helper function to show if given well position is assigned."""
        if col is None:
            return self.plate.loc[row].assigned
        else:
            return self.plate.iloc[row,col].assigned
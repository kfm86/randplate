import pandas as pd
import logging as lg
import random as rand

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


    def print(self, level: int = lg.DEBUG, transpose: bool = False) -> None:
        """'Nicely' print plate layout, with target group names"""
        df = self.plate
        if transpose:
            df = self.plate.T
        msg = f"\n{rp.utils.print_sep()}\nPlate {self.filename}:\n{df}\n[{self.rows} rows x {self.cols} columns]\n{rp.utils.print_sep()}"
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
        self.print(lg.INFO, True)
    

    # assigned_coords -> Plate
    # df -> dataframe of drugs to position
    #       for each drug, we need to generate a position on the assigned_coords Plate
    #       we assume this dataframe has already been randomised, and can therefore assign them
    #       row and column indices, up to the shape of assigned_coords
    # goal -> how many each (row,column) should have on average
    # The generated coordinates are stored in assigned_coords object. 
    # Returns a pd.Dataframe (modified from input df).
    def generate_coordinates(self, drug_group: pd.DataFrame, goal: (float, float), group_name: str) -> pd.DataFrame:
        """Generate the position matrix for the items in a target group."""
        # Generate two lists of integers: indices of row,col. Together they make coordinates.
        # The coordinates will be added to df as a new column: pos

        num_rows = self.plate.shape[0]
        num_cols = self.plate.shape[1]
        row_indices = []
        col_indices = []

        # 1. Generate list of row indices. These should not already be assigned.
        redo = [True] * len(drug_group)
        while any(redo):
            # 1.1 get a list of row numbers for each row in df
            row_indices = rp.utils.gen_single_axis_index_list(num_rows, goal[0], len(drug_group))
            # 1.2 for each item in list, check that there are enough free spaces in that row
            for i in range(len(drug_group)):
                row = row_indices[i]
                num_assigned = 0
                for col in range(num_cols):
                    if self.is_assigned(row,col):
                        num_assigned += 1
                #print(f"{row}: {num_assigned}")
                if num_assigned >= num_cols:
                    redo[i]=True
                else:
                    redo[i]=False
            print("Redo:",redo)
                #all assigned, need to redo this index.

        # 2. get a list of column numbers 
        col_indices = rp.utils.gen_single_axis_index_list(num_cols, goal[1], len(drug_group))
        redo = [True] * len(drug_group)
        while any(redo):
            rand.shuffle(col_indices)
            positions = rp.utils.combine_coord_lists(row_indices, col_indices)
            # 2.1. get a list of column numbers for each row in df.
            # 2.2. for each item in list, check that there are enough free spaces in that row
            for i in range(len(drug_group)):
                col = col_indices[i]
                num_assigned = 0
                for row in range(num_rows):
                    if self.is_assigned(row,col):
                        num_assigned += 1
                #print(f"{row}: {num_assigned}")
                #TODO: is this comparison correct?
                if num_assigned >= num_rows:
                    print(f"&&& redo[{i}]=True")
                    # redo[i]=True
                    continue
                redo[i] = False
                # 2.3. for each item in list, check it is not touching any of same primary_target
                # this is in the same list!
                # if positions[i] is touching any other placed item, it should be moved.
                # start with positions[i]
                # loop through the rest
                # calculate the distance
                # if touching, redo[i]=True
                for pos in positions:
                    #print(f"&&& pos={pos}({type(pos)}) posisions[{i}]={positions[i]}({type(positions[i])}) ")
                    if is_touching(positions[i], pos) and pos != positions[i]:
                        print(f"Positions touching: {pos}-{positions[i]} => redo[{i}]=True")
                        redo[i] = True
                        #print (redo)
            num_redo = len([i for i in redo if i == True])

            
            redo_wells = [col_indices[i] for i in range(len(redo)) if redo[i]]
            print(f"wells to redo: {num_redo}: {redo_wells}")
            # take the wells to redo
            # calc which ones need to be redone (if A1 and A2 are touching, only one of them must move)
            # split those coordinates into row/col, shuffle the cols, reform coords
            # check if any are touching

                
                


        print(f"&&& len(row_indices)={len(row_indices)} len(col_indices)={len(col_indices)}")

        # 3. Combine these to get a single list of coordinates. Add this as a new column to df.
        #    Store this list in self, so these positions are marked as assigned.
        positions = rp.utils.combine_coord_lists(row_indices, col_indices)
        lg.debug(f"positions[{len(positions)}]: {positions}")

        self.store(row_indices, col_indices, group_name)

        return drug_group

    def is_assigned(self, row: int or str, col: int = None) -> bool:
        """Helper function to show if given well position is assigned."""
        if col is None:
            return self.plate.loc[row].assigned
        else:
            return self.plate.iloc[row,col].assigned
        

    def get_rand_free_coord(self) -> str:
        free_wells = []
        for row in self.plate.shape[0]:
            for col in self.plate.shape[1]:
                if not self.plate.iloc[row,col].is_assigned():
                    free_wells.append(self.plate.iloc[row,col])
        if not free_wells:
            raise RuntimeError("No free wells remaining")
        rand.shuffle(free_wells)
        return free_wells[0].ident

        



    # def is_touching(self, group: str, row: int, col: int, dist: int = 1) -> bool:
    #     """Returns true if any positions are within {dist=1} wells of already assigned well with same primary target"""
    #     touching = False
    #     for r1 in range(row-dist,row+dist):
    #         for c1 in range(col-dist, col+dist):
    #             distance = self.plate.iloc[row,col].distance(r1, c1)
    #             #print(f"{r1},{c1}:{distance}/{self.plate.iloc[r1,c1].group}")
    #             if distance[0] > dist or distance[1] > dist:
    #                 if self.plate.iloc[r1,c1].group == group:
    #                     touching = True
    #     return touching
        
def is_touching(pos1: str, pos2: str, dist: int = 1) -> bool:
    """Returns True if the two given positions are within dist wells of each other. Diagonal distances are not considered."""
    #pos1=str(pos1)
    #print(f"pos1='{pos1} pos2={pos2} type(pos1)={type(pos1)} type(pos2)={type(pos2)}")
    #
    # 4   4 3 2 3
    # 3   3 2 1 2
    # 2   2 1 X 1
    # 1   3 2 1 2
    # 0   4 3 2 3
    #
    #     0 1 2 3
    # Total distance must be less than {dist}.
    # i.e.  pos1 = (2,2) 
    #       pos2 = (0,0) (1,1) (2,2) (3,3) (3,0)
    #  diff_coor = (2,2) (1,1) (0,0) (1,1) (1,2)
    # diff_total =    4     2     0     2     3
    #
    if pos1 == pos2:
        return True
    pos1 = rp.utils.split_str_coord(pos1)
    pos2 = rp.utils.split_str_coord(pos2)

    rows_dist = abs(pos1[0] - pos2[0])
    cols_dist = abs(pos1[1] - pos2[1])
    return rows_dist + cols_dist <= dist
        

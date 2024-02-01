import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import logging
import random
import time
import sys

import randplate as rp

lg = logging.getLogger('randplate')

TIMEOUT = 1

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
        try:
            self.plate = pd.read_csv(filename, index_col=1, header=None)
        except IndexError:
            lg.error(f"Failed to parse plate file '{filename}'. Please verify the format.")
            sys.exit(1)
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


    def print(self, level: int = logging.DEBUG, transpose: bool = False) -> None:
        """'Nicely' print plate layout, with target group names"""
        df = self.plate
        if transpose:
            df = self.plate.T
        msg = f"\n{rp.utils.print_sep()}\nPlate {self.filename}:\n{df}\n[{self.rows} rows x {self.cols} columns]\n{rp.utils.print_sep()}"
        lg.log(level, msg)

    def store(self, drug_group: pd.DataFrame, group: str) -> None:
        """Store the coordinates obtained from combining the two lists of row and col indices."""
        # if len(row_indices != self.rows):
        #     raise ValueError("len(row_indices) != self.rows")
        # if len(col_indices != self.cols):
        #     raise ValueError("len(col_indices) !+ self.cols")
        lg.debug(f"Storing drug group:{group}\nPositions:")
        for i in drug_group.index:
            row = rp.utils.row_as_str(drug_group.at[i,'row'])
            col = drug_group.at[i,'col']
            #print(drug_group)
            lg.debug(f"i:{i} row:{row} col:{col}")
            try:
                self.plate.at[row,col].assigned = True
                self.plate.at[row,col].group = group
            except KeyError as ex:
                print("!!! ERROR: KeyError CAUGHT !!!")
                print(f"row:{row} col:{col}")
                print(self.plate.shape)
                raise
            if row == 0 or col == 0:
                raise RuntimeError(f"ROW={row} COL={col}")
        self.print(logging.INFO, True)
    

    # assigned_coords -> Plate
    # df -> dataframe of drugs to position
    #       for each drug, we need to generate a position on the assigned_coords Plate
    #       we assume this dataframe has already been randomised, and can therefore assign them
    #       row and column indices, up to the shape of assigned_coords
    # goal -> how many each (row,column) should have on average
    # The generated coordinates are stored in assigned_coords object. 
    # Returns a pd.Dataframe (modified from input df).
    def generate_coordinates(self, drug_group: pd.DataFrame, goal: (float, float), group_name: str) -> pd.DataFrame:
        ROWS = "row"
        COLS = "col"
        REDO = "redo"
        POS = "position"
        """Generate the position matrix for the items in a target group."""
        # Generate two lists of integers: indices of row,col. Together they make coordinates.
        # The coordinates will be added to df as a new column: pos

        num_rows = self.plate.shape[0]
        num_cols = self.plate.shape[1]


        # 1. Copy drug_group dataframe and generate row indices
        df = drug_group
        df[REDO] = [True] * len(drug_group)
        while any(df[REDO]):
            # 1.1 get a list of row numbers for each row in df
            df[ROWS] = random.choices(list(range(num_rows)), k=len(drug_group))
            # 1.2 for each item in list, check that there are enough free spaces in that row
            for i in range(len(df)):
                row = df[ROWS].iloc[i]
                num_assigned_to_row = 0
                for col in range(num_cols):
                    if self.is_assigned(row,col):
                        num_assigned_to_row += 1
                #print(f"{row}: {num_assigned}")
                if num_assigned_to_row >= num_cols:
                    df[REDO].iloc[i] = True
                else:
                    df[REDO].iloc[i] = False
            lg.debug("Redo:",df[REDO])
            #all assigned, need to redo this index.

        #col_indices = rp.utils.gen_single_axis_index_list(num_cols, goal[1], len(drug_group))
        start_time = time.time()
        df[REDO] = [True] * len(drug_group)
        # 2. get a list of column numbers 
        df[COLS] = random.choices(list(range(1, num_cols)), k=len(df))
        while any(df[REDO]):
            # 2.1. for each position, check that there are enough free spaces in that row
            df[POS] = rp.utils.combine_coord_lists(df[ROWS].to_list(), df[COLS].to_list())
            touching_positions = []
            for i in df.index:
                #TODO: is this comparison correct?
                if num_assigned_to_row >= num_rows:
                    lg.debug(f"Too many wells assigned to row {row}: recalc #{i}")
                    df.loc[i, REDO] = True
                    continue
                # 2.3. for each item in list, check it is not touching any of same primary_target
                # TODO if pos1 touches pos2, only add pos1, not pos2
                # TODO check there are enough free wells to achieve this
                touching = False
                for pos in df[POS]:
                    print(f"pos{pos} df.loc[i,POS]={df.loc[i,POS]}")
                    if is_touching(pos, df.loc[i,POS]) and pos != df.loc[i,POS] and df.loc[i,POS] not in touching_positions \
                        and pos not in touching_positions and not self.plate.at[rp.utils.split_str_coord(pos)].assigned:
                        lg.info(f"Positions touching: {pos}-{df.loc[i,POS]} => recalc #{i}/{pos}")
                        print((f"{is_touching(pos, df.loc[i,POS])} - {pos != df.loc[i,POS]} - {df.loc[i,POS] not in touching_positions}"
                               f"{pos not in touching_positions}"))
                        
                        
                        
                        print(self.plate.at[rp.utils.split_str_coord(pos)].assigned)
                        touching = True
                        touching_positions.append(df.loc[i,POS])
                lg.debug(f"{i}: touching positions = {touching_positions}")
                if touching:
                    df.loc[i, REDO] = True
                    continue
                # if we haven't found a reason not to, mark this position as OK
                df.loc[i, REDO] = False

            # check here for only one well needing redistribution.
            # otherwise, we get into a deadlock where only two touching 

            # for the wells that need recalculation, remove them and redistribute
            #TODO Check for all columns being the same => same as len()==1
            #redo = df[df[REDO]]
            #print(redo)
            if len(touching_positions) == 0:
                drug_group[ROWS] = df[ROWS]
                drug_group[COLS] = df[COLS]
                continue # hooray
            elif len(touching_positions) == 1:
                # need to allow more wells into the list or we get a deadlock
                lg.debug(f"="*80,"\nredoing rows:\n",df[df[REDO]])
                for i in df[df[REDO]].index:
                    while df.at[i,REDO]:
                        old_val = df.at[i,COLS]
                        df.at[i,COLS] = 1 + random.randint(1,num_cols)
                        df.at[i,REDO] = old_val == df.at[i,COLS]

            
            else:
                for i in df[df[REDO]].index:
                    old_val = df.loc[i,COLS]
                    df.loc[i,COLS] = random.randint(1,num_cols)
                    lg.debug(f"i={i}: replaced {old_val} with {df.loc[i,COLS]}")

            if time.time() - start_time > TIMEOUT:
                lg.error("Failed to converge on solution. Using current best attempt...")
                break

        drug_group[ROWS] = df[ROWS]
        drug_group[COLS] = df[COLS]
        drug_group[POS] = rp.utils.combine_coord_lists(df[ROWS].to_list(), df[COLS].to_list())
        lg.info(f"Finished group {group_name}...")

        #print(f"&&& len(df[ROWS])={len(df[ROWS])} len(df[COLS])={len(df[COLS])}")

        # 3. Combine these to get a single list of coordinates. Add this as a new column to df.
        #    Store this list in self, so these positions are marked as assigned.
        positions = rp.utils.combine_coord_lists(df[ROWS].to_list(), df[COLS].to_list())
        #lg.debug(f"positions[{len(positions)}]: {positions}")

        self.store(drug_group, group_name)

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
        random.shuffle(free_wells)
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
    pos1 = rp.utils.coord_as_ints(pos1)
    pos2 = rp.utils.coord_as_ints(pos2)

    rows_dist = abs(pos1[0] - pos2[0])
    cols_dist = abs(pos1[1] - pos2[1])
    return rows_dist + cols_dist <= dist
        

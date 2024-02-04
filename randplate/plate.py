import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import logging
import random
import time
import sys

import randplate as rp

lg = logging.getLogger('randplate')

TIMEOUT = 1
ROW = "row"
COL = "col"
TOUCHING = "redo"
POS = "position"

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
        for i in drug_group.index:
            row = drug_group.at[i, ROW]
            col = drug_group.at[i, COL]
            self.plate.at[row,col].assigned = True
            self.plate.at[row,col].group = group
        self.print(logging.INFO, True)
    

    def generate_coordinates(self, drug_group: pd.DataFrame, goal: (float, float), group_name: str) -> pd.DataFrame:
        """Generate the position matrix for the items in a target group."""
        df = self.gen_nontouching_coords_(drug_group, group_name)
        self.store(df, group_name)
        row_donors, row_recipients = self.get_donor_recipient_lists_(df, goal, group_name, "row")
        col_donors, col_recipients = self.get_donor_recipient_lists_(df, goal, group_name, "col")
        lg.debug(f"{rp.utils.print_sep()}\nRow donors:{row_donors}\nRow recipients:{row_recipients}")
        lg.debug(f"{rp.utils.print_sep()}\nCol donors:{col_donors}\nCol recipients:{col_recipients}")
        self.store(df, group_name)


    def gen_nontouching_coords_(self, drug_group: pd.DataFrame, group_name: str) -> pd.DataFrame:
        """First step in coordinate generation. Find an initial random distribution of non-touching positions.
           The number of assigned wells per column/row is probably not correct."""
        num_rows = self.plate.shape[0]
        num_cols = self.plate.shape[1]
        df = drug_group

        lg.debug("\n" + rp.utils.print_sep() + "\nCalculating coordinates \n" + rp.utils.print_sep())
        start_time = time.time()
        df[TOUCHING] = [True] * len(drug_group)
        df[ROW] = [rp.utils.row_as_str(i) for i in random.choices(list(range(num_rows-1)), k=len(drug_group))]
        df[COL] = random.choices(list(range(1, num_cols)), k=len(df))
        while any(df[TOUCHING]):
            lg.debug("Starting loop...")
            # 2.1. for each position, check that there are enough free spaces in that row
            df[POS] = rp.utils.combine_coord_lists(df[ROW].to_list(), df[COL].to_list())
            for i in df.index:
                if not self.candidate_pos_invalid(df.at[i, POS], df) and not self.is_assigned(df.at[i, POS]):
                    df.at[i, TOUCHING] = False
                    continue
            
            num_redo = len(df[df[TOUCHING]][POS])
            lg.debug(f"{num_redo} touching positions")
            if num_redo == 0:
                lg.debug("Finished")
                drug_group[ROW] = df[ROW]
                drug_group[COL] = df[COL]
                continue # hooray
            else:
                lg.debug(f"{rp.utils.print_sep()}\nrecalculating:\n{df[df[TOUCHING]][POS]}")
                for i in df[df[TOUCHING]].index:
                    old_col = df.at[i, COL]
                    old_row = df.at[i, ROW]
                    df.at[i, COL] = random.randint(1,num_cols)
                    df.at[i, ROW] = rp.utils.row_as_str(random.randint(0,num_rows-1))
                    lg.debug(f"index {i}: replaced col:{old_col}>{df.at[i, COL]} row:{old_row}>{df.at[i, ROW]}")

            if time.time() - start_time > TIMEOUT:
                lg.error("Failed to converge on solution. Using current best attempt...")
                break

        drug_group[ROW] = df[ROW]
        drug_group[COL] = df[COL]
        drug_group[POS] = rp.utils.combine_coord_lists(df[ROW].to_list(), df[COL].to_list())
        lg.info(f"Finished assigning free non-touching positions for {group_name}...")
        lg.debug(f"{rp.utils.print_sep()}\n{drug_group[POS]}")

        return drug_group
    

    def get_donor_recipient_lists_(self, df: pd.DataFrame, goal: (float, float), group_name: str, axis: str) -> (list, list):
        """Go through the axis (row/col), and try to make each contain as close to goal as possible"""
        lg.debug((f"{rp.utils.print_sep()}\nRationalising {axis} distributions for group {group_name}\n"
            f"Goal distribution: {goal}"))
        if axis != "row" and axis != "col":
            raise KeyError(f"Invalid axis: {axis}")


        num_per_row = self.delta_per_axis(df, axis, goal)
        donor_indices = []
        candidate_donor_indices = []
        recipient_rows = [key for key, val in num_per_row.items() if val < 0]
        candidate_recipient_rows = []
        sum_reassign_to = 0
        for row, delta in num_per_row.items():
            if delta > 1:
                sum_row_i_donating = 0
                for i in df.index:
                    if df.at[i, axis] == row and sum_row_i_donating < delta-1:
                        sum_row_i_donating += 1
                        donor_indices.append(i)
            elif delta < 0:
                sum_reassign_to -= delta
            elif delta == 1:
                for i in df.index:
                    if df.at[i, axis] == row:
                        candidate_donor_indices.append(i)
            else: # delta == 0
                for i in df.index:
                    if df.at[i, axis] == row and row not in candidate_recipient_rows:
                        candidate_recipient_rows.append(row)

        
        lg.debug(f"{rp.utils.print_sep()}\nInitial donor indices:{donor_indices} ({len(donor_indices)})\nInitial recipient rows:{recipient_rows} ({sum_reassign_to} free places)")
        lg.debug(f"Candiate donor indices: {candidate_donor_indices}\nCandidate recipient rows:{candidate_recipient_rows}")
        while len(donor_indices) < sum_reassign_to:
            try:
                new_index = candidate_donor_indices.pop()
                lg.debug(f"Not enough indices to reassign - add index {new_index}={df.at[new_index,POS]}")
                donor_indices.append(new_index)
            except IndexError:
                lg.info(f"Ran out of donor candidates. Donor indices:{donor_indices}, recipient ros:{recipient_rows}")


        while len(donor_indices) > sum_reassign_to:
            lg.debug(f"Too many indices to reassign - add some to rows with delta==0")
            try:
                new_row = candidate_recipient_rows.pop()
                recipient_rows.append(new_row)
                sum_reassign_to += num_per_row[new_row]
            except IndexError:
                lg.info(f"Ran out of empty spaces. Donor indices:{donor_indices}, recipient ros:{recipient_rows}")
        lg.debug(f"Donor indices:{donor_indices} positions:{[df.at[i,POS] for i in donor_indices]}")
        return donor_indices, recipient_rows


    def redistribute_donors(self, donor_inidices, recipient_rows, axis, goal, df):
        for i in donor_inidices:
            print (f"index={i} pos={df.at[i,POS]}")
            placed = False
            start_time = time.time()
            """
            This is getting stuck because it doesn't work.
            It doesn't change the column so if none of the candidate positions are ok, it never gets solved
            Also, if it is touching itself, it fails eg moving A01=>B01
            """
            while not placed:
                print(recipient_rows)
                new_row = random.choice(recipient_rows)
                new_pos = rp.utils.make_coord(new_row, df.at[i, COL])
                print(f"Try new row:{new_row} position:{new_pos}")
                if not self.candidate_pos_invalid(new_pos, df):
                    df.at[i, axis] = new_row
                    df.at[i, POS] = rp.utils.make_coord(df.at[i, axis], df.at[i, COL])
                    num_per_row = self.delta_per_axis(df, axis, goal)
                    recipient_rows = [key for key, val in num_per_row.items() if val < 0]
                    print(f"Recipient rows:{recipient_rows}")
                    if num_per_row[new_row] <= 0:
                        lg.debug(f"Row {new_row} is now full")
                    placed = True
                elif time.time() - start_time > .2:
                    print(f"!!! Failed to converge on solution !!!")
                    print("Using current best attempt...")
                    break
        # num_per_col = {}
        # for i in range(1, self.plate.shape[1]):
        #     num_per_col[i] = 0
        # for i in df.index:
        #     col = df.at[i, COL]
        #     if col in num_per_col.keys():
        #         num_per_col[col] += 1
        #     else:
        #         num_per_col[col] = 1
        # lg.debug(f"num per col: {num_per_col}")
        # for col, count in num_per_col.items():
        #     if int(goal[1]) > count or count  > int(goal[1]) + 1:
        #         print(f"Need to redo col {col}")

        return df
                




    def delta_per_axis(self, df: pd.DataFrame, axis: str, goal: (float, float)) -> {str or int, int}:
        """Count the number of assigned positions in df per row or column.
           The value per row/column is the delta away from the goal amount
           ie val<0 means there are not enough assigned, val>1 means there are too many.
           If goal[axis] = 1.5, it is acceptable to have either 1 or 2 assigned per row/column"""
        
        #print(f">>>shape={self.plate.shape}")
        
        if axis == "row":
            shape_i = 0
        elif axis == "col":
            shape_i = 1
        else:
            raise KeyError(f"Unknown axis: {axis}")
        goal = goal[shape_i]
        num_per_axis = {}
        for i in range(self.plate.shape[shape_i]):
            if axis == "row":
                num_per_axis[rp.utils.row_as_str(i)] = -int(goal)
            else:
                num_per_axis[i] = -int(goal)

        lg.debug(f"Delta per row: {num_per_axis}")

        for i in df.index:
            row = df.at[i, axis]
            if axis == "col":
                row = row-1
                print(type(row))
            num_per_axis[row] += 1

        #lg.debug(f"num per row: {num_per_axis}")
        # randomise order
        l = list(num_per_axis.items())
        random.shuffle(l)
        num_per_axis = dict(l)
        for key,val in num_per_axis.items():
            num_per_axis[key] = val 
        lg.debug(f"num per row: {num_per_axis}")
        return num_per_axis


    def is_assigned(self, row: int or str, col: int = None) -> bool:
        """Helper function to show if given well position is assigned."""
        if col is None:
            row, col = rp.utils.split_str_coord(row)
            return self.plate.at[row,col].assigned
        else:
            return self.plate.iloc[row,col].assigned
        

    def get_rand_free_coord(self) -> str:
        free_wells = []
        for row in self.plate.shape[0]:
            for col in self.plate.shape[1]:
                print(f"TEST {row} {col}")
                if not self.is_assigned(row, col):
                    free_wells.append(self.plate.iloc[row,col])
        if not free_wells:
            raise RuntimeError("No free wells remaining")
        random.shuffle(free_wells)
        return free_wells[0].ident

    def candidate_pos_invalid(self, candidate: str, df: pd.DataFrame) -> bool:
        touching = False
        for pos in df[POS]:
            if _is_touching(candidate, pos):
                touching = True
        return touching
        

def _is_touching(pos1: str, pos2: str, dist_limit: int = 1) -> bool:
    """Returns True if the two given positions are within dist wells of each other. 
    Diagonal distances are not considered.
    If the positions are the same, False is returned."""
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
        # return False or we have to always guard against checking a position against itself
        return False
    pos1n = rp.utils.coord_as_ints(pos1)
    pos2n = rp.utils.coord_as_ints(pos2)

    rows_dist = abs(pos1n[0] - pos2n[0])
    cols_dist = abs(pos1n[1] - pos2n[1])
    return rows_dist + cols_dist <= dist_limit


        

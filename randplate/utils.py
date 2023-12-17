import logging as lg
import random

import pandas as pd
import numpy as np 


PRINT_HDR_WD=80

DEBUG=True

def print_sep():
    return("="*PRINT_HDR_WD)

def list_df_items(plate_layout):
    my_list = []
    for row in range(plate_layout.shape[0]):
        for col in range(plate_layout.shape[1]):
            #print(plate_layout.iat[row, col])
            my_list.append(plate_layout.iat[row,col])
    return my_list

def init_logger(level):
    lg.getLogger().setLevel(level)

def log_lvl():
    return lg.getLogger().getEffectiveLevel()

#
# assigned_coords -> Plate
# df -> dataframe of drugs to position
#       for each drug, we need to generate a position on the assigned_coords Plate
#       we assume this dataframe has already been randomised, and can therefore assign them
#       row and column indices, up to the shape of assigned_coords
# goal -> how many each (row,column) should have on average
#
# The generated coordinates are stored in assigned_coords object. 
# No return value.
def generate_coordinates(assigned_coords, df, goal):
    rows = assigned_coords.shape[0]
    cols = assigned_coords.shape[1]

    row_indices = gen_single_axis_index_list(rows, goal[0], len(df))
    col_indices = gen_single_axis_index_list(cols, goal[1], len(df))

    lg.debug(f"row_indices[{len(row_indices)}]: {row_indices}")
    lg.debug(f"col_indices:[{len(col_indices)}] {col_indices}")

    assigned_coords.store(row_indices, col_indices)



def gen_single_axis_index_list(num_items, goal, len_df):
    indices = []
    cur_col = 0
    indices_per_row = int(goal)

    lg.debug(f"indices_per_row={indices_per_row}")
    for i in range(num_items): # for each row
        # assign indices_per_row
        for _ in range(indices_per_row):
            indices.append(cur_col)
        cur_col += 1

    cur_col = 0
    while (len(indices) < len_df):
        indices.append(cur_col)
        cur_col += 1

    random.shuffle(indices)

    return indices


    

import logging as lg
import random

import pandas as pd
import numpy as np 


PRINT_HDR_WD=80
POS_COL_NAME='pos'

DEBUG=True

def print_sep() -> str:
    return("="*PRINT_HDR_WD)

def list_df_items(plate_layout: pd.DataFrame) -> list:
    my_list = []
    for row in range(plate_layout.shape[0]):
        for col in range(plate_layout.shape[1]):
            #print(plate_layout.iat[row, col])
            my_list.append(plate_layout.iat[row,col])
    return my_list

def init_logger(level: int) -> None:
    lg.getLogger().setLevel(level)

def log_lvl() -> int:
    return lg.getLogger().getEffectiveLevel()



def gen_single_axis_index_list(num_items: int, goal: float, len_df: int) -> list:
    """Generate a random list of indices (num_items long) for a single axis, with average {goal} per column/row assigned"""
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


def row_as_str(row_as_int: int) -> str:
    """Awful way to convert a plate's row letter int to corresponding string"""
    table = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'Y', 24: 'X', 25: 'Z'}
    return table[row_as_int]


def combine_coord_lists(rows: list, cols: list) -> list:
    if len(rows) != len(cols):
        raise ValueError("Can only combine lists of same lengths")
    
    out = []
    for i in range(len(rows)):
        out.append(f"{row_as_str(rows[i])}{cols[i]+1:02d}")
    return out

    
    

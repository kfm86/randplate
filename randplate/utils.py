import logging as lg
import random
import re

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
    """Convert a plate's row int to corresponding string"""
    return chr(row_as_int + ord('A'))

def row_as_int(row_as_str: str) -> int:
    """Convert a plate's row string to corresponding int"""
    return ord(row_as_str) - ord('A')


def combine_coord_lists(rows: list, cols: list) -> list:
    if len(rows) != len(cols):
        raise ValueError("Can only combine lists of same lengths")
    
    out = []
    for i in range(len(rows)):
        out.append(f"{row_as_str(rows[i])}{cols[i]+1:02d}")
    return out

def split_str_coord(coord: str) -> (int, int):
    #print(f"1={re.search('[A-Z]', coord).group(0)} 2={re.split('[A-Z]', coord)[1]}")
    return (row_as_int(re.search('[A-Z]', coord).group(0)), int(re.split('[A-Z]', coord)[1]))

    
    

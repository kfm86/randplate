import logging


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

def init_log(level):
    logging.getLogger().setLevel(level)

def log_lvl():
    return logging.getLogger().getEffectiveLevel()


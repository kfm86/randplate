#!/usr/bin/env python

import csv
import pandas as pd
import numpy as np
import argparse
import logging as lg

import randplate as rp


def main():
    parser = argparse.ArgumentParser(
        prog="randomiser",
        description="Tool to randomly assign a list of drugs to positions on a plate, based on their mechanism/target")
    parser.add_argument('plate')
    parser.add_argument('drug_list')
    parser.add_argument('--log', '-l', action="store", default="INFO")
    args = parser.parse_args()

    rp.utils.init_log(args.log)

    plate = rp.Plate(args.plate)
    plate.print()

    drug_list = rp.DrugList(args.drug_list)
    drug_list.print()

    targets = drug_list.drugs.primary_target.value_counts()
    msg = f"\n{rp.utils.print_sep()}\nUsing the following primary target mechanisms:\n{targets}\n"
    lg.info(msg)

    controls = drug_list.drugs.query("primary_target == 'Control'")
    msg = f"Using {len(controls)} controls"
    lg.debug(msg)







if __name__ == "__main__":
    main()


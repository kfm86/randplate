#!/usr/bin/env python

import argparse

import randplate as rp


# TODO:
# - Main task
# - tests
# - documentation



def main():
    parser = argparse.ArgumentParser(
        prog="randomiser",
        description="Tool to randomly assign a list of drugs to positions on a plate, based on their mechanism/target")
    parser.add_argument('plate')
    parser.add_argument('drug_list')
    parser.add_argument('--log', '-l', action="store", default="INFO")
    args = parser.parse_args()

    rp.utils.init_logger(args.log)

    # 1. Read in input files
    plate = rp.Plate(args.plate)
    plate.print()

    drug_list = rp.DrugList(args.drug_list, plate)
    drug_list.print()

    # 2. Calculate random distributions of each mechanism 
    drug_list.calculate_disributions()



    # 3. Turn into histograms

    # 4. Print/save output







if __name__ == "__main__":
    main()


#/usr/bin/env python

import argparse

def main():
    parser = argparse.ArgumentParser(prog="gen_test_csv_file")
    parser.add_argument("cfg_in_file", action="store", default="gen_test.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", default=False)

    args = parser.parse_args()

    # Read in a yaml file
    # Parse yaml file for test setup
    # Write the test setup to an output file


if __name__ == "__main__":
    main()

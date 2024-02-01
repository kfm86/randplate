import pandas as pd
import logging
import sys

import randplate as rp

lg = logging.getLogger('randplate')

class DrugList:
    """Class to handle reading, parsing, and grouping of a test input file."""
    def __init__(self, filename: str, plate: rp.Plate):
        """Read given input file and store as pd.Dataframe"""
        lg.info(f"Reading test file: {filename}")
        try:
            self.drugs = pd.read_csv(filename, delimiter=";").sample(frac=1).reset_index(drop=True)
        except OSError as ex:
            lg.error(f"Unable to open file '{filename}':{str(ex)}")
            sys.exit(1)
        except IndexError:
            lg.error(f"Failed to parse test file '{filename}'. Please verify the format.")
            sys.exit(1)
        self.plate = plate

    def print(self, level: int = logging.DEBUG) -> None:
        """Print a helpful message"""
        msg = f"\n{rp.utils.print_sep()}\nAssigning drugs:\n{self.drugs}\n{rp.utils.print_sep()}"
        lg.log(level, msg)


    # Called from main
    def calculate_disributions(self) -> rp.Plate:
        """Calculate the well-position for each drug listed in the input file."""
        lg.debug("Calculating distributions...")

        # 1. Split self.drugs (pd.DataFrame) by value of primary_target column i.e. to group by primary target
        num_targets = self.drugs.primary_target.value_counts()
        msg = f"\n{rp.utils.print_sep()}\nUsing the following primary target mechanisms:\n{num_targets}\n"
        lg.info(msg)

        # controls = self.drugs.query("primary_target == 'Control'")
        # msg = f"Using {len(controls)} controls"
        # lg.debug(msg)
        
        # use following for grouping
        # for group in self.drugs.groupby(['primary_target']):
        #     print(group.)

        # 2. Generate the list of positions for each group

        # Start with DNA for ease...

        dna_targetting = self.calc_("DNA")

        controls = self.calc_("Control")
        #print(dna_targetting)


        # what to do with results?
        # each group's dataframe should be returned, or maybe: the calculated positions should be combined into a list and added to self.plate
        # then self.plate is returned
        return self.plate


    def calc_(self, primary_target: str) -> pd.DataFrame:
        """Calculate positions for a primary target group. Outputs a dataframe with new pos, col, and row columns."""
        goal = self.drugs.query(f'primary_target == "{primary_target}"').shape[0]
        goal = (goal/self.plate.shape[0], goal/self.plate.shape[1])
        
        msg = f"{rp.utils.print_sep()}\nIdeal distribution: {goal}"
        lg.debug(msg)

        num_in_series = 1

        #get a dataframe of a group of primary_target values - in this case, DNA is most common
        matches = self.drugs[self.drugs.primary_target == primary_target]
        lg.debug(f"Using the columns:\n{matches.columns}")

        # generate a list of positions for each row in the primary_target group
        # then we add this list to matches as a new column
        matches = self.plate.generate_coordinates(matches, goal, primary_target)
        
        return matches



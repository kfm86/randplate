import pandas as pd
import logging as lg
import sys

import randplate as rp

class DrugList:
    def __init__(self, filename, plate):
        lg.info(f"Reading test file: {filename}")
        try:
            self.drugs = pd.read_csv(filename, delimiter=";")
            self.drugs['Plate'] = "___"
        except OSError as ex:
            lg.error(f"Unable to open file '{filename}':{str(ex)}")
            sys.exit()
        self.plate = plate

    def print(self, level=lg.DEBUG):
        msg = f"\n{rp.utils.print_sep()}\nAssigning drugs:\n{self.drugs}\n{rp.utils.print_sep()}"
        lg.log(level, msg)

    def calculate_disributions(self):
        lg.debug("Calculating distributions...")

        num_targets = self.drugs.primary_target.value_counts()
        msg = f"\n{rp.utils.print_sep()}\nUsing the following primary target mechanisms:\n{num_targets}\n"
        lg.info(msg)

        controls = self.drugs.query("primary_target == 'Control'")
        msg = f"Using {len(controls)} controls"
        lg.debug(msg)
        
        # use following for grouping
        #self.drugs.groupby(['primary_target'])

        ## TODO: need to do the following for each group of primary_target, programatically
        dna_targetting = self.drugs.query('primary_target == "DNA"').sample(frac=1).reset_index(drop=True)
        msg = f"\n{rp.utils.print_sep()}DNA-targeting drugs:{dna_targetting}"
        lg.debug(msg)

        #num_placed = pd.Series(dna_targetting.shape, dtype=bool)
        

        #print(dna_targetting.pivot(columns=self.plate.shape[0]))

        self.calc_()


        # 35 / 16 rows = 2.1875
        # 35 / 24 cols = 1.458333



    def calc_(self):
        self.drugs = self.drugs.sample(frac=1).reset_index(drop=True)
        goal = self.drugs.query('primary_target == "DNA"').shape[0]
        goal = (goal/self.plate.shape[0], goal/self.plate.shape[1])
        
        msg = f"{rp.utils.print_sep()}\nIdeal distribution: {goal}"
        lg.debug(msg)

        num_in_series = 1

        #get a dataframe of a group of primary_target values - in this case, DNA is most common
        dna_targetting = self.drugs[self.drugs.primary_target == 'DNA']
        lg.debug(f"Using the columns:\n{dna_targetting.columns}")


        # generate the list of positions
        assigned_coords = rp.Coordinates(self.plate)


        # generate a list of positions for each row in the primary_target group
        positions = rp.utils.generate_coordinates(assigned_coords, dna_targetting, goal)


        # assign the list of positions
        #dna_targetting.loc['Plate'] = range(0, dna_targetting['Plate'].shape[0])
        #lg.debug(f"dna_targetting=\n{dna_targetting['Plate']}")



        # for row in range(1, self.plate.shape[0]):

        #     lg.debug(f"{rp.utils.print_sep()}\nrow={row} num_in_series={num_in_series}")


        #     #self.drugs.query('primary_target == "DNA"').iloc[row].loc['Plate'] = row-1
            
        #     col = "A"

        #     if num_in_series == 0:
        #         num_in_series += 1
        #         continue
        #     if num_in_series/row > goal[0]:
        #         num_in_series += 1
        #         goal[0] += goal[0]
            
        #     lg.debug(f"drugs.iloc[row].loc['Plate']={self.drugs.query('primary_target == "DNA"').iloc[row].loc['Plate']}")
            


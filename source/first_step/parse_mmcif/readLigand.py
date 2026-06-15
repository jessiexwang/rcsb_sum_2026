import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(DIR))
UTIL_DIR = os.path.join(SRC_DIR, "util")
PROJECT_DIR = os.path.dirname(SRC_DIR) 
DATA_DIR = os.path.join(PROJECT_DIR, "data") #data directory
if not os.path.isdir(DATA_DIR): # makes one if it does not exist
    os.makedirs(DATA_DIR)

LOG_DIR = os.path.join(PROJECT_DIR, "log") 
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

sys.path.insert(0, SRC_DIR)
from first_step.parse_mmcif.readLegacy import LegacyReader


class readLignad():
    """class to read the information needed from ligands
    """



    def __init__(self):
        self.l_id_pass = []

    def read(self, id):
        fp = os.path.join(DATA_DIR, "G_1002329", id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        reader.readCategory(category) # read category, save to dictionary
        reader.cleanDict() #clean
        rt_data = reader.d_category # return a dictionary
    
        return rt_data
        
        
    


def main():
    pass




if __name__ == "__main__":
    main()
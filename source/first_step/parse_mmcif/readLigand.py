import os
import sys
import functools
from concurrent.futures import ProcessPoolExecutor

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


#----------logging-----------
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s')
f_handler = logging.FileHandler(os.path.join(LOG_DIR, "readRcsb.log"), mode='w', encoding='utf-8')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(log_format)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(log_format)

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
logger.addHandler(f_handler)
logger.addHandler(c_handler)
#-----------------------------

class readLignad():
    """class to read the information needed from ligands
    """



    def __init__(self):
        self.l_id_pass = []

    def searchCategory(self, group, id, category):
        fp = os.path.join(DATA_DIR, group, id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        res = reader.readCategory(category)
        if res == False: # read category, save to dictionary)
            return id
            
        else:
            reader.cleanDict() #clean
            rt_data = reader.d_category # return a dictionary
            return rt_data

    
    def searchNull(self):

        pass
        
    def filterLigand(self, group, l_id, l_category):
        partial_searchCategory = functools.partial(self.searchCategory, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_searchCategory, l_id, l_category)

        results_list = list(results)

        print(results_list)


def main():
    l_id = ["D_1001407944", "D_1001407945"]
    group = 'G_1002329'

    l_category = ["_pdbx_entity_instance_feature", "pdbx_entity_instance_feature"] # testing purposes

    rl = readLignad()

    rl.filterLigand(group, l_id, l_category)




if __name__ == "__main__":
    main()
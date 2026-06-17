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
from first_step.parse_mmcif.readSingle import workerOne


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

class readPolymer():
    def __init__(self):
        self.category1 = "entity"
        self.category2 = "entity_poly"
        self.category3 = "struct_ref"
        self.category4 = "entity_src_gen"
        self.cat_list1 = ["_entity.src_method", "_entity.pdbx_description"]
        self.cat_list2 = ["_entity_poly.pdbx_seq_one_letter_code "]
        self.cat_list3 = ["_struct_ref.db_code"]
        self.cat_list4 = ["_entity_src_gen.pdbx_gene_src_scientific_name"]
        self.l_category = ["entity", "entity_poly","struct_ref", "entity_src_gen"]
        self.l_cat = [self.cat_list1, self.cat_list2, self.cat_list3, self.cat_list4 ]
     

    def readList(self, l_id, group, category, l_item_category):
        partial_workerOne = functools.partial(workerOne, category, group)
        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_workerOne, l_id)
            # map returns a generator, so convert to list if needed
        results_list = list(results)

        return results_list


    def readPolymer(self, l_id, group):
        
        partial_processList_id = functools.partial(self.readList, l_id, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_processList_id, self.l_category, self.l_category)       

        results_list = list(results)
        print(results_list)
            




        # list of ids
        # parse out the info



        pass



def main():
    l_id = ["D_1001407944", "D_1001407945"]
    group = 'G_1002329'

    rp = readPolymer()
    rp.readPolymer(l_id, group)

if __name__ == "__main__":
    main()
        
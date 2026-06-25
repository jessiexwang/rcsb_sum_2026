import os
import json
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

class consolidateAll():
    def __init__(self):
        pass


    def readJSON(self, fp):
        with open(fp) as json_file:
            one_file = json.load(json_file)

        return one_file
    
    def consolidateGroups(self, category):

        dict_cat = {}

        for i in range(2):
            num = str(i+2)
            fn = category + num + ".json"
            fp = os.path.join(DATA_DIR, "parse_mmcif", fn)
            d_ = self.readJSON(fp)
            dict_cat.update(d_)

        fn_json = category + ".json"
        fp_category_json = os.path.join(DATA_DIR, "consolidating", fn_json)

        with open(fp_category_json, 'w') as fp:
            json.dump(dict_cat, fp, indent= 4)


    def mapCategories(self, l_category):
        with ProcessPoolExecutor() as executor:
            results = executor.map(self.consolidateGroups, l_category)


    def consolidateList(self):

        l_ligand = []

        for i in range(2):
            num = str(i+2)
            fn = "ligand_missing" + num + ".list"
            fp = os.path.join(DATA_DIR, "parse_mmcif", fn)

        with open(fp) as f:
            one_ligand = f.read().splitlines()
            l_ligand.append(one_ligand)


        fn = "ligand_missing.list" 
        fp = os.path.join(DATA_DIR, "consolidating", fn)
        
        with open(fp, 'w') as f:
            # Join the list elements into a single string with a newline character
            data_to_write = '\n'.join(l_ligand)
    
            # Write the data to the file
            f.write(data_to_write)
     





def main():
  
    category = "assembly"
    l_category = ["assembly", "authorship", "cell_divisions", "citation", "data_collection",
                  "exptl_crystal_grow", "pdbx_deposit_group", "polymer", "refine", "source"]

    cA = consolidateAll()
    cA.consolidateGroups(category)
    cA.consolidateList()


if __name__ == "__main__":
    main()
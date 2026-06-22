import os
import sys
import functools
import json

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
from first_step.parse_mmcif.readSingle import workerOne
from first_step.parse_mmcif.readSingle import writeDictToFile

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

class readAssembly:
    def __init__(self):
        self.category1 = "pdbx_struct_assembly"
        self.category2 = "pdbx_struct_assembly_gen"
        self.l_cat = ["_pdbx_struct_assembly.oligomeric_details", "_pdbx_struct_assembly_gen.asym_id_list"]
        self.list = []


    def readTwoCat(self, group, id):
        d1 = workerOne(self.category1, group, id)
        d2 = workerOne(self.category2, group, id)

        d1.update(d2)
        return d1

    def readAssembly(self, group, l_id):
        partial_readTwoCat = functools.partial(self.readTwoCat, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_readTwoCat, l_id)
        # map returns a generator, so convert to list if needed
        self.list = list(results)

        d_category_all = {}

        for i in range(len(l_id)):
            try:
                id = l_id[i]
                d_category = self.list[i]
                logger.info(f"Processing {id}")    
                d_category_all[id] = d_category # for a key [the id], add category info
                
            except IndexError as e:
                logger.error("entry %s with error %s", id, e)
                continue


        fn = "assembly.tsv"
        fp = os.path.join(DATA_DIR, "parse_mmcif", fn)
        fn_json = "assembly.json"
        fp_category_json = os.path.join(DATA_DIR, "parse_mmcif", fn_json)

        writeDictToFile(d_category_all, fp, self.l_cat)

        with open(fp_category_json, 'w') as fp:
            json.dump(d_category_all, fp, indent= 4)




      

def main():
   l_id = ["D_1001407944", "D_1001407945", "D_1001407946"]
   group = 'G_1002329'
   ra = readAssembly()
   ra.readAssembly(group, l_id)

if __name__ == "__main__":
    main()
        
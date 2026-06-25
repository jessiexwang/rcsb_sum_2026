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

class readTwo:
    """a class to read mmcif data files and extract certain metadata from two groups about the entry's structure assembly
    Attributes:
        list: list to combine dictionaries
        l_cat: list of select attributes
    """
    def __init__(self):
        self.list = []
        self.l_cat = []


    def readTwoCat(self, group, cat1, cat2, id):
        """method to read the two categories+ their attributes needed

        Args:
            group (str): group that the entry belongs to
            id (str): dep id
            cat1 (str): first category to parse
            cat2 (str): second category to parse

        Returns:
            dict: dictionary of combined parsed info
        """
        d1 = workerOne(cat1, group, id)
        d2 = workerOne(cat2, group, id)

        d1.update(d2)
        d_new = {}

        for item in self.l_cat:
            d_new[item] = d1[item]

        return d_new
    
    def readTwo(self, group, cat1, cat2, l_id, l_cat, file_name, num):
        """method to parse out all the needed information about an entry

        Args:
            group (str): group that the entry belongs to
            cat1 (str): first category to parse
            cat2 (str): second category to parse
            l_id (str): list of dep ids
            l_cat (str): list of attributes to parse
            file_name (str): name of file out
        """
        self.l_cat = l_cat.copy()
        print(self.l_cat)
        partial_readTwoCat = functools.partial(self.readTwoCat, group, cat1, cat2)

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


        # fn = file_name +".tsv"
        # fp = os.path.join(DATA_DIR, "parse_mmcif", fn)
        fn_json = file_name + num +".json"
        fp_category_json = os.path.join(DATA_DIR, "parse_mmcif", fn_json)


        with open(fp_category_json, 'w') as fp:
            json.dump(d_category_all, fp, indent= 4)

def main():
   l_id = ["D_1001407944", "D_1001407945", "D_1001407946"]
   group = 'G_1002329'
   cat1 = "citation"
   cat2 = "citation_author"
   #l_cat = ["_audit_author.name", "_audit_author.pdbx_ordinal", "_struct.title"]
   l_cat = ["_citation.title", "_citation_author.name"]
   fn = "citation"

   rt = readTwo()
   rt.readTwo(group, cat1, cat2, l_id, l_cat, fn)

if __name__ == "__main__":
    main()
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
from first_step.parse_mmcif.readSingle import workerOne_all

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

class readMore:
    """a class to read mmcif data files and extract certain metadata from any amount of groups about the entry's structure assembly
    Attributes:
        list: list to combine dictionaries
        l_cat: list of select attributes
    """
    def __init__(self):
        self.list = []
        self.l_cat_attr = []

    def readMoreCat(self, group, l_cat, id):
        """method to read the two categories+ their attributes needed

        Args:
            group (str): group that the entry belongs to
            id (str): dep id
            l_cat (str): list of categories to parse

        Returns:
            dict: dictionary of combined parsed info
        """
        dict_all = {}

        for category in l_cat:
            d1 = workerOne_all(category, group, id)
            dict_all.update(d1)
        
        d_new = {}

        for item in self.l_cat_attr:
            d_new[item] = dict_all[item]

        return d_new
    
    def readMore(self, group, l_cat, l_id, l_cat_attr, file_name):
        """method to parse out all the needed information about an entry

        Args:
            group (str): group that the entry belongs to
            cat1 (str): first category to parse
            cat2 (str): second category to parse
            l_id (str): list of dep ids
            l_cat (str): list of attributes to parse
            file_name (str): name of file out
        """
        self.l_cat_attr = l_cat_attr.copy()

        partial_readTwoCat = functools.partial(self.readMoreCat, group, l_cat)

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
        fn_json = file_name + ".json"
        fp_category_json = os.path.join(DATA_DIR, "parse_mmcif", fn_json)


        with open(fp_category_json, 'w') as fp:
            json.dump(d_category_all, fp, indent= 4)

def main():
   l_id = ["D_1001407944", "D_1001407945", "D_1001407946"]
   group = 'G_1002329'
   l_cat = ["citation", "citation_author", "struct"]
   cat1 = "citation"
   cat2 = "citation_author"
   #l_cat = ["_audit_author.name", "_audit_author.pdbx_ordinal", "_struct.title"]
   l_attr = ["_citation.title", "_citation_author.name", "_struct.title"]
   fn = "test"

   rm= readMore()
   rm.readMore(group, l_cat, l_id, l_attr, fn)

if __name__ == "__main__":
    main()
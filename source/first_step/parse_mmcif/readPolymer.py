import os
import sys
import json
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

class readPolymer():
    """ a class to read mmcif data files and extract certain metadata about the entry's polymers
    Attributes:
        category1: first category of metadata
        category2: second category of metadata
        category3: third category of metadata
        category4: fourth category of metadata
        cat_list: list of category attributes
        list: list to combine dictionaries
    """
    def __init__(self):
        self.category1 = "entity"
        self.category2 = "entity_poly"
        self.category3 = "struct_ref"
        self.category4 = "entity_src_gen"
        self.cat_list = ["_entity.src_method", "_entity_src_gen.pdbx_gene_src_scientific_name" ,"_entity.pdbx_description", "_entity_poly.pdbx_seq_one_letter_code", "_struct_ref.db_code"]
        self.list = []



    def readMultipleCat(self, group, id):
        """method to parse data from multiple categories and combine them into one dictionary

        Args:
            group (str): group that the entry belongs to
            id (str): dep id

        Returns:
            dict: dictionary of parsed info
        """
        d1 = workerOne(self.category1, group, id)
        en_type = d1['_entity.type'].copy()
        index_list = []
        for item in en_type:
            print(item)
            if item == "polymer":
                index_list.append(en_type.index(item))
        
        for item in d1:
            l_new = []
            for i in index_list:
                l_new.append(d1[item][i])
            d1[item] = l_new
            

        d2 = workerOne(self.category2, group, id)
        d3 = workerOne(self.category3, group, id)
        d4 = workerOne(self.category4, group, id)

        d1.update(d2)
        d1.update(d3)
        d1.update(d4)

        d_new = {}

        for item in self.cat_list:
            d_new[item] = d1[item]

        return d_new

     


    def readPolymer(self, l_id, group):
        """method to parse out all the needed information about an entry's polymer(s)

        Args:
            l_id (str): list of dep ids
            group (str): group that the entry belongs to
        """

        partial_readMultipleCat = functools.partial(self.readMultipleCat, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_readMultipleCat, l_id)
        # map returns a generator, so convert to list if needed
        self.list = list(results)

        #print(self.list)

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


        fn = "polymer.tsv"
        fp = os.path.join(DATA_DIR, "parse_mmcif", fn)
        fn_json = "polymer.json"
        fp_category_json = os.path.join(DATA_DIR, "parse_mmcif", fn_json)

        writeDictToFile(d_category_all, fp, self.cat_list)

        with open(fp_category_json, 'w') as fp:
            json.dump(d_category_all, fp, indent= 4)


def main():
    l_id = ["D_1001407944", "D_1001407945", "D_1001407946"]
    group = 'G_1002329'

    rp = readPolymer()
    rp.readPolymer(l_id, group)

if __name__ == "__main__":
    main()
        
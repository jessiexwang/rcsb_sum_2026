import os
import sys
import json

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
        self.cat_list = ["_entity.src_method", "_entity.pdbx_description", "_entity_poly.pdbx_seq_one_letter_code", "_struct_ref.db_code"]
        self.list = []


    def writeDictToFile(self, d_all, fp, l_item):
        """a method to write dictionary information into a tsv (tab separated values) file, given a dictionary, a filepath, and a list of headings.
            
            Returns:
                bool: True if the category was read successfully, False otherwise.
        """
        l_h = ["id"]
        l_h.extend(l_item) # add rest of headings
        
        with open(fp, 'w') as f:
            f.write("\t".join(l_h)) #separate headings w tabs
            f.write("\n") # start adding data on a new line
            for id, d_one in d_all.items(): # for each id, take one of the dictionaries (contact/citation)
                if d_one:
                    for i in range(len(list(d_one.values())[0])): # for every value in the dictionary
                        l_line = [id] # new line staring w id
                        for item in l_item: # item (not category)
                            l_line.append(d_one[item][i]) # add all info (items only)
                        f.write("\t".join(l_line)) # combine into a line w a tab separation
                        f.write("\n") # new line for  new data
                else:
                    logger.warning("entry %s has EMPTY dict", id)
                    continue
        return True


    def readMultipleCat(self, group, id):
        d1 = workerOne(self.category1, group, id)
        d2 = workerOne(self.category2, group, id)
        d3 = workerOne(self.category3, group, id)
        d4 = workerOne(self.category4, group, id)

        d1.update(d2)
        d1.update(d3)
        d1.update(d4)

        return d1

     


    def readPolymer(self, l_id, group):
        
        for i in range(len(l_id)):
            id = l_id[i]
            dict = self.readMultipleCat(group, id)
            self.list.append(dict)

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

        self.writeDictToFile(d_category_all, fp, self.cat_list)

        # with open(fp_category_json, 'w') as fp:
        #     json.dump(d_category_all, fp)


def main():
    l_id = ["D_1001407944"]
    # , "D_1001407945"
    group = 'G_1002329'

    rp = readPolymer()
    rp.readPolymer(l_id, group)

if __name__ == "__main__":
    main()
        
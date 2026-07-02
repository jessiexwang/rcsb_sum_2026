import os
import sys
import functools
from concurrent.futures import ProcessPoolExecutor
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

class readEntity():

    def __init__(self):
        pass


    def readNonPolymer(self, group, id):

        fp = os.path.join(DATA_DIR, group, id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        reader.readCategory("entity")
        en_type = reader.d_category['_entity.type'].copy()

        non_poly = []

        for i in range(len(en_type)):
            if en_type[i] != "polymer":
                non_poly.append(reader.d_category["_entity.pdbx_description"][i])

        d_new = {}
        d_new["_entity_summation.id"] = id
        d_new["_entity_summation.non-polymer"] = non_poly

        return d_new
    
    def readEntity(self, group, l_id):

        partial_nonpoly = functools.partial(self.readNonPolymer, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_nonpoly, l_id)

        results_list = list(results)

        d_src_all = {}

        for i in range(len(l_id)):
            try:
                id = l_id[i]
                d_info = results_list[i]
                logger.info(f"Processing {id}")    
                d_src_all[id] = d_info # for a key [the id], add category info
                
            except IndexError as e:
                logger.error("entry %s with error %s", id, e)
                continue


        fn_category_json = "entity.json"
        fp_category_json = os.path.join(DATA_DIR, "chenghua_test_data", fn_category_json)

    
        with open(fp_category_json, 'w') as fp:
                json.dump(d_src_all, fp, indent= 4)


def main():

    l_id = []
    for i in range(16):
        id = 1001407490 + i
        dep_id = "D_" + str(id)
        l_id.append(dep_id)



    group = 'G_1002307'
    


    rE= readEntity()
    rE.readEntity(group, l_id)
    # dict = rm.readManyCat(group, "pdbx_contact_author", "D_1001407490")
    # print(dict)

if __name__ == "__main__":
    main()


        
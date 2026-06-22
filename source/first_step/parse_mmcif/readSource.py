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

class readSource:
    def __init__(self):
        self.l_source = []
        self.src_nat = []
        self.src_gen = []
        self.src_syn = []


    
    
    def filterSource(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        reader.readCategory("entity")
        en_type = reader.d_category['_entity.type'].copy()
        for i in range(len(en_type)):
            if en_type[i] == "polymer":
                src = reader.d_category["_entity.src_method"][i]

                if src == "man": # check if category exists
                    self.l_source.append("entity_src_gen")
                elif src == "nat":
                    self.l_source.append("entity_src_nat")
                else:
                    self.l_source.append("pdbx_entity_src_syn")
                    

    def srcNat(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("entity_src_nat")
        reader.cleanDict() #clean
        rt_data = {}
        for item in reader.d_category:
            if reader.d_category[item] != ["?"]:
                rt_data[item] = reader.d_category[item]
        return rt_data
    
    def srcGen(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("entity_src_gen")
        reader.cleanDict() #clean
        rt_data = {}
        for item in reader.d_category:
            if reader.d_category[item] != ["?"]:
                rt_data[item] = reader.d_category[item]
        return rt_data
    
    def srcSyn(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("pdbx_entity_src_syn")
        reader.cleanDict() #clean
        rt_data = {}
        for item in reader.d_category:
            if reader.d_category[item] != ["?"]:
                rt_data[item] = reader.d_category[item]
        return rt_data
    
    def writeOut(self, src_list, src_type):
        d_src_all = {}

        for i in range(len(src_list)):
            try:
                id = src_list[i][id]
                d_category = src_list[i]
                logger.info(f"Processing {id}")    
                d_src_all[id] = d_category # for a key [the id], add category info
                
            except IndexError as e:
                logger.error("entry %s with error %s", id, e)
                continue



    def readSource(self, group, id):
        self.filterSource(group, id)

        d_all = {}

        res = workerOne("entity", group, id)
        d_all["_entity"] = res

        for i in self.l_source:
            if i == "entity_src_nat":
                res = self.srcNat(group, id)
                d_all["_entity_src_nat"] = res
            elif i == "entity_src_gen":
                res = self.srcGen(group, id)
                d_all["_entity_src_gen"] = res
            elif i == "pdbx_entity_src_syn":
                res = self.srcSyn(group, id)
                d_all["pdbx_entity_src_syn"] = res
            

        return d_all
    
    def mapSource(self, group, l_id):
        
        with ProcessPoolExecutor() as executor:
            results = executor.map(self.readSource, group, l_id)
        
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


        fn_category_json = "source.json"
        fp_category_json = os.path.join(DATA_DIR, "parse_mmcif", fn_category_json)

    
        with open(fp_category_json, 'w') as fp:
                json.dump(d_src_all, fp)



        
    



def main():
    l_id = ["D_1001407944", "D_1001406693", "D_1001400001"] 
    group = 'test_readSource' #testing purposes
    l_group = []

    r = readSource()
    res = r.readSource(group, l_id[1])
    print(res)

    # r.mapSource(group, l_id) # to test

if __name__ == "__main__":
    main()
        
    
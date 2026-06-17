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

class readSource:
    def __init__(self):
        self.source = ""
        self.src_nat = []
        self.src_gen = []
        self.src_syn = []

    
    def filterSource(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        res = reader.readCategory("entity_src_nat")
        if res == False: # check if category exists
            res2 = reader.readCategory("entity_src_gen")
            if res2 == False:
                self.source = "pdbx_entity_src_syn"
            else:
                self.source = "entity_src_gen"
        else:
            self.source = "entity_src_nat"

    def srcNat(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("entity_src_nat")
        reader.cleanDict() #clean
        rt_data = reader.d_category
        return rt_data
    
    def srcGen(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("entity_src_gen")
        reader.cleanDict() #clean
        rt_data = reader.d_category
        return rt_data
    
    def srcSyn(self, group, id):
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("pdbx_entity_src_syn")
        reader.cleanDict() #clean
        rt_data = reader.d_category
        return rt_data

    def readSource(self, group, id):
        self.filterSource(group, id)

        if self.source == "entity_src_nat":
            res = self.srcNat(group, id)
        elif self.source == "entity_src_gen":
            res = self.srcGen(group, id)
        elif self.source == "pdbx_entity_src_syn":
            res = self.srcSyn(group, id)

        return res
    
    def mapSource(self, group, l_id):
        partialSource = functools.partial(self.source, group)
        
        with ProcessPoolExecutor() as executor:
            results = executor.map(partialSource, l_id)
        
        results_list = list(results)

        for i in range(len(results_list)):
            if "_entity_src_gen.entity_id" in results_list[i]: 
                self.src_gen.append(results_list[i])
            if "_entity_src_nat.entity_id" in results_list[i]: 
                self.src_nat.append(results_list[i])
            if "_pdbx_entity_src_syn.entity_id" in results_list[i]: 
                self.src_syn.append(results_list[i])
            
        # to separate into lists, read into json?
        # inprogress

        



def main():
    l_id = ["D_1001407944", "D_1001407945"]
    group = 'G_1002329'

    r = readSource()
    res = r.readSource(group, l_id[0])
    print(res)

if __name__ == "__main__":
    main()
        
    
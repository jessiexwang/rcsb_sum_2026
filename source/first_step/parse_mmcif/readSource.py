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
    """a class to read mmcif data files and extract certain metadata about an entry's entity source(s)
    Attributes:
        l_source: container for a list of sources within an entry
    
    """
    def __init__(self):
        self.l_source = []
    
    def filterSource(self, group, id):
        """method to determine what the source method(s) is/are

        Args:
            group (str): group that the entry belongs to
            id (str): dep id
        """
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
        """method to parse out info of the source is natural from categories with non-null values

        Args:
            group (str): group that the entry belongs to
            id (str): dep id

        Returns:
            dict: dictionary of metadata
        """
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
        """method to parse out info of the source is genetically modified from categories with non-null values

        Args:
            group (str): group that the entry belongs to
            id (str): dep id

        Returns:
            dict: dictionary of metadata
        """

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
        """method to parse out info of the source is synthetic from categories with non-null values

        Args:
            group (str): group that the entry belongs to
            id (str): dep id

        Returns:
            dict: dictionary of metadata
        """
        fp = os.path.join(DATA_DIR, group, id + ".cif")
        reader = LegacyReader(fp)
        reader.readCategory("pdbx_entity_src_syn")
        reader.cleanDict() #clean
        rt_data = {}
        for item in reader.d_category:
            if reader.d_category[item] != ["?"]:
                rt_data[item] = reader.d_category[item]
        return rt_data



    def readSource(self, group, id):
        """method to read the source information of one id

        Args:
            group (str): group that the entry belongs to
            id (str): dep id

        Returns:
            dict: dictionary, where the keys are are type of source and the values are the dictionaries of information
        """
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
    
    def mapSourceOneGroup(self, group, l_id):
        """method to read the source of a list of ids belonging to one group
        Args:
            group (str): group that the entry belongs to
            l_id (str): list of dep ids
        """
        
        partial_readSource = functools.partial(self.readSource, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_readSource, l_id)
        
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
                json.dump(d_src_all, fp, indent= 4)



    def mapSourceMoreGroup(self, l_group, l_id): 
        """method to read the source of a list of ids belonging to multiple groups, given by a list
        that corresponds to the list of ids

        Args:
            l_group (str): groups that the entries belong to, matching the the list of ids
            l_id (str): list of dep ids
        """ 
        with ProcessPoolExecutor() as executor:
            results = executor.map(self.readSource, l_group, l_id)
        
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
                json.dump(d_src_all, fp, indent= 4)

        



def main():
    
    l_id = ["D_1001407944", "D_1001406693", "D_1001400001"] 
    group = 'test_readSource' #testing purposes
    l_group = []

    l_test = ["D_1001400364"]
    group_2 = "G_1002001"

    r = readSource()
    # res = r.readSource(group, l_id[1])
    # print(res)

    r.mapSourceOneGroup(group_2, l_test) # to test

if __name__ == "__main__":
    main()
        
    
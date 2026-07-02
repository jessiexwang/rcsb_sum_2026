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

class readManyCat:
    """a class to read mmcif data files and extract metadata from any amount of groups about the entry, either the entire thing or
    a select attribute
    Attributes:
        list: list to combine dictionaries
        l_cat: list of select attributes
    """
    def __init__(self):
        self.random = ""


    def readManyCat(self, group, category, id):
            """method to read the two categories+ their attributes needed

            Args:
                group (str): group that the entry belongs to
                id (str): dep id
                l_cat (str): list of categories to parse

            Returns:
                dict: dictionary of combined parsed info
            """
    
            d_new = {}      

            
            if "." in category :
                attr = category.index(".")
                actual_cat = category[:attr]

                d1 = workerOne_all(actual_cat, group, id)
                d_new[category] = d1[category]
            else:
                d1 = workerOne_all(category, group, id)
                d_new.update(d1)

            return d_new
    
    def mapManyCat_id(self, group, l_id, category):
         
        partial_workerOne = functools.partial(self.readManyCat, group, category)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_workerOne, l_id)
        # map returns a generator, so convert to list if needed
        results_list = list(results)

        d_category_all = {}

        for i in range(len(l_id)):
            try:
                id = l_id[i]
                d_category = results_list[i]
                logger.info(f"Processing {id} with category {category}")    
                d_category_all[id] = d_category # for a key [the id], add category info
                
            except IndexError as e:
                logger.error("entry %s with error %s", id, e)
                continue

        if "." in category:
            category.replace(".", "-")

        fn_category_json = category + ".json"
        fp_category_json = os.path.join(DATA_DIR, "chenghua_test_data", fn_category_json)

        
        with open(fp_category_json, 'w') as fp:
            json.dump(d_category_all, fp, indent= 4)

         
    def mapManyCat_category(self, group, l_category, l_id):
        partial_manyCat_id = functools.partial(self.mapManyCat_id, group, l_id)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_manyCat_id, l_category)


def main():

    l_id = []
    for i in range(16):
        id = 1001407490 + i
        dep_id = "D_" + str(id)
        l_id.append(dep_id)



    group = 'G_1002307'
    l_cat = ["pdbx_contact_author", "audit_author", "struct", "struct_keywords", "citation", "citation_author",
            "entity_poly", "entity_src_gen", "exptl_crystal_grow", "exptl_crystal", "cell", "symmetry",
            "diffrn_source", "diffrn_detector", "diffrn", "diffrn_radiation","diffrn_radiation_wavelength","reflns",
            'reflns_shell','refine','refine_ls_shell','software','pdbx_audit_support','pdbx_deposit_group',
            'pdbx_entity_instance_feature','pdbx_entity_nonpoly','pdbx_initial_refinement_model','pdbx_struct_assembly']
    


    rm= readManyCat()
    rm.mapManyCat_category(group, l_cat, l_id)
    # dict = rm.readManyCat(group, "pdbx_contact_author", "D_1001407490")
    # print(dict)

if __name__ == "__main__":
    main()
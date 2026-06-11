import csv
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

# sys.path.insert(0, UTIL_DIR)
# from pathFinderNew import PathFinderWwpdbLocal, PathFinderWwpdbLegacy

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


def writeDictToFile(d_all, fp, l_item):
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

def workerOne(category, id):
    fp = os.path.join(DATA_DIR, "G_1002329", id + ".cif")

    logger.info("filepath at %s", fp)
    reader = LegacyReader(fp)
    reader.readCategory(category) # read category, save to dictionary
    reader.cleanDict() #clean
    rt_data = reader.d_category # return a dictionary

    return rt_data

def processList_id(l_id, category, l_item_category):
    """a method to take a list of data files and extracts information from each file  of thelist into two dictionaries: one for  audit contact information and one for  primary citation information. Then, it converts each dictionary into a tsv file.
    
    Returns:
        none.
    """
    #data_folder = "/Users/jessiewang/data"
    # data_folder = "/Users/chenghua/Projects/Training/data"

    l_id_test = l_id

    partial_workerOne = functools.partial(workerOne, category)

    with ProcessPoolExecutor() as executor:
        results = executor.map(partial_workerOne, l_id_test)
    # map returns a generator, so convert to list if needed
    results_list = list(results)

    d_category_all = {}

    for i in range(len(l_id_test)):
        try:
            id = l_id[i]
            d_category = results_list[i]
            logger.info(f"Processing {id} with category {d_category}")    
            d_category_all[id] = d_category # for a key [the id], add category info
            
        except IndexError as e:
            logger.error("entry %s with error %s", id, e)
            continue

    fn_category = category + ".tsv"
    fp_category = os.path.join(DATA_DIR, "parse_mmcif", fn_category)

    writeDictToFile(d_category_all, fp_category, l_item_category)


def processList_category(l_category, l_id, l_item_category):
    for i in l_category:
        processList_id(l_id, l_category[i], l_item_category[i])

        

def main():
    #fn_list = "test_id.list"
    # fn_list = "yes_audit_contact_author.list"
    # fp_list = os.path.join(DATA_DIR, "parse_mmcif", fn_list)

    # with open(fp_list) as f:
    #     l_id = f.read().splitlines() # list of ids, split file at a new line 

    # # logger.info(l_id)


    category = 'exptl_crystal_grow'
    l_category = ['exptl_crystal_grow', 'diffrn_radiation_wavelength', 'source_diffrn_source']
    id = "D_1001407944"
    l_id = ["D_1001407944", "D_1001407945"]
    l_struct_keywords = ['_struct_keywords.entry_id', '_struct_keywords.pdbx_keywords', '_struct_keywords.text']
    l_crystal_grow = ['_exptl_crystal_grow.temp', '_exptl_crystal_grow.method']
    l_radiation_wl = ['_diffrn_radiation_wavelength.wavelength']
    l_diffrn_source = ['_source_diffrn_source.type']
    l_item_cat = [l_crystal_grow, l_radiation_wl, l_diffrn_source]

    #processList_id(l_id, category, l_crystal_grow)
    processList_category(l_id, l_category, l_item_cat) 
    

if __name__ == "__main__":
    main()
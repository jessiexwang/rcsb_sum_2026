import os
import json
import sys
import functools
from concurrent.futures import ProcessPoolExecutor

DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(DIR)
UTIL_DIR = os.path.join(SRC_DIR, "util")
PROJECT_DIR = os.path.dirname(SRC_DIR) 
DATA_DIR = os.path.join(PROJECT_DIR, "data") #data directory
if not os.path.isdir(DATA_DIR): # makes one if it does not exist
    os.makedirs(DATA_DIR)

LOG_DIR = os.path.join(PROJECT_DIR, "log") 
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

#----------logging-----------
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s')
f_handler = logging.FileHandler(os.path.join(LOG_DIR, "parseXml.log"), mode='w', encoding='utf-8')
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

def readJson(fp):
    with open(fp) as json_file:
        data = json.load(json_file)
    
    return data

def filterId(id, fp):
    data = readJson(fp)
    one_d = data[id]

    return one_d

def jsonOut(destination, l_id, fp, fn):
    dict = {}
    classification = readJson(fp)
    
    for id in l_id:
        print(id)
        dict[id] = classification[id]
        
    print(dict)

    fn_json = fn + ".json"
    fp_category_json = os.path.join(DATA_DIR, destination , fn_json)
    
    with open(fp_category_json, 'w') as fp:
        json.dump(dict, fp, indent= 4)


def mapGetIndiviudal(destination, l_id, l_fp, l_fn):


    partial_get = functools.partial(jsonOut, destination, l_id)

    with ProcessPoolExecutor() as executor:
        results = executor.map(partial_get, l_fp, l_fn)

    # for i in range(len(l_fp)):
    #     jsonOut(destination, l_id, l_fp[i], l_fn[i])


    

def main():

    assem = os.path.join(DATA_DIR, "consolidating", "assembly.json")
    auth = os.path.join(DATA_DIR, "consolidating", "authorship.json")
    cell_div = os.path.join(DATA_DIR, "consolidating", "cell_divisions.json")
    citation = os.path.join(DATA_DIR, "consolidating", "citation.json")
    data_coll = os.path.join(DATA_DIR, "consolidating", "data_collection.json")
    exptl = os.path.join(DATA_DIR, "consolidating", "exptl_crystal_grow.json")  
    dep = os.path.join(DATA_DIR, "consolidating", "pdbx_deposit_group.json")    
    poly = os.path.join(DATA_DIR, "consolidating", "polymer.json")    
    ref = os.path.join(DATA_DIR, "consolidating", "refine.json")         
    #src = os.path.join(DATA_DIR, "consolidating", "source.json") 

    l_fp = [assem, auth, cell_div, citation, data_coll, exptl, dep, poly, ref]
    l_id = ["D_1001404927", "D_1001404928", "D_1001404929", "D_1001405411", "D_1001405412", "D_1001405413"]     
    
    destination = os.path.join(DATA_DIR, "test_data")

    l_fn  = ["assem", "auth", "cell_div", "citation", "data_coll", "exptl", "dep", "poly", "ref"]

    mapGetIndiviudal(destination, l_id, l_fp, l_fn)
    

if __name__ == "__main__":
    main()
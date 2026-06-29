import os
import json
import sys

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

def jsonOut(destination, id, fp):
    dict = filterId(id, fp)

    fn_json = id + ".json"
    fp_category_json = os.path.join(DATA_DIR, destination , fn_json)
    
    with open(fp_category_json, 'w') as fp:
        json.dump(dict, fp, indent= 4)


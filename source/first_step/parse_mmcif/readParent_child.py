import os
import sys

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
from first_step.parse_mmcif.readLigand import readLigand as rL
from first_step.parse_mmcif.readSource import readSource as rS
from first_step.parse_mmcif.compareAssembly import compareAssembly as cA

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


def sort(process, group, l_id, index = None):
    """sort list of ids into diff processes
    """

    if process == "source":
        rS.mapSource(group, l_id)
        src_nat = rS.srcNat
        src_gen = rS.srcGen
        src_syn = rS.srcSyn
    elif process == "ligand":
        rL.filterLigand(group, l_id)
    elif process == "assembly":
        cA.mapAssembly(group, l_id, index)
    else:
        logger.error("Not a valid process.")

  


def main():
    pass




if __name__ == "__main__":
    main()
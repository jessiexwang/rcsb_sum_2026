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
from first_step.parse_mmcif.readLigand import readLigand 
from first_step.parse_mmcif.readSource import readSource 
from first_step.parse_mmcif.readAssembly import readAssembly 
from first_step.parse_mmcif.readTwo import readTwo 
from first_step.parse_mmcif.readPolymer import readPolymer 
from first_step.parse_mmcif.readSingle import processList_category 

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


def parseAll(group, l_id, num):
    """run through different processes for the list of ids 
    """

    rL = readLigand()
    rS = readSource()
    rA = readAssembly()
    rP = readPolymer()
    rT = readTwo()

    # -------- single categories ---------#
    l_single = ["exptl_crystal_grow", "refine", "pdbx_deposit_group"]
    l_1 = ["_exptl_crystal_grow.temp", "_exptl_crystal_grow.method"]
    l_2 = ["_refine.ls_d_res_high"]
    l_4 = ["_pdbx_deposit_group.group_title", "_pdbx_deposit_group.group_description"]

    l_single_attr = [l_1, l_2, l_4]

    processList_category(l_id, l_single, l_single_attr, group, num) 
    # ------------------------------------


    # # ---------- two categories ----------
    l_cat1 = ["_diffrn_radiation_wavelength.wavelength", "_diffrn_source.type"]
    rT.readTwo(group, cat1="diffrn_radiation_wavelength", cat2="diffrn_source", l_id=l_id, l_cat=l_cat1, file_name="data_collection", num=num)

    l_cat2 = ["_audit_author.name", "_audit_author.pdbx_ordinal", "_struct.title"]
    rT.readTwo(group, "audit_author", "struct", l_id, l_cat2, "authorship", num)

    l_cat3 = ["_citation.title", "_citation_author.name"]
    rT.readTwo(group, "citation", "citation_author", l_id, l_cat3, "citation", num)

    l_cat4 = ["_cell.entry_id", "_cell.length_a", "_cell.length_b", "_cell.length_c", "_cell.angle_alpha", 
              "_cell.angle_beta", "_cell.angle_gamma", "_cell.Z_PDB", "_cell.pdbx_unique_axis", "_symmetry.space_group_name_H-M"]
    rT.readTwo(group, "cell", "symmetry", l_id, l_cat4, "cell_divisions", num)


    # ------------------------------------

    # ------------ complicated -----------

    rL.filterLigand(group, l_id, num) 
    rS.mapSourceOneGroup(group, l_id, num)
    rA.readAssembly(group, l_id, num)
    rP.readPolymer(group, l_id, num)

    # ---------------------------------------

  
def map_parseAll(l_groups, l_ids, l_num):

    with ProcessPoolExecutor() as executor:
        results = executor.map(parseAll, l_groups, l_ids, l_num)




def main():

    l_id1 = []
    l_id2 = []
    l_id3 = []

    for i in range(364):
       id = 1001400001 + i
       dep_id = "D_" + str(id)
       l_id1.append(dep_id)

    for i in range(258):
       id = 1001404297 + i
       dep_id = "D_" + str(id)
       l_id2.append(dep_id)

    for i in range(223):
       id = 1001405411 + i
       dep_id = "D_" + str(id)
       l_id3.append(dep_id)

    l_ids = [l_id1, l_id2, l_id3]


    group1 = "G_1002001"
    group2 = "G_1002241"
    group3 = "G_1002264"

    l_groups = [group1, group2, group3]

    l_num = ["1", "2", "3"]

    map_parseAll(l_groups, l_ids, l_num)



if __name__ == "__main__":
    main()
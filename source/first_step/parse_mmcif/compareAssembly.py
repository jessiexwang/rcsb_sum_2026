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
from first_step.parse_mmcif.readSingle import workerOne

class compareAssembly:
    def __init__(self):
        self.data1 = {}
        self.data2 = {}


    def compareAssembly(self, group, id1, id2):
        category = "pdbx_struct_assembly_gen"
        #self.data1 = workerOne(category, group, id1)
        #self.data2 = workerOne(category, group, id2)

        #list1 = self.data1["_pdbx_struct_assembly_gen.asym_id_list"]
        #list2 = self.data2["_pdbx_struct_assembly_gen.asym_id_list"]
        list1 = ['A,C,D,I', 'B,E,F,G,H,J']
        list2 = ['B,E,F,G,H,J', 'A,C,D,I']

        sorted1 = sorted(list1)
        sorted2 = sorted(list2)

        if sorted1 == sorted2:
            print ("The {id1} and {id2} are the same")
        else:
            print ("The{id1} and {id2} are not the same")





      

def main():
   id1 = "D_1001407944"
   id2 = "D_1001407945"
   group = 'G_1002329'
   ca = compareAssembly()
   ca.compareAssembly(group, id1, id2)
   pass

if __name__ == "__main__":
    main()
        
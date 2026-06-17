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
        self.base = ""
        self.data1 = {}
        self.data2 = {}


    def compareAssembly(self, group, id1, id2):
        category = "pdbx_struct_assembly.oligomeric_details"

        self.data1 = workerOne(category, group, id1)
        self.data2 = workerOne(category, group, id2)

        list1 = self.data1["_pdbx_struct_assembly.oligomeric_details"]
        list2 = self.data2["_pdbx_struct_assembly.oligomeric_details"]
    

        sorted1 = sorted(list1)
        sorted2 = sorted(list2)

        if sorted1 == sorted2:
            return
        else:
            return id2

    def mapAssembly(self, l_id, index):
        self.base = l_id[index] # pick an id to serve as the basis

        partialCompare = functools.partial(self.compareAssembly, self.base)
        
        with ProcessPoolExecutor() as executor:
            results = executor.map(partialCompare, l_id)
        
        results_list = list(results)

        return results_list
        




      

def main():
   id1 = "D_1001407944"
   id2 = "D_1001407945"
   group = 'G_1002329'
   ca = compareAssembly()
   ca.compareAssembly(group, id1, id2)

if __name__ == "__main__":
    main()
        
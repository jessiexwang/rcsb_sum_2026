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

class readAssembly:
    def __init__(self):
        self.category1 = "pdbx_struct_assembly"
        self.category2 = "pdbx_struct_assembly_gen"
        self.l_cat = ["_pdbx_struct_assembly.oligomeric_details", "_pdbx_struct_assembly_gen.asym_id_list"]
        self.data1 = {}
        self.data2 = {}


    def readTwoCat(self, group, id):
        d1 = workerOne(self.category1, group, id)
        d2 = workerOne(self.category2, group, id)

        d1.update(d2)
        return d1

    def readAssembly(self, group, l_id):
        pass

    def mapAssembly(self, l_id, index):
        self.base = l_id[index] # pick an id to serve as the basis

        partialCompare = functools.partial(self.compareAssembly, self.base)
        
        with ProcessPoolExecutor() as executor:
            results = executor.map(partialCompare, l_id)
        
        results_list = list(results)

        return results_list
        




      

def main():
   l_id = ["D_1001407944", "D_1001407945", "D_1001407946"]
   group = 'G_1002329'
   ra = readAssembly()
   ra.readAssembly(group, l_id)

if __name__ == "__main__":
    main()
        
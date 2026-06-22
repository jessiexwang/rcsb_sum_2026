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

class readLigand:
    """a class to read mmcif data files and find entries missing the Ligand of Interest (LOI)
    this classes searches the file and determines if `_pdbx_entity_instance_feature` is missing 
    or there is a null value in `_pdbx_entity_instance_feature.auth_comp_id`. 
    Attributes:
        l_id_null: list of ids that do not have the category `_pdbx_entity_instance_feature`
        l_id_to_null: list of ids to check for a null value in `_pdbx_entity_instance_feature.auth_comp_id`
    """
  
    def __init__(self):
        self.l_id_null = []
        self.l_id_to_null =[]

    def searchCategory(self, group, id):
        """method to search for the `pdbx_entity_instance_feature` category

        Args:
            group (str): group that the entry belongs to
            id (str): deposition id

        Returns:
            str: dep id
            or
            str: tuple of (dep id, dictionary of information)
        """
        fp = os.path.join(DATA_DIR, group, id + ".cif")

        logger.info("filepath at %s", fp)
        reader = LegacyReader(fp)
        res = reader.readCategory("pdbx_entity_instance_feature")
        if res == False: # check if category exists
            return id
            
        else:
            reader.cleanDict() #clean
            rt_data = reader.d_category # return a dictionary
            print(type((id, rt_data)))
            return (id, rt_data)

    
    def searchNull(self, id_tuple):
        """method to search for null values

        Args:
            id_tuple (str, str): _description_
        """
        info = id_tuple[1]
        if info['_pdbx_entity_instance_feature.comp_id'] == ['?'] or info['_pdbx_entity_instance_feature.comp_id'] == ['.'] or info['_pdbx_entity_instance_feature.comp_id'] == ['']: 
           self.l_id_null.append(id_tuple[0])

        
    def filterLigand(self, group, l_id):
        """method to filter for entries that are missing lingand info and write out into a list

        Args:
            group (str): group that the entry belongs to
            l_id (str): list of dep ids
        """
        partial_searchCategory = functools.partial(self.searchCategory, group)

        with ProcessPoolExecutor() as executor:
            results = executor.map(partial_searchCategory, l_id)

        results_list = list(results)
        

        for i in range(len(results_list)):
            if type(results_list[i]) == str:
                self.l_id_null.append(results_list[i])

            else: 
                self.l_id_to_null.append(results_list[i])

        

        
        for i in range(len(self.l_id_to_null)):
            self.searchNull(self.l_id_to_null[i])
        
        fn = "ligand_missing.list"
        fp = os.path.join(DATA_DIR, "parse_mmcif", fn)
        
        with open(fp, 'w') as f:
            # Join the list elements into a single string with a newline character
            data_to_write = '\n'.join(self.l_id_null)
    
            # Write the data to the file
            f.write(data_to_write)
            


def main():
    l_id = ["D_1001407944", "D_1001407945"]
    group = 'G_1002329'

    #l_category = ["_pdbx_entity_instance_feature", "pdbx_entity_instance_feature"] # testing purposes

    rl = readLigand()

    rl.filterLigand(group, l_id)




if __name__ == "__main__":
    main()
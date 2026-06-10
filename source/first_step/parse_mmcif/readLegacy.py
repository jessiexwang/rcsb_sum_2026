# --- for server use ----

import logging
import os
import sys
from mmcif.io.IoAdapterCore import IoAdapterCore

DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(DIR))
UTIL_DIR = os.path.join(SRC_DIR, "util")
PROJECT_DIR = os.path.dirname(SRC_DIR) 
DATA_DIR = os.path.join(PROJECT_DIR, "data") #data directory
if not os.path.isdir(DATA_DIR): # makes one if it does not exist
    os.makedirs(DATA_DIR)


sys.path.insert(0, UTIL_DIR)
from convertCatDataFormat import convertCatObjToDict

## ^ ask

# ------------------------
# place holder to a class to read legacy? the mmcif data files and extract specific information.

logger = logging.getLogger(__name__)


class LegacyReader:
    """A class to read legacy data files and extract specific information.
    This class reads a file, extracts the 'audit_contact_author' category, 
    and 'citation' category primary publication's pubmed id and doi.
    It stores the extracted data in a dictionary LegacyReader.d_.
    Attributes:
        filepath (str): The path to the legacy data file.
        l_dc (list): List of data categories read from the file.
        dc0 (object): The first data category object.
        d_ (dict): Dictionary to store extracted data.
    Methods:
        __init__(filepath): Initializes the reader with the file path.
        readCategory(): Reads the 'audit_contact_author' category and updates the dictionary.
        cleanDict(): Cleans the dictionary by removing tab and return char.
    """
    def __init__(self, filepath):
        if not os.path.isfile(filepath):
            logger.error("failed to find file at %s", filepath)
            sys.exit(1)
            
        logger.info("start to read %s", filepath)
        self.io = IoAdapterCore()
        self.l_dc = self.io.readFile(filepath)
        self.dc0 = self.l_dc[0]
        logger.info("finished reading %s", filepath)
        
        self.d_category = {}

        
    def readCategory(self, category):
        """a method to read a category from the legacy data file.
        This method checks if the  category exists in the data categories.
        If it exists, it converts the category object to a dictionary and updates the instance's dictionary.
        
        Returns:
            bool: True if the category was read successfully, False otherwise.
        """
        if category not in self.dc0.getObjNameList():
            logger.error("failed to find category") 
            return False
        
        if type(category) is not str:
            logger.error("category not in string format") 
            return False

        try:
            c_cat = self.dc0.getObj(category)
            self.d_category = convertCatObjToDict(c_cat)  # use convertCatObjToDict utility to convert category object to dictionary
            return True
        except Exception as e:
            logger.error("failed to read category with error %s", e)
            return False

        
    # def readCitationPrimary(self):
    #      """a method to read the citation category from the legacy data file.
    #     This method checks if the 'citation' category exists in the data categories.
    #     If it exists, it converts two category objects (pdbx_database_id_PubMed and .pdbx_database_id_DOI) to a dictionary and updates the instance's dictionary.
        
    #     Returns:
    #         bool: True if the category was read successfully, False otherwise.
    #      """
    #      d_new = {}


    #      if "citation" not in self.dc0.getObjNameList():
    #          logger.error("failed to find citation")
    #          return False

    #      try:
    #          c_cat = self.dc0.getObj("citation")
    #          d_cat = convertCatObjToDict(c_cat)
    #          for i in range(len(list(d_cat.values())[0])):
    #              if d_cat["_citation.id"][i].lower() == "primary":
    #                  self.d_citation["_citation.pdbx_database_id_PubMed"] = [d_cat["_citation.pdbx_database_id_PubMed"][i]]
    #                  self.d_citation["_citation.pdbx_database_id_DOI"] = [d_cat["_citation.pdbx_database_id_DOI"][i]]
    #                  break
    
    #          logger.info(f"d_citation is now {self.d_citation}")
    #          return True
            
    #      except Exception as e:
    #          logger.error("failed to read citation with error %s", e)
    #          return False
        

    def cleanOne(self, input):
        return ' '.join(str(input).split())

         
    def cleanDictOne(self, d_one):
         """a method to clean the dictionary of extracted data by removing special characters that could cause errors
        
        Returns:
            bool: True if the category was read successfully, False otherwise.
         """
         try:
             for key, value in d_one.items():
                 for i in range(len(list(value))):
                     d_one[key][i] = self.cleanOne(value[i])        
             return True

         except Exception as e:
             logger.error("failed to clean dictionary with error %s", e)
             return False

    def cleanDict(self):
        if self.d_category:
            self.cleanDictOne(self.d_category)

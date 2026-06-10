# --- for server use ----

import os ,shutil,sys,traceback
from mmcif.io.IoAdapterCore import IoAdapterCore as IoAdapter

class GetGroupEntryFiles(object):
    """ Class for copying the latest version of group's entry cif files from archive directory to local directory
    """
    def __init__(self, verbose=False, log=sys.stderr):
        """
        """
        self.__verbose = verbose
        self.__lfh = log
        #
        # The following top directory paths need to be adjusted accordingly 
        #
        self.__topGroupDirPath = "/wwpdb_da/da_top/data_depgrp/autogroup"
        self.__topGroupArchiveDirPath = "/wwpdb_da/da_top/data_depgrp/archive"
        self.__myLocalDirPath = "/home_local/jessie"

    def run(self, groupId):
        """
        """
        try:
            groupCifFile = os.path.join(self.__topGroupDirPath, groupId, groupId + ".cif")
            if not os.access(groupCifFile, os.F_OK):
                self.__lfh.write("Group Cif file '%s' does not exist.\n" % groupCifFile)
                return
            #
            readIoObj = IoAdapter()
            cifContainerList = readIoObj.readFile(groupCifFile)
            if len(cifContainerList) == 0:
                self.__lfh.write("Read Group Cif file '%s' failed.\n" % groupCifFile)
                return
            #
            catObj = cifContainerList[0].getObj("pdbx_deposit_group_index")
            if not catObj:
                self.__lfh.write("Group Cif file '%s' does not have 'pdbx_deposit_group_index' category.\n" % groupCifFile)
                return
            #
            depIdList = []
            for rowIndex in range(catObj.getRowCount()):
                formatType = self.__getValue(catObj, "auth_file_content_type", rowIndex)
                depId = self.__getValue(catObj, "dep_set_id", rowIndex)
                if depId and (formatType == "model"):
                    depIdList.append(depId)
                #
            #
            if len(depIdList) == 0:
                self.__lfh.write("No deposition ID found in Group Cif file '%s'.\n" % groupCifFile)
                return
            #
            localGroupDirPath = os.path.join(self.__myLocalDirPath,"rcsb_sum_2026/data",groupId)
            if not os.access(localGroupDirPath, os.F_OK):
                os.makedirs(localGroupDirPath)
            #
            for depId in depIdList:
                self.__copyLatestVersionArchiveFile(localGroupDirPath, depId)
            #
        except:
            self.__lfh.write("%s\n" % traceback.format_exc())
        #

    def __getValue(self, catObj, attribute, rowIdx):
        """ Get a value from attributeName='attribute', rowIndex='rowIdx' in catetory object 'catObj'.
        """
        value = ""
        try:
            value = catObj.getValue(attributeName=attribute, rowIndex=rowIdx)
            if (value is None) or (value == ".") or (value == "?"):
                value = ""
            #
            value = value.strip()
        except:
            value = ""
        #
        return value

    def __copyLatestVersionArchiveFile(self, groupDirPath, depId):
        """ Find the lateast version of archive model coordinate file based on input depId and
            copy the file to local group directory.
        """
        depArchiveDirPath = os.path.join(self.__topGroupArchiveDirPath, depId)
        if not os.path.isdir(depArchiveDirPath):
            self.__lfh.write("Archive directory '%s' does not exist.\n" % depArchiveDirPath)
            return
        # 
        baseName = depId + "_model_P1.cif"
        vList = []
        fileList = os.listdir(depArchiveDirPath)
        for fileName in fileList:
            if (not fileName.startswith(baseName)) or fileName.endswith(".gz"):
                continue
            #
            fSp = fileName.split(".V")
            if (len(fSp) < 2) or (not fSp[1].isdigit()):
                continue
            #
            vList.append(int(fSp[1]))
        #
        if len(vList) > 1:
            vList.sort()
        #
        if len(vList) > 0:
            shutil.copyfile(os.path.join(depArchiveDirPath, baseName + ".V" + str(vList[-1])), os.path.join(groupDirPath, depId + ".cif"))
        else:
            self.__lfh.write("No lateast version of archive model coordinate file found for deposition ID '%s'.\n" % depId)
        #

if __name__ == "__main__":
    obj = GetGroupEntryFiles(verbose=True)
    obj.run(sys.argv[1])
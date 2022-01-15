from __future__ import print_function
from dataclasses import field
import jsonpickle
import numpy as np
import _modules.listObject as listObject
from collections import defaultdict

def EM1(sortedSectors: dict) -> dict:
    EM1byFirm = defaultdict(list)
    # get EM1 ratio on firm level for each sector
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            EM1byFirm[sectorID].append(entry.stdEBIT/entry.stdCFO)
    EM1ratios = dict(EM1byFirm)

    # get median on sector level
    EM1bySector = defaultdict(float)
    for sectorID, EM1s in EM1ratios.items():
        EM1bySector[sectorID] = np.median(np.array(EM1s))

    return dict(EM1bySector)

def EM2(sortedSectors: dict) -> dict:
        
    return None

def EM3(sortedSectors: dict) -> dict:

    return None

def EM4(sortedSectors: dict) -> dict:

    return None


def readJSON(JSONfile: str) -> list:
    f = open(JSONfile)
    JSONstring = f.read()
    objList = jsonpickle.decode(JSONstring)
    f.close()
    return objList
    
def sortSectors(objList: list) -> list:
    # sort by sector and store in dict
    secList = defaultdict(list)
    for entry in objList:
        for x in entry.NAICE:
            secList[str(x)[:2]].append(entry)
    
    secList = dict(secList)

    # count sector entrys
    secEntryCount = defaultdict(int)
    for i in list(secList.keys()):
        secEntryCount[i] += len(secList[i])

    return secList, dict(secEntryCount)


if __name__ == '__main__':
    ### TODO get command line arguments for input file
    JSONfile = './_data/python_objects.json'
    objList = readJSON(JSONfile)
    
    # classify entrys by sectors, multiple NAICE entrys result in multiple sector classifications
    sortedSectors, secEntryCount = sortSectors(objList)
    resEM1 = EM1(sortedSectors)
    print(resEM1)
    resEM2 = EM2(sortedSectors)
    resEM3 = EM3(sortedSectors)
    resEM4 = EM4(sortedSectors)
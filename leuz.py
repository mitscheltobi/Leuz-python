from dataclasses import field
import jsonpickle
import numpy as np
import _modules.listObject as listObject
from collections import defaultdict

def EM1(objList: list) -> float:

    return None

def EM2(objList: list) -> float:

    return None

def EM3(objList: list) -> float:

    return None

def EM4(objList: list) -> float:

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
    print(secEntryCount)
    resEM1 = EM1(objList)
    resEM2 = EM2(objList)
    resEM3 = EM3(objList)
    resEM4 = EM4(objList)
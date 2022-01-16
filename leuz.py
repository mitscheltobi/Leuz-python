import re
import jsonpickle
import numpy as np
import _modules.listObject as listObject
from collections import defaultdict
import scipy.stats

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
    EM2bySector = defaultdict(lambda: defaultdict(lambda:np.empty(7)))
    # get company level deltaAccruals & deltaCFOs for each sector & add them together to get sector level timeline
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            EM2bySector[sectorID]['deltaAccrruals'] += np.array(entry.deltaAccruals)
            EM2bySector[sectorID]['deltaCFO'] += np.array(entry.deltaCFO)

    EM2bySector = dict(EM2bySector)

    # calculate spearman correlation using scipy becuase there is no native numpy function
    for sectorID, valueDicts in EM2bySector.items():
        r,p = scipy.stats.pearsonr(valueDicts['deltaAccrruals'], valueDicts['deltaCFO'])
        EM2bySector[sectorID] = r

    return EM2bySector

def EM3(sortedSectors: dict) -> dict:
    # same as EM1 with abs(acc)/abs(CFO)
    EM3byFirm = defaultdict(list)
    # get EM3 ratio on firm level for each sector
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            EM3byFirm[sectorID].append(entry.absAccruals/entry.absCFO)
    EM3ratios = dict(EM3byFirm)

    # get median on sector level
    EM3bySector = defaultdict(float)
    for sectorID, EM1s in EM3ratios.items():
        EM3bySector[sectorID] = np.median(np.array(EM1s))

    return dict(EM3bySector)

def EM4(sortedSectors: dict, percentile: int = 1) -> dict:
    EM4bySector = defaultdict(lambda: defaultdict(lambda: np.empty(0)))
    # iterate through sector profits and losses and add them together
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            EM4bySector[sectorID]['profits'] = np.concatenate((entry.profits, EM4bySector[sectorID]['profits']), axis=None)
            EM4bySector[sectorID]['losses'] = np.concatenate((entry.losses, EM4bySector[sectorID]['losses']), axis=None)
    
    EM4bySector = dict(EM4bySector)
    for sectorID, sectorEarnings in EM4bySector.items():    
        # get sector specific Profit/Loss Threshhold
        sectorProfitThreshhold = np.percentile(sectorEarnings['profits'], percentile)
        sectorLossThreshhold = np.percentile(sectorEarnings['losses'], 100-percentile)
        # calculate sector level EM4
        EM4bySector[sectorID] = len(sectorEarnings['profits'][sectorEarnings['profits'] < sectorProfitThreshhold]) / len(sectorEarnings['losses'][sectorEarnings['losses'] > sectorLossThreshhold])

    return EM4bySector


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
    ### runtime optimization, doing everyting in one loop would be much faster if needed
    JSONfile = './_data/python_objects.json'
    objList = readJSON(JSONfile)
    
    # classify entrys by sectors, multiple NAICE entrys result in multiple sector classifications
    sortedSectors, secEntryCount = sortSectors(objList)
    resEM1 = EM1(sortedSectors)
    resEM2 = EM2(sortedSectors)
    resEM3 = EM3(sortedSectors)
    # using 10% as threshhold for "small" profit and losses; default is 1%
    resEM4 = EM4(sortedSectors, 1)

    results = defaultdict(dict)
    for sectorID, secEntries, em1,em2,em3,em4 in zip(resEM1.keys(), secEntryCount.values(), resEM1.values(), resEM2.values(), resEM3.values(), resEM4.values()):
        results[sectorID] = {
            'EM1': round(em1,3),
            'EM2': round(em2,3),
            'EM3': round(em3,3),
            'EM4': round(em4,3),
            'sampleSize': secEntries
        }
    results = dict(results)
    for i in sorted(list(results.keys())):
        print(f"{i}: {results[i]}")
        
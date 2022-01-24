from datetime import datetime
import jsonpickle, json
import numpy as np
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from collections import defaultdict
import scipy.stats
from argparse import ArgumentParser

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
        EM1sNumpy = np.array(EM1s)
        EM1bySector[sectorID] = np.median(EM1sNumpy[~ np.isnan(EM1sNumpy)])

    return dict(EM1bySector)

def EM2(sortedSectors: dict) -> dict:
    EM2bySector = defaultdict(lambda: defaultdict(lambda:np.empty(2)))
    # get company level deltaAccruals & deltaCFOs for each sector & add them together to get sector level timeline
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            # if company has NaN value in timeline omit company dataset for the calculation
            if not np.isnan(entry.deltaAccruals).any() and not np.isnan(entry.deltaCFO).any():
                EM2bySector[sectorID]['deltaAccrruals'] = np.concatenate((EM2bySector[sectorID]['deltaAccrruals'], np.array(entry.deltaAccruals)), axis=None)
                EM2bySector[sectorID]['deltaCFO'] = np.concatenate((EM2bySector[sectorID]['deltaCFO'], np.array(entry.deltaCFO)),axis=None)
    EM2bySector = dict(EM2bySector)

    # calculate spearman correlation using scipy because there is no native numpy function
    for sectorID, valueDicts in EM2bySector.items():
        try:
            nanArrayDeltaAccruals = np.isnan(valueDicts['deltaAccrruals'])
            nanArrayDeltaCFO = np.isnan(valueDicts['deltaCFO'])

            r,p = scipy.stats.pearsonr(valueDicts['deltaAccrruals'][~ nanArrayDeltaAccruals], valueDicts['deltaCFO'][~ nanArrayDeltaCFO])
            EM2bySector[sectorID] = r
            # print(f"EM2 sector {sectorID}, {valueDicts['deltaAccrruals']}, {valueDicts['deltaCFO']}")
        except ValueError:
            print(f"EM2 Error in sector {sectorID}, {valueDicts['deltaAccrruals']}, {valueDicts['deltaCFO']}")
            EM2bySector[sectorID] = np.nan

    return EM2bySector

def EM3(sortedSectors: dict) -> dict:
    # same as EM1 with abs(acc)/abs(CFO)
    EM3byFirm = defaultdict(list)
    # get EM3 ratio on firm level per year for each sector
    for sectorID, entries in sortedSectors.items():
        for entry in entries:
            EM3byFirm[sectorID].append(entry.absAccruals/entry.absCFO)
    EM3ratios = dict(EM3byFirm)

    # get median of sector level year ratios
    EM3bySector = defaultdict(float)
    for sectorID, EM3s in EM3ratios.items():
        EM3sNumpy = np.array(EM3s)
        EM3bySector[sectorID] = np.median(EM3sNumpy[~ np.isnan(EM3sNumpy)])

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
        # this could cause runtime errors if there are no profits/losses in sample -> IndexError
        # or if there are 0 losses above the threshhold -> ZeroDivisionError
        try:
            sectorProfitThreshhold = np.percentile(sectorEarnings['profits'], percentile)
            sectorLossThreshhold = np.percentile(sectorEarnings['losses'], 100-percentile)
        except:
            print(f"ERROR in EM4 calculation in sector: {entry.NAICE}. This could be due to little/no data in this sector in the dataset. You can drop the sector by not including it in your -s file.")
            raise

        # calculate sector level EM4
        EM4bySector[sectorID] = len(sectorEarnings['profits'][sectorEarnings['profits'] < sectorProfitThreshhold]) / len(sectorEarnings['losses'][sectorEarnings['losses'] > sectorLossThreshhold])
    return EM4bySector


def readJSON(JSONfile: str) -> list:
    f = open(JSONfile)
    JSONstring = f.read()
    data = jsonpickle.decode(JSONstring)
    f.close()
    return data
    
def sortSectors(objList: list, sectors: list) -> list:
    # sort by sector and store in dict
    secList = defaultdict(list)
    for entry in objList:
        for x in entry.NAICE:
            if x in sectors:
                secList[x].append(entry)
    
    secList = dict(secList)

    # count sector entrys
    secEntryCount = defaultdict(int)
    for i in list(secList.keys()):
        secEntryCount[i] += len(secList[i])

    return secList, dict(secEntryCount)

def writeToFile(oFilePath: str, data: list) -> bool:
    try:
        with open(oFilePath, 'w') as ofile:
            ofile.write(json.dumps(data, sort_keys=True, indent=4))
            ofile.close()
        print(f"Successfully written {len(data)} JSON entrys to {oFilePath}.")
        return True
    except:
        return False

def getArgs() -> tuple[str,str,bool]:
    parser = ArgumentParser(description='Calculates EM measures from serialized JSON data.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/company_objects.json', type=str, help="Specify json input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default=f'./_results/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', type=str, help="Specify json output file path. Default: %(default)s")
    parser.add_argument("-s", "--sfile", dest="sFilePath", default='./_data/_misc/sectors_selection.json', type=str, help="Specify json file path to pass a list of sectors to calculate. Default: (all sectors) %(default)s")
    parser.add_argument("-p", dest="em4perc", default=1, type=int, help="Specify percentile denominator for EM4 'small' profits/loss. This has to be an integer. Default: %(default)s")
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], args['sFilePath'], args['em4perc'], args['verbosity'])

if __name__ == '__main__':
    ### TODO:
    ### runtime optimization, doing everyting in one loop would be much faster if needed
    ### verbosity is a mess at the moment and could lead to significantly longer runtimes for big files

    iFile, oFile, sFile, em4perc, verbosity = getArgs()
    if verbosity: bar = statusBar.statusBar(5, 100)
    objList = readJSON(iFile)
    
    try:
        sectors = readJSON(sFile)
    except:
        print("Sector json file not readable. Please have a look at '_data/sectors all.json' for reference.")
        raise

    if verbosity: bar.update(1)
    # classify entrys by sectors, multiple NAICE entrys result in multiple sector classifications
    sortedSectors, secEntryCount = sortSectors(objList, sectors)
    resEM1 = EM1(sortedSectors)
    if verbosity: bar.update(2)
    resEM2 = EM2(sortedSectors)
    if verbosity: bar.update(3)
    resEM3 = EM3(sortedSectors)
    if verbosity: bar.update(4)

    # use supplied percentile denominator for 'small' p/l
    resEM4 = EM4(sortedSectors, em4perc)
    results = defaultdict(dict)

    for sectorID, secEntries, em1,em2,em3,em4 in zip(resEM1.keys(), secEntryCount.values(), resEM1.values(), resEM2.values(), resEM3.values(), resEM4.values()):
        if sectorID in sectors:
            results[sectorID] = {
                'EM1': round(em1, 3),
                'EM2': round(em2, 3),
                'EM3': round(em3, 3),
                'EM4': round(em4, 3),
                'sampleSize': secEntries
            }
    
    results = dict(results)
    if verbosity:
        bar.update(5)
        print("\nDone calculating. Results:")
        for i in list(results.keys()):
            print(f"{i}: {results[i]}")
    
    if not writeToFile(oFile, results):
        print('Error while writing to file.')
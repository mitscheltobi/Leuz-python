from unicodedata import category
import jsonpickle, json
import numpy as np
from collections import defaultdict
from argparse import ArgumentParser

def getArgs() -> tuple[str,str,bool]:
    parser = ArgumentParser(description='Count valid firm year observations of dataset.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/company_objects.json', type=str, help="Specify json input file path. Default: %(default)s")
    parser.add_argument("-s", "--sfile", dest="sFilePath", default='./_data/_misc/sectors_selection.json', type=str, help="Specify json file path to pass a list of sectors to calculate. Default: (selected sectors) %(default)s")
    args = vars(parser.parse_args())
    return (args['iFilePath'],args['sFilePath'])

def sortSectors(objList: list, sectors: list) -> list:
    # sort by sector and store in dict
    secList = defaultdict(list)
    for entry in objList:
        for x in entry.NAICE:
            if x in sectors:
                secList[x].append(entry)
    return dict(secList)

def totSampleSize(secList):
    # count sector entrys
    secEntryCount = defaultdict(lambda: defaultdict(int))
    for i in list(secList.keys()):
        for entry in secList[i]:
            categories = ['EBIT', 'NetIncome','totAssets','totCurAssets','cash','totLiabilities','curLiabilities','shortTermDebt','taxPayable','Depreciation']
            for cat in categories:
                for yearIdx in range(len(entry.EBIT)):
                    if not np.isnan(entry.EBIT[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.NetIncome[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.totAssets[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.totCurAssets[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.cash[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.totLiabilities[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.curLiabilities[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.shortTermDebt[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.taxPayable[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
                    if not np.isnan(entry.Depreciation[yearIdx]):
                        secEntryCount[i][yearIdx] += 1
    return dict(secEntryCount)

def readJSON(JSONfile: str) -> dict:
    f = open(JSONfile)
    JSONstring = f.read()
    data = jsonpickle.decode(JSONstring)
    f.close()
    return data

if __name__ == '__main__':
    ifile, sfile = getArgs()
    JSONblob = readJSON(ifile)
    sectors = readJSON(sfile)
    sortedSectors = sortSectors(JSONblob, sectors)
    # Jahresbeobachtungen
    secEntryCount = totSampleSize(sortedSectors)
    for key in secEntryCount.keys():
        print(key, dict(secEntryCount[key]))
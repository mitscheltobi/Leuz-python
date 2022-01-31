from cmath import isnan
from collections import defaultdict
import _modules.listObject_hyp_1 as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
import numpy as np
import json
from pandas import read_excel, DataFrame
from datetime import datetime
from os import system

class FileTypeError(Exception):
    pass

def yieldObject(rowData: DataFrame, years: list[int, int], numDropped: int) -> listObject.entry:
    naicsClasses = {'na': 'No Category','11': 'Agriculture, Forestry, Fishing and Hunting','21': 'Mining, Quarrying, and Oil and Gas Extraction','22': 'Utilities','23': 'Construction','31': 'Manufacturing','32': 'Manufacturing','33': 'Manufacturing','42': 'Wholesale Trade','44': 'Retail Trade','45': 'Retail Trade','48': 'Transportation and Warehousing','49': 'Transportation and Warehousing','51': 'Information','52': 'Finance and Insurance','53': 'Real Estate and Rental and Leasing','54': 'Professional, Scientific, and Technical Services','55': 'Management of Companies and Enterprises','56': 'Administrative and Support and Waste Management and Remediation Services','61': 'Educational Services','62': 'Health Care and Social Assistance','71': 'Arts, Entertainment, and Recreation','72': 'Accommodation and Food Services','81': 'Other Services (except Public Administration)','92': 'Public Administration'}

    # Metadata
    id = int(rowData[0])
    name = rowData['Company name Latin alphabet']
    try:
        # case one classification
        naice = [naicsClasses[str(rowData['NAICS 2017, primary code(s)'])[:2]]]
    except ValueError:
        # case more than one classification
        naice = [naicsClasses[x[:2]] for x in rowData['NAICS 2017, primary code(s)'].split("; ")]

    # data columns conversion to numbers
    def refData(rowData, timeframe, headers):
        dataCategories = defaultdict(list)
        for dataCategory in headers:
            years = rowData[str(dataCategory + str(timeframe[0])) : str(dataCategory + str(timeframe[1]))]
            try:
                dataCategories[dataCategory]=[float(yearval) for yearval in years]
            except ValueError:
                # function for catching errors in list comprehension; error means nan value in data
                def catch(convert, *args, **kwargs):
                    try:
                        return convert(*args, **kwargs)
                    except Exception:
                        return None

                dataCategories[dataCategory]=[res if (res:=catch(lambda: float(yearval))) else np.nan for yearval in years]
        return dataCategories
    
    headers = ['Sales\nth USD ', 'Total assets\nth USD ']
    if (res:= refData(rowData[3:], years, headers)):
        sales = res['Sales\nth USD ']
        totAssets = res['Total assets\nth USD ']
        # You need to check the Object under ./_modules/listObject.py to see how the other KPIs are calculated as they are calculated on company level upon calling the object constructor method like below
        itm = listObject.entry(ID=id, name=name, NAICE=naice, totAssets=totAssets, sales=sales)
        return itm
    else:
        numDropped += 1
        return numDropped

def readFile(iFilePath: str, years: int, bar: statusBar.statusBar = None) -> list:
    objlst= []
    numDropped = 0
    if bar: iter = 0

    if iFilePath[-4:].lower() == "xlsx":
        # read xlsx years, generate python object and add to list
        wb = read_excel(iFilePath, sheet_name=1, engine='openpyxl')
        for row in wb.iloc:
            if type(res := yieldObject(row, years, numDropped)) != int:
                objlst.append(res)
            else:
                numDropped+=1
            if bar: iter += 1
            bar.update(iter)
        print(f"\nLoading data complete. Dropped {numDropped} entrys because of faulty data. Writing to file...")
        return objlst
    else:
        raise FileTypeError("Filetype supplied is not supported. Please use .xlsx files only.")

def getIterCount(iFilePath: str) -> int:
    if iFilePath[-4:].lower() == "xlsx":
        try:
            return len(read_excel(iFilePath, sheet_name=1, engine='openpyxl',na_values=['n.a.']))
        except ValueError:
            raise FileTypeError("The file you supplied does not appear to have two sheets. Please make sure your years is on the second sheet in the .xlsx file.")
    else:
        raise FileTypeError("Filetype supplied is not supported. Please use .xlsx files only.")

def saveAsJSON(data, path):
    with open(path, "w") as file:
        file.write(json.dumps(data, sort_keys=True, indent=4))
    return True

def readJSON(JSONfile: str) -> dict:
    with open(JSONfile) as f:
        JSONstring = f.read()
        data = json.loads(JSONstring)
        f.close()
    return data

def getArgs():
    # handles commandline args call -h for help
    parser = ArgumentParser(description='Loads xlsx Orbis report and converts it to JSON serialized python objects.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_nebenrechnungen/_data/_orbisRaw/Export default.xlsx', type=str, help="Specify xlsx input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default=f'./_nebenrechnungen/_results/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', type=str, help="Specify josn output file path. Default: %(default)s")
    parser.add_argument("-s", "--sfile", dest="sFilePath", default='./_data/_misc/sectors_selection.json', type=str, help="Specify json file path to pass a list of sectors to calculate. Default: (selected sectors) %(default)s")
    parser.add_argument("-ly", "--lastyear", dest="last_year", default=2021, type=int, help="Specify last year in dataset. Default: %(default)s")
    parser.add_argument("-fy", "--firstyears", dest="first_year", default=2012, type=int, help="Specify first year in dataset. Default: %(default)s")
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], args['sFilePath'], [args['last_year'], args['first_year']], args['verbosity'])

def sortSectors(objList: list, sectors: list) -> list:
    # sort by sector and store in dict
    secList = defaultdict(list)
    for entry in objList:
        for x in entry.NAICE:
            if x in sectors:
                secList[x].append(entry)
    
    secList = dict(secList)
    return secList

def getVolBySector(sectorData):
    SectorSTDs = defaultdict(list)
    for sectorID, entries in sectorData.items():
        for entry in entries:
            if not np.isnan(entry.salesScaled).any():
                SectorSTDs[sectorID].append(np.std(entry.salesScaled))
    
    VOL = defaultdict(float)
    for sectorID, stds in SectorSTDs.items():
        VOL[sectorID] = round(np.nanmedian(stds), 3)

    return dict(VOL)

if __name__ == '__main__':
    # if you are trying to find out how Accruals, CFO etc. are calculated please have a look at .\_modules\listObject.py as the calculations are done when calling the constructor method of the object
    # fetch commandline args
    iFilePath, oFilePath, sFilePath, years, verbosity = getArgs()

    # read from file & parse years
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years)

    sectors = readJSON(sFilePath)
    sectorData = sortSectors(returnedObjects, sectors)
    volatility = getVolBySector(sectorData)
    
    # save to file
    if saveAsJSON(volatility, oFilePath):
        print("__DONE__")

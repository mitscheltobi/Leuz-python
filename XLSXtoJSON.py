from collections import defaultdict
from email import header
import jsonpickle
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
from collections.abc import Generator
import numpy as np
from pandas import read_excel, DataFrame
from datetime import datetime
from os import system

class FileTypeError(Exception):
            pass

def yieldObject(rowData: DataFrame, years: list[int, int], numDropped: int, NaN: str) -> listObject.entry:
    # This is so ugly I wanna be blind
    naicsClasses = {'na': 'No Category','11': 'Agriculture, Forestry, Fishing and Hunting','21': 'Mining, Quarrying, and Oil and Gas Extraction','22': 'Utilities','23': 'Construction','31': 'Manufacturing','32': 'Manufacturing','33': 'Manufacturing','42': 'Wholesale Trade','44': 'Retail Trade','45': 'Retail Trade','48': 'Transportation and Warehousing','49': 'Transportation and Warehousing','51': 'Information','52': 'Finance and Insurance','53': 'Real Estate and Rental and Leasing','54': 'Professional, Scientific, and Technical Services','55': 'Management of Companies and Enterprises','56': 'Administrative and Support and Waste Management and Remediation Services','61': 'Educational Services','62': 'Health Care and Social Assistance','71': 'Arts, Entertainment, and Recreation','72': 'Accommodation and Food Services','81': 'Other Services (except Public Administration)','92': 'Public Administration'}

    id = int(rowData[0])
    name = rowData['Company name Latin alphabet']
    try:
        # case one classification
        naice = [naicsClasses[str(rowData['NAICS 2017, primary code(s)'])[:2]]]
    except ValueError:
        # case more than one classification
        naice = [naicsClasses[x[:2]] for x in rowData['NAICS 2017, primary code(s)'].split("; ")]

    def refData(rowData, timeframe, NaN, headers):
        dataCategories = defaultdict(list)
        for dataCategory in headers:
            years = rowData[str(dataCategory + str(timeframe[0])) : str(dataCategory + str(timeframe[1]))]
            try:
                dataCategories[dataCategory]=[float(year) for year in years]
            except ValueError:
                # function for catching errors in list comprehension
                def catch(convert, *args, **kwargs):
                    try:
                        return convert(*args, **kwargs)
                    except Exception:
                        return None

                match NaN:
                    case 'accept':
                        dataCategories[dataCategory]=[res if (res:=catch(lambda: float(year))) else np.nan for year in years]
                    case 'convert':
                        if dataCategory != 'Income Tax Payable\nth USD ':
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(year))) else np.nan for year in years]
                        else:
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(year))) else 0.00 for year in years]
                    case 'perpetuate':
                        if dataCategory != 'Income Tax Payable\nth USD ':
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(year))) else np.nan for year in years]
                        else:
                            # could be faster
                            def findNextVal(list):
                                for x in list:
                                    try:
                                        return float(x)
                                    except ValueError:
                                        continue
                                return np.nan
                            dataCategories[dataCategory]=[res if (res := catch(lambda: float(years[year]))) else findNextVal(years[year:]) for year in range(len(years))]
                    case _:
                        # drop entire row
                        return None
        return dataCategories
    
    headers = ['Operating P/L [=EBIT]\nth USD ', 'P/L for period [=Net income]\nth USD ', 'Total assets\nth USD ', 'Cash & cash equivalent\nth USD ', 'Total Liabilities and Debt\nth USD ', 'Total Current Liabilities\nth USD ', 'Income Tax Payable\nth USD ', 'Depreciation\nth USD ']
    if (res:= refData(rowData[3:], years, NaN, headers)):
        ebit = res[headers[0]]
        NetInc = res[headers[1]]
        totAssets = res[headers[2]]
        cash = res[headers[3]]
        totLiabilities = res[headers[4]]
        curLiabilities = res[headers[5]]
        taxPayable = res[headers[6]]
        Depreciation = res[headers[7]]
        itm = listObject.entry(id, name, naice, ebit, NetInc, totAssets, cash, totLiabilities, curLiabilities, taxPayable, Depreciation)
        return itm
    else:
        numDropped += 1
        return numDropped

def readFile(iFilePath: str, years: int, NaN: str, bar: statusBar.statusBar = None) -> list:
    objlst= []
    numDropped = 0
    if bar: iter = 0

    if iFilePath[-4:].lower() == "xlsx":
        # read xlsx years, generate python object and add to list
        wb = read_excel(iFilePath, sheet_name=1, engine='openpyxl')
        for row in wb.iloc:
            if type(res := yieldObject(row, years, numDropped, NaN)) != int:
                objlst.append(res)
            else:
                numDropped+=1
            iter += 1
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

def writeToFile(oFilePath: str, years: list) -> bool:
    try:
        # write objects to json file
        with open(oFilePath, 'w') as ofile:
            ofile.write(jsonpickle.encode(years, unpicklable=True))
            ofile.close()
        print(f"Successfully written {len(years)} JSON entrys to {oFilePath}.")
        return True
    except:
        return False

def getArgs():
    parser = ArgumentParser(description='Loads xlsx Orbis report and converts it to JSON serialized python objects.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/_orbisRaw/Export default.xlsx', type=str, help="Specify xlsx input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default=f'./_data/_pythonObjects/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', type=str, help="Specify json output file path. Default: %(default)s")
    parser.add_argument("-ly", "--lastyear", dest="last_year", default=2021, type=int, help="Specify last year in dataset. Default: %(default)s")
    parser.add_argument("-fy", "--firstyears", dest="first_year", default=2012, type=int, help="Specify first year in dataset. Default: %(default)s")
    parser.add_argument("-nan", dest="NaN", choices=['drop', 'accept', 'convert', 'perpetuate'], default='dropNaNdata', help="""
Determines what to do with NaN values in years.

Choices:
    drop: Don't accept firm-year observations of NaN in dataset. Drops all firm datasets which contain NaN values.
    accept: Accept firm-year observations of NaN in dataset. NaN values will lower the quality of the EM computation.
    convert: Convert NaN values in 'taxPayable' only to 0. Other NaN values will be accepted.
    perpetuate: Assume NaN values in 'taxPayable' only to be equal to any previous year with years. Other NaN values will be accepted.
    Default: %(default)s
    """)
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    parser.add_argument("-c", "--calc", dest="calc", default=False, action='store_true', help="(flag) Automatically calls leuz.py after execution to calculate measures from generated data.")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], [args['last_year'], args['first_year']], args['NaN'], args['calc'], args['verbosity'])

if __name__ == '__main__':
    # fetch commandrowData args
    iFilePath, oFilePath, years, NaN, calc, verbosity = getArgs()

    # read from file & parse years
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years,NaN=NaN, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years, NaN=NaN)
    
    # write to file
    if not writeToFile(oFilePath=oFilePath, years=returnedObjects):
        print("Error while writing to specified file!")

    if calc:
        system(f"python ./leuz.py -i {oFilePath} -v")
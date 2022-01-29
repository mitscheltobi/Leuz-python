from collections import defaultdict
import jsonpickle
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
import numpy as np
from pandas import read_excel, DataFrame
from datetime import datetime
from os import system

class FileTypeError(Exception):
    pass

def yieldObject(rowData: DataFrame, years: list[int, int], numDropped: int, NaN: str) -> listObject.entry:
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
    def refData(rowData, timeframe, NaN, headers):
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

                match NaN:
                    case 'accept':
                        dataCategories[dataCategory]=[res if (res:=catch(lambda: float(yearval))) else np.nan for yearval in years]
                    case 'convert':
                        if dataCategory not in ['Income Tax Payable\nth USD ', 'Other Short Term Debt\nth USD ']:
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(yearval))) else np.nan for yearval in years]
                        else:
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(yearval))) else 0.00 for yearval in years]
                    case 'perpetuate':
                        if dataCategory not in ['Income Tax Payable\nth USD ', 'Other Short Term Debt\nth USD ']:
                            dataCategories[dataCategory]=[res if (res:=catch(lambda: float(yearval))) else np.nan for yearval in years]
                        else:
                            # could be faster
                            def findNextVal(list, year):
                                # first try to look for a value in previous years
                                for x in list[year:]:
                                    try:
                                        return float(x)
                                    except ValueError:
                                        continue
                                # if there is no previous year with dara try to look for a value in future years
                                for x in list[:year][::-1]:
                                    try:
                                        return float(x)
                                    except ValueError:
                                        continue
                                # if the entire timeline has no data return 0.00
                                return 0.00
                            dataCategories[dataCategory]=[res if (res := catch(lambda: float(years[year]))) else findNextVal(years, year) for year in range(len(years))]
                    case _:
                        # drop entire row
                        return None
        return dataCategories
    
    headers = ['Operating P/L [=EBIT]\nth USD ','P/L for period [=Net income]\nth USD ','Total assets\nth USD ','Total Current Assets\nth USD ','Cash & cash equivalent\nth USD ','Total Liabilities and Debt\nth USD ','Total Current Liabilities\nth USD ','Other Short Term Debt\nth USD ','Income Tax Payable\nth USD ','Depreciation & Amortization\nth USD ']
    if (res:= refData(rowData[3:], years, NaN, headers)):
        ebit = res['Operating P/L [=EBIT]\nth USD ']
        NetInc = res['P/L for period [=Net income]\nth USD ']
        totAssets = res['Total assets\nth USD ']
        currAssets = res['Total Current Assets\nth USD ']
        cash = res['Cash & cash equivalent\nth USD ']
        totLiabilities = res['Total Liabilities and Debt\nth USD ']
        curLiabilities = res['Total Current Liabilities\nth USD ']
        shortTermDebt = res['Other Short Term Debt\nth USD ']
        taxPayable = res['Income Tax Payable\nth USD ']
        Depreciation = res['Depreciation & Amortization\nth USD ']
        # You need to check the Object under ./_modules/listObject.py to see how the other KPIs are calculated as they are calculated on company level upon calling the object constructor method like below
        itm = listObject.entry(ID=id, name=name, NAICE=naice, EBIT=ebit, NetIncome=NetInc, totAssets=totAssets, totCurAssets=currAssets, cash=cash, totLiabilities=totLiabilities, curLiabilities=curLiabilities, shortTermDebt=shortTermDebt, taxPayable=taxPayable, Depreciation=Depreciation)
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
    # handles commandline args call -h for help
    parser = ArgumentParser(description='Loads xlsx Orbis report and converts it to JSON serialized python objects.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/_orbisRaw/Export default.xlsx', type=str, help="Specify xlsx input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default=f'./_data/_pythonObjects/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', type=str, help="Specify json output file path. Default: %(default)s")
    parser.add_argument("-ly", "--lastyear", dest="last_year", default=2021, type=int, help="Specify last year in dataset. Default: %(default)s")
    parser.add_argument("-fy", "--firstyears", dest="first_year", default=2012, type=int, help="Specify first year in dataset. Default: %(default)s")
    parser.add_argument("-nan", dest="NaN", choices=['drop', 'accept', 'convert', 'perpetuate'], default='dropNaNdata', help="""
Determines what to do with NaN values in years.

Choices:
    drop: Don't accept firm-year observations of NaN in dataset. Drops all firm datasets which contain NaN values.
    accept: Accept firm-year observations of NaN in dataset. NaN values will lower the quality of the EM computation (=reduced sample size where NaN makes calculation impossible).
    convert: Convert NaN values in 'taxPayable' & 'currentLiabilities' only to 0. Other NaN values will be accepted.
    perpetuate: Assume NaN values in 'taxPayable' & 'currentLiabilities' only to be equal to any previous/future year with data. Other NaN values will be accepted.
    Default: %(default)s
    """)
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    parser.add_argument("-c", "--calc", dest="calc", default=False, const='all', nargs='?', help="(flag) Automatically calls leuz.py after execution to calculate measures from generated data. You can pass 'all', '1', '2', '3', '4', '23' to specify which EM measure to calculate. Check leuz.py -h for more information. Default: 'all'")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], [args['last_year'], args['first_year']], args['NaN'], args['calc'], args['verbosity'])

if __name__ == '__main__':
    # if you are trying to find out how Accruals, CFO etc. are calculated please have a look at .\_modules\listObject.py as the calculations are done when calling the constructor method of the object
    # fetch commandline args
    iFilePath, oFilePath, years, NaN, calc, verbosity = getArgs()

    # read from file & parse years
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years,NaN=NaN, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years, NaN=NaN)
    
    # try to write to file
    if not writeToFile(oFilePath=oFilePath, years=returnedObjects):
        print("Error while writing to specified file!")

    # if -c is passed execute leuz.py with file generated by this script as input and pass whatever was passed to -c to -em
    if calc:
        system(f"python ./leuz.py -i {oFilePath} -v -em {calc}")
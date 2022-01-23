import csv
import jsonpickle
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
from collections.abc import Generator
import numpy as np
import openpyxl as pyxl
from pandas import read_excel

class FileTypeError(Exception):
            pass

def yieldObject(reader: csv.DictReader, years: int, numDropped: int, NaN: str) -> Generator[listObject.entry]:
    naicsClasses = {
                    '11': 'Agriculture, Forestry, Fishing and Hunting',
                    '21': 'Mining, Quarrying, and Oil and Gas Extraction',
                    '22': 'Utilities',
                    '23': 'Construction',
                    '31': 'Manufacturing',
                    '32': 'Manufacturing',
                    '33': 'Manufacturing',
                    '42': 'Wholesale Trade',
                    '44': 'Retail Trade',
                    '45': 'Retail Trade',
                    '48': 'Transportation and Warehousing',
                    '49': 'Transportation and Warehousing',
                    '51': 'Information',
                    '52': 'Finance and Insurance',
                    '53': 'Real Estate and Rental and Leasing',
                    '54': 'Professional, Scientific, and Technical Services',
                    '55': 'Management of Companies and Enterprises',
                    '56': 'Administrative and Support and Waste Management and Remediation Services',
                    '61': 'Educational Services',
                    '62': 'Health Care and Social Assistance',
                    '71': 'Arts, Entertainment, and Recreation',
                    '72': 'Accommodation and Food Services',
                    '81': 'Other Services (except Public Administration)',
                    '92': 'Public Administration'
                }
    
    # assumes fixed data length and positions
    for line in reader:
        if line[0] != "ID":
            # __metadata__
            id = int(line[0])
            name = line[1]
            try:
                # case one classification
                naice = [naicsClasses[line[2][:2]]]
            except ValueError:
                # case more than one classification
                naice = [naicsClasses[x[:2]] for x in line[2].split("; ")]

            def refData(line):
                dataCategories = []
                for i in range(8):
                    dataCategory = line[3+years*i:3+years*(i+1)]
                    try:
                        dataCategories.append([float(x) for x in dataCategory])
                    except ValueError:
                        # function for catching errors in list comprehension
                        def catch(convert, *args, **kwargs):
                            try:
                                return convert(*args, **kwargs)
                            except Exception:
                                return None

                        match NaN:
                            case 'accept':
                                dataCategories.append([res if (res:=catch(lambda: float(x))) else np.nan for x in dataCategory])
                            case 'convert':
                                if i != 6:
                                    dataCategories.append([res if (res:=catch(lambda: float(x))) else np.nan for x in dataCategory])
                                else:
                                    dataCategories.append([res if (res:=catch(lambda: float(x))) else 0.00 for x in dataCategory])
                            case 'perpetuate':
                                if i != 6:
                                    dataCategories.append([res if (res:=catch(lambda: float(x))) else np.nan for x in dataCategory])
                                else:
                                    # could be faster
                                    def findNextVal(list):
                                        for x in list:
                                            try:
                                                return float(x)
                                            except ValueError:
                                                continue
                                        return np.nan
                                    dataCategories.append([res if (res := catch(lambda: float(dataCategory[x]))) else findNextVal(dataCategory[x:]) for x in range(len(dataCategory))])
                            case _:
                                # drop entire row
                                return None
                return dataCategories

                    # for itmIndx in range(len(dataCategory)):
                    #     try:
                    #         # try to convert number in field to float
                    #         numbers.append(float(dataCategory[itmIndx]))
                    #     except ValueError:
                    #         # NaN value conversion depending on what NaN logic was supplied
                    #         match NaN:
                    #             case 'accept':
                    #                 numbers.append(np.nan)
                    #             case 'convert':
                    #                 if i == 6:
                    #                     # everything in taxPayable will be converted to 0
                    #                     numbers.append(0.00)
                    #                 else:
                    #                     numbers.append(np.nan)
                    #             case 'perpetuate':
                    #                 if i == 6:
                    #                     def findNextVal(list):
                    #                         for x in list:
                    #                             try:
                    #                                 return float(x)
                    #                             except ValueError:
                    #                                 continue
                    #                         return None
                                        
                    #                 else:
                    #                     numbers.append(np.nan)
                    #             case _:
                    #                 return None

                #     oput.append(numbers)
                # return oput
            
            if (data:= refData(line)):
                ebit = data[0]
                NetInc = data[1]
                totAssets = data[2]
                cash = data[3]
                totLiabilities = data[4]
                curLiabilities =data[5]
                taxPayable = data[6]
                Depreciation = data[7]
                itm = listObject.entry(id, name, naice, ebit, NetInc, totAssets, cash, totLiabilities, curLiabilities, taxPayable, Depreciation)
                yield itm
            else:
                numDropped += 1
                yield numDropped
        else: pass


def readFile(iFilePath: str, years: int, NaN: str, bar: statusBar.statusBar = None) -> list:
    objlst= []
    numDropped = 0
    if bar: iter = 0

    if iFilePath[-3:].lower() == "csv":
        # read csv data, generate python object and add to list
        with open(iFilePath, newline='') as csvfile:
            readerObj = csv.reader(csvfile, delimiter=',', quotechar='|')
            gen = yieldObject(readerObj, years, numDropped, NaN)
            while True:
                try:
                    ret = next(gen)
                    if type(ret) is not int:
                        objlst.append(ret)
                    else:
                        numDropped = ret
                    
                    if bar:
                        iter += 1
                        bar.update(iter)
                except StopIteration:
                    # generator yields nothing; end of list
                    print(f"\nLoading data complete. Dropped {numDropped} entrys because of faulty data. Writing to file...")
                    break
            csvfile.close()
        return objlst
    elif iFilePath[-4:].lower() == "xlsx":
        # read xlsx data, generate python object and add to list
        wb = read_excel(iFilePath, sheet_name=1, engine='openpyxl',na_values=['n.a.'])
        for row in wb.iloc:
            print(row)
            break
    else:
        raise FileTypeError("Filetype supplied is not supported. Please use .csv or .xlsx files only.")

def getIterCount(iFilePath: str) -> int:
    # TODO itercount for xlsx
    if iFilePath[-3:].lower() == "csv":
        with open(iFilePath, newline='') as csvfile:
            readerObj = csv.reader(csvfile, delimiter=',', quotechar='|')
            i = sum(1 for _ in readerObj)
            csvfile.close()
        return i
    elif iFilePath[-4:].lower() == "xlsx":
        try:
            return len(read_excel(iFilePath, sheet_name=1, engine='openpyxl',na_values=['n.a.']))
        except ValueError:
            raise FileTypeError("The file you supplied does not appear to have two sheets. Please make sure your data is on the second sheet in the .xlsx file.")
    else:
        raise FileTypeError("Filetype supplied is not supported. Please use .csv or .xlsx files only.")

def writeToFile(oFilePath: str, data: list) -> bool:
    try:
        # write objects to json file
        with open(oFilePath, 'w') as ofile:
            ofile.write(jsonpickle.encode(data, unpicklable=True))
            ofile.close()
        print(f"Successfully written {len(data)} JSON entrys to {oFilePath}.")
        return True
    except:
        return False

def getArgs() -> tuple[str, str, int, bool, bool]:
    parser = ArgumentParser(description='Parses csv data and converts it to JSON serialized python objects.')
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/data.csv', type=str, help="Specify csv input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default='./_data/python_objects.json', type=str, help="Specify json output file path. Default: %(default)s")
    parser.add_argument("-y", "--years", dest="years", default=10, type=int, help="Specify number of columns of each data category in csv file. Default: %(default)s")
    parser.add_argument("-nan", dest="NaN", choices=['drop', 'accept', 'convert', 'perpetuate'], default='dropNaNdata', help="""
Determines what to do with NaN values in data.

Choices:
    drop: Don't accept firm-year observations of NaN in dataset. Drops all firm datasets which contain NaN values.
    accept: Accept firm-year observations of NaN in dataset. NaN values will lower the quality of the EM computation.
    convert: Convert NaN values in 'taxPayable' only to 0. Other NaN values will be accepted.
    perpetuate: Assume NaN values in 'taxPayable' only to be equal to any previous year with data. Other NaN values will be accepted.
    Default: %(default)s
    """)
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], args['years'], args['NaN'], args['verbosity'])

if __name__ == '__main__':
    # fetch commandline args
    iFilePath, oFilePath, years, NaN, verbosity = getArgs()

    # read from file & parse data
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years,NaN=NaN, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years, NaN=NaN)
    
    # write to file
    if not writeToFile(oFilePath=oFilePath, data=returnedObjects):
        print("Error while writing to specified file!")
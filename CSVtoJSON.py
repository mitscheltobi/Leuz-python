import csv
import jsonpickle
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
from collections.abc import Generator
import numpy as np

def yieldObject(reader: csv.DictReader, years: int, numDropped: int, convertNaNToZero: bool = False, acceptNaNvals: bool = True) -> Generator[listObject.entry]:
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
                oput = []
                for i in range(8):
                    # leaves 2021 out; timeline from 2012-2020
                    dat = line[4+years*i:3+years*(i+1)]
                    numbers = []
                    for itm in dat:
                        try:
                            # try to convert number in field to float
                            numbers.append(float(itm))
                        except ValueError:
                            if acceptNaNvals:
                                numbers.append(np.nan)
                            elif convertNaNToZero:
                                if i == 6:
                                    numbers.append(0.00)
                                else:
                                    return None
                            else:
                                return None

                    oput.append(numbers)
                return oput
            
            data = refData(line)
            if data:
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


def readFile(iFilePath: str, years: int, convertNaNToZero: bool = False, acceptNaNvals: bool = True, bar: statusBar.statusBar = None) -> list:
    objlst= []
    numDropped = 0
    if bar: iter = 0
    # read csv data, generate python object and add to list
    with open(iFilePath, newline='') as csvfile:
        readerObj = csv.reader(csvfile, delimiter=',', quotechar='|')
        gen = yieldObject(readerObj, years, numDropped, convertNaNToZero, acceptNaNvals)
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

def getIterCount(iFilePath: str) -> int:
    with open(iFilePath, newline='') as csvfile:
        readerObj = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = sum(1 for _ in readerObj)
        csvfile.close()
    return i

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
    parser.add_argument("-n", dest="acceptNaN", default=False, action='store_false', help="(flag) Accept firm-year observations of NaN in dataset. If not set every firm with a firm-year observation of NaN will be completely excluded from any computations.")
    parser.add_argument("-c", dest="convertNaNToZero", default=False, action='store_true', help="(flag) Convert NaN values in 'taxPayable' to 0. Only has an effect if -n is not set simultaneously.")
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="(flag) Verbosity level")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], args['years'], args['convertNaNToZero'], args['acceptNaN'], args['verbosity'])

if __name__ == '__main__':
    # fetch commandline args
    iFilePath, oFilePath, years, convertNaNToZero, acceptNaNvals, verbosity = getArgs()

    # read from file & parse data
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years, convertNaNToZero=convertNaNToZero, acceptNaNvals=acceptNaNvals, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years, convertNaNToZero=convertNaNToZero)
    
    # write to file
    if not writeToFile(oFilePath=oFilePath, data=returnedObjects):
        print("Error while writing to specified file!")
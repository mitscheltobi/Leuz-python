import csv
import jsonpickle
import _modules.listObject as listObject
import _modules.statusBar as statusBar
from argparse import ArgumentParser
from collections.abc import Generator

def yieldObject(reader: csv.DictReader, years: int, numDropped: int, convertNaNToZero: bool = False) -> Generator[listObject.entry]:
    # assumes fixed data length and positions
    for line in reader:
        if line[0] != "ID":
            # __metadata__
            id = int(line[0])
            name = line[1]
            try:
                # case one classification
                naice = [int(line[2])]
            except ValueError:
                # case more than one classification
                naice = [int(x) for x in line[2].split("; ")]

            # look trough data for n.a. and wrap in list
            def refData(line):
                oput = []
                for i in range(8):
                    # leaves 2021 out; timeline from 2012-2020
                    dat = line[4+years*i:3+years*(i+1)]
                    numbers = []
                    for itm in dat:
                        try:
                            # try to convert field to int
                            numbers.append(float(itm))
                        except ValueError:
                            if convertNaNToZero:
                                if i == 6:
                                    numbers.append(0.00)
                                else:
                                    #if not tax payable and not convertible drop entire row
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


def readFile(iFilePath: str, years: int, convertNaNToZero: bool = False, bar: statusBar.statusBar = None) -> list:
    objlst= []
    numDropped = 0
    if bar: iter = 0
    # read csv data, generate python object and add to list
    with open(iFilePath, newline='') as csvfile:
        readerObj = csv.reader(csvfile, delimiter=',', quotechar='|')
        gen = yieldObject(readerObj, years, numDropped, convertNaNToZero)
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
    parser.add_argument("-i", "--ifile", dest="iFilePath", default='./_data/data.csv', type=str, help="specify csv input file path. Default: %(default)s")
    parser.add_argument("-o", "--ofile", dest="oFilePath", default='./_data/python_objects.json', type=str, help="specify json output file path. Default: %(default)s")
    parser.add_argument("-y", "--years", dest="years", default=10, type=int, help="specify number of columns of each data category in csv file. Default: %(default)s")
    parser.add_argument("-c", dest="convertNaNToZero", default=False, action='store_true', help="convert N/A values in 'taxPayable' to 0 (flag)")
    parser.add_argument("-v", dest="verbosity", default=False, action='store_true', help="verbosity level (flag)")
    args = vars(parser.parse_args())
    return (args['iFilePath'], args['oFilePath'], args['years'], args['convertNaNToZero'], args['verbosity'])

if __name__ == '__main__':
    # fetch commandline args
    iFilePath, oFilePath, years, convertNaNToZero, verbosity = getArgs()

    # read from file & parse data
    if verbosity:
        i = getIterCount(iFilePath)
        lbar = statusBar.statusBar(i, size=100)
        returnedObjects = readFile(iFilePath=iFilePath, years=years, convertNaNToZero=convertNaNToZero, bar=lbar)
    else:
        returnedObjects = readFile(iFilePath=iFilePath, years=years, convertNaNToZero=convertNaNToZero)
    
    # write to file
    if not writeToFile(oFilePath=oFilePath, data=returnedObjects):
        print("Error while writing to specified file!")
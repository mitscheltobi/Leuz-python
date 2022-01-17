import csv
import jsonpickle
import _modules.listObject as listObject

def yieldObject(reader: csv.DictReader, years: int, numDropped: int, convertNaNToZero: bool = False) -> listObject.entry:
    # assumes fixed data length and positions
    for line in reader:
        if line[0] != "ID":
            # metadata
            id = int(line[0][:-1])
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
                            #try to convert field to int
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

def readFile(iFilePath: str, years: int, convertNaNToZero: Boolean = False) -> list:
    objlst= []
    numDropped = 0
    #read csv data, generate python object and add to list
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
            except StopIteration:
                # generator yields nothing == end of list
                break
    print(f"Dropped {numDropped} entrys because of faulty data...")
    return objlst

def writeToFile(oFilePath: str, data: list) -> bool:
    try:
        # write objects to json file
        with open(oFilePath, 'w') as ofile:
            ofile.write(jsonpickle.encode(data, unpicklable=True))
            ofile.close()

        print(f"Successfully saved {len(data)} entrys as JSON...")
        return True
    except:
        return False

if __name__ == '__main__':
    ### TODO get command line args for input, output, specified years, verbosity
    years = 10
    returnedObjects = readFile(iFilePath='./_data/data.csv', years=years, convertNaNToZero=True)
    if not writeToFile(oFilePath='./_data/python_objects.json', data=returnedObjects):
        print("Error while writing to specified file!")
    else:
        print("__________DONE__________")
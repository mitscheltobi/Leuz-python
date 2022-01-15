from __future__ import print_function
import csv
import jsonpickle
import _modules.listObject as listObject

def yieldObject(reader: csv.DictReader, years: int, numDropped: int) -> listObject.entry:
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
                    dat = line[4+years*i:3+years*(i+1)]
                    numbers = []
                    for itm in dat:
                        try:
                            #try to convert field to int
                            numbers.append(float(itm))
                        except ValueError:
                            #if not drop entire row
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


def readFile(years):
    objlst= []
    numDropped = 0

    #read csv data, generate python object and add to list
    with open('./_data/data.csv', newline='') as csvfile:
        rd = csv.reader(csvfile, delimiter=',', quotechar='|')
        gen = yieldObject(rd, years, numDropped)
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

    # write objects to json file
    with open('./_data/python_objects.json', 'w') as ofile:
        ofile.write(jsonpickle.encode(objlst, unpicklable=True))
        ofile.close()

    print(f"Dropped {numDropped} entrys becuase of faulty data...")
    print(f"Successfully saved {len(objlst)} entrys as JSON...")

if __name__ == '__main__':
    ### TODO get command line args for input, output, specified years, verbosity
    years = 10
    readFile(years)
    print("__________DONE__________")
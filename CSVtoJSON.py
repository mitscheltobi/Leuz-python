import csv
import jsonpickle
import _modules.listObject as listObject
import numpy as np

def yieldObject(reader: csv.DictReader, years: int) -> listObject.entry:
    # assumes fixed data length and positions
    # if there are multiple NACE categorys, move to end
    for line in reader:
        if line[0] != "ID":
            # metadata
            id = int(line[0][:-1])
            name = line[1]
            try:
                naice = [int(line[2])]
            except ValueError:
                naice = [line[2].split("; ")]

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
                            #if not possible leave as string
                            # print(f"{name}: string value {itm} in data, dropping row...")
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


def readFile(years):
    objlst= []
    #read csv data, generate python object and add to list
    with open('./_data/data.csv', newline='') as csvfile:
        rd = csv.reader(csvfile, delimiter=',', quotechar='|')
        gen = yieldObject(rd, years)
        while True:
            try:
                objlst.append(next(gen))
            except StopIteration:
                # generator yields nothing == end of list
                # print(objlst)
                break

    # write objects to json file
    with open('./_data/python_objects.json', 'w') as ofile:
        ofile.write(jsonpickle.encode(objlst, unpicklable=True))
        ofile.close()

if __name__ == '__main__':
    years = 10
    readFile(years)
    print("___DONE___")

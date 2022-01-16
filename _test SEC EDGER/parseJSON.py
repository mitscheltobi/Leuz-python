import json
import os
import statusBar
from collections import defaultdict

def reformatData(rawData):
    res = {'year': [], 'val': []}
    for x in reversed(rawData):
        if x['end'][:4] not in res['year']:
            res['year'].append(x['end'][:4])
            res['val'].append(x['val'])
    return res

def filterByForm(rawData, formName= '10-K'):
    return [x for x in rawData if x['form']==formName]

files = os.listdir('C:/Users/to200/Desktop/company facts')
dictmissing = defaultdict(int)
i = 0
a = 0
d = 0
exports = []
for itm in files:
    bar = statusBar.statusBar(len(files), size=100)
    with open(f"C:/Users/to200/Desktop/company facts/{itm}") as file:
        gen = file.read()
        temp = json.loads(gen)

        def probeErr(key):
            if key not in temp['facts']['us-gaap'].keys(): dictmissing[key] += 1

        for x in ['IncomeLossFromContinuingOperations', 'NetIncomeLoss', 'Assets', 'CashAndCashEquivalentsAtCarryingValue', 'LiabilitiesCurrent', 'StockholdersEquity', 'LiabilitiesAndStockholdersEquity', 'DeferredTaxLiabilities', 'DepreciationDepletionAndAmortization']:
            probeErr(x)
        
        name = temp['entityName']
        cik = temp['cik']
        try:
            opInc = reformatData(filterByForm(temp['facts']['us-gaap']['IncomeLossFromContinuingOperations']['units']['USD']))
            netInc = reformatData(filterByForm(temp['facts']['us-gaap']['NetIncomeLoss']['units']['USD']))
            Assets = reformatData(filterByForm(temp['facts']['us-gaap']['Assets']['units']['USD']))
            cash = reformatData(filterByForm(temp['facts']['us-gaap']['CashAndCashEquivalentsAtCarryingValue']['units']['USD']))
            curLiabilities = reformatData(filterByForm(temp['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD']))
            stockholdersEquity = reformatData(filterByForm(temp['facts']['us-gaap']['StockholdersEquity']['units']['USD']))
            liabilitiesAndStockholdersEquity = reformatData(filterByForm(temp['facts']['us-gaap']['LiabilitiesAndStockholdersEquity']['units']['USD']))
            taxPayable = reformatData(filterByForm(temp['facts']['us-gaap']['DeferredTaxLiabilities']['units']['USD']))
            depreciation = reformatData(filterByForm(temp['facts']['us-gaap']['DepreciationDepletionAndAmortization']['units']['USD']))

            exports.append({
                'name': name,
                'cik': cik,
                'opInc': opInc,
                'netInc': netInc,
                'Assets': Assets,
                'cash': cash,
                'curLiabilities': curLiabilities,
                'stockholdersEquity': stockholdersEquity,
                'liabilitiesAndStockholdersEquity': liabilitiesAndStockholdersEquity,
                'taxPayable': taxPayable,
                'depreciation': depreciation
            })
            a += 1
        except KeyError:
            d += 1
            pass
        file.close()
    i += 1
    bar.update(i)

# write objects to json file
with open('processedData.json', 'w') as ofile:
    # ofile.write(exports)
    ofile.write(json.dumps(exports))
    ofile.close()

print(f"\n\nAccepted: {a}\n Denied: {d}\nTotal: {i}\n\n")
print(dict(dictmissing))
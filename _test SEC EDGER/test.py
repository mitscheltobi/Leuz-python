import json

with open('processedData.json') as f:
    data = f.read()
    lst = json.loads(data)
    print(len(lst))
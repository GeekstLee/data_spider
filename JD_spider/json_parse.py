import json


def parseAllJsonFile(start, end):
    jsonDic = dict()
    for i in range(start, end + 1):
        filePath = "./spider_json/" + str(i) + ".json"
        with open(filePath, 'r') as load_file:
            loadDict = json.load(load_file)
            json_string = json.dumps(loadDict)
            loadDict = json.loads(json_string)
        first_category_id = loadDict['first_category_id']
        jsonDic[first_category_id] = loadDict

    return jsonDic


if __name__ == '__main__':
    jsonDic = parseAllJsonFile(1, 2)
    print(jsonDic)
    for firstCat in jsonDic:
        print(firstCat, "====", jsonDic[firstCat])

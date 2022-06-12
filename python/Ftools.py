import csv

def createDictCSV(fileName="", testDict={},idealDict={},delimiter=',',main_dir=''):
    nodedict={}
    with open(fileName+"num.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile,delimiter=delimiter)
        for k,v in testDict.items():
            csvWriter.writerow([k]+v)
            csvWriter.writerow([k]+idealDict[k])
        csvFile.close()
    with open(main_dir+"/label.csv","r") as f:
        for l in f:
            arr=l.strip().split(",")
            nodedict[int(arr[0])] = arr[1]
    with open(fileName+"lable.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile,delimiter=delimiter)
        for k,v in testDict.items():
            csvWriter.writerow([nodedict[k]]+[nodedict[node] for node in v])
            csvWriter.writerow([nodedict[k]]+[nodedict[node] for node in idealDict[k]])
        csvFile.close()
def createDictCSV2(fileName="", testDict1={},testDict2={},idealDict={},delimiter=',',main_dir=''):
    nodedict={}
    with open(fileName+"num.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile,delimiter=delimiter)
        for k,v in testDict1.items():
            csvWriter.writerow([k]+v)
            csvWriter.writerow([k]+testDict2[k])
            csvWriter.writerow([k] + idealDict[k])
        csvFile.close()
    with open(main_dir+"/label.csv","r") as f:
        for l in f:
            arr=l.strip().split(",")
            nodedict[int(arr[0])] = arr[1]
    with open(fileName+"lable.csv", "w") as csvFile:
        csvWriter = csv.writer(csvFile,delimiter=delimiter)
        for k,v in testDict1.items():
            csvWriter.writerow([nodedict[k]]+[nodedict[node] for node in v])
            csvWriter.writerow([k]+testDict2[k])
            csvWriter.writerow([nodedict[k]]+[nodedict[node] for node in idealDict[k]])
        csvFile.close()

if __name__ =="main":
    pass
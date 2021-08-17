import sys
import yaml
import pathlib2


folder = sys.argv[1]


def getAll(directory):
    theList = []
    paths = pathlib2.Path(directory)
    for directories in paths.iterdir():
        for directory in directories.iterdir():
            theDirectory = directory.parts[0] + '/' + directory.parts[1] + '/' + directory.parts[2]
            theList.insert(0, theDirectory)

    return theList


def getServicesFolder(data):
    theList = []

    for line in data:
        path = pathlib2.Path(line)
        thePath = path.parts[1] + '/' + path.parts[2]
        theList.insert(0, thePath)

    sortedList = sorted(set(theList))
    return sortedList


def readYaml(filePath):
    with open(filePath) as data:
        loadData = list(yaml.safe_load_all(data))
    return loadData


def loadYaml(data, newData):
    with open(data, 'w') as data:
        yaml.safe_dump_all(newData, data)


def main():
    for service in getServicesFolder(getAll(folder)):
        deploymentPath = "services/" + service + "/" + "kube" + "/" + "base" + "/" + "deployment.yaml"
        if pathlib2.Path(deploymentPath).is_file():
            readIt = readYaml(deploymentPath)
            serviceName = readIt[1]["metadata"]["name"]
            selector = {"selector": {"matchLabels": {"service": serviceName}}}
            readIt[1]["apiVersion"] = "apps/v1"
            readIt[1]["spec"].update(selector)

            loadYaml(deploymentPath, readIt)
            print(serviceName)
            print(readIt[1]["spec"]["template"]["metadata"]["labels"])
            print(readIt[1]["metadata"]["name"])
            print(readIt[1]["apiVersion"])


if __name__ == "__main__":
    main()
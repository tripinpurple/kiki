import sys
import json
import pathlib2

# Usage: bake-json.py [app] [service/path service/path] [registry] [tag] [true/false] [folder]

app = sys.argv[1]
services = sys.argv[2]
registry = sys.argv[3]
tag = sys.argv[4]
everything = sys.argv[5]
folder = sys.argv[6]


def getAll(directory):
    theList = []
    paths = pathlib2.Path(directory)
    for directories in paths.iterdir():
        for directory in directories.iterdir():
            theDirectory = directory.parts[0] + '/' + directory.parts[1] + '/' + directory.parts[2]
            theList.insert(0, theDirectory)

    return theList


def getServicesCLI(data):
    theList = []

    for line in data.split(' '):
        path = pathlib2.Path(line)
        thePath = path.parts[1] + '/' + path.parts[2]
        theList.insert(0, thePath)

    sortedList = sorted(set(theList))
    return sortedList


def getServicesFolder(data):
    theList = []

    for line in data:
        path = pathlib2.Path(line)
        thePath = path.parts[1] + '/' + path.parts[2]
        theList.insert(0, thePath)

    sortedList = sorted(set(theList))
    return sortedList


def bakeJson(paths):

    def writeJson(newData, filename='docker-bake.json'):
        with open(filename, 'r+') as file:
            fileData = json.load(file)
            fileData["target"].update(newData)
            fileData["group"]["default"]["targets"].append(renamedPath)
            file.seek(0)
            json.dump(fileData, file, indent=4)

    with open("docker-bake.json", mode='w+', encoding='utf-8') as feedsJson:
        entry = {"group": {"default": {"targets": []}}, "target": {}}
        json.dump(entry, feedsJson)

    for line in paths:
        name = line
        print(name)
        targetDocker = "Dockerfile.build"
        targetName = "/".join(name.strip("/").split('/'))
        targetContext = "/".join(name[0].strip("/").split('/')[5:]) + "/./"
        targetEcr = str(registry) + "/" + app + "/" + targetName + ":" + tag

        renamedPath = targetName.replace('/', '-')

        jsonString = {renamedPath: {"context": targetContext, "dockerfile": targetDocker, "tags": [targetEcr]}}

        writeJson(jsonString)


def main():
    if everything == "true":
        bakeJson(getServicesFolder(getAll(folder)))
    elif everything == "false":
        bakeJson(getServicesCLI(services))
    else:
        print("Nothing to do.")

if __name__ == "__main__":
    main()

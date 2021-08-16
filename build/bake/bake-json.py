import sys
import json
import pathlib

# Usage: bake-json.py [app] [service/path service/path] [registry] [tag]

app = sys.argv[1]
registry = sys.argv[3]
tag = sys.argv[4]


def getServices(data):
    theList = []

    for line in data.split(' '):
        path = pathlib.Path(line)
        thePath = path.parts[1] + '/' + path.parts[2]
        theList.insert(0, thePath)

    sortedList = sorted(set(theList))
    return sortedList


paths = getServices(sys.argv[2])


def bakeJson():
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

        targetDocker = "Dockerfile.build"
        targetName = "/".join(name.strip("/").split('/'))
        targetContext = "/".join(name[0].strip("/").split('/')[5:]) + "/./"
        targetEcr = str(registry) + "/" + app + "/" + targetName + ":" + tag

        renamedPath = targetName.replace('/', '-')

        jsonString = {renamedPath: {"context": targetContext, "dockerfile": targetDocker, "tags": [targetEcr]}}

        writeJson(jsonString)


def main():
    if paths == "":
        print("No services found.")
    else:
        bakeJson()

if __name__ == "__main__":
    main()

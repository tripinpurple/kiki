import os
import sys
import pathlib2
import subprocess
from datetime import datetime

services = sys.argv[1]
everything = sys.argv[2]
folder = sys.argv[3]

now = datetime.now()
currentTime = now.strftime("1.%Y%m%d.%H%M%S")

currentDirectory = pathlib2.Path.cwd()


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


def goBuild(theServices):
    for service in theServices:
        print(service)
        tidyCommand = 'go mod tidy'
        buildCommand = 'go build -ldflags "-X main.appversion='+currentTime+'" -o '+str(currentDirectory)+'/services/'+service+'/app .'
        subprocess.call(tidyCommand, cwd="services/" + service, shell=True, env={'GOOS': os.environ['GOOS'], 'GOARCH': os.environ['GOARCH'], 'GOSUMDB': os.environ['GOSUMDB'], 'GOPRIVATE': os.environ['GOPRIVATE']})
        subprocess.call(buildCommand, cwd="services/" + service, shell=True, env={'GOOS': os.environ['GOOS'], 'GOARCH': os.environ['GOARCH'], 'GOSUMDB': os.environ['GOSUMDB'], 'GOPRIVATE': os.environ['GOPRIVATE']})


def main():
    if everything == "true":
        goBuild(getServicesFolder(getAll(folder)))
    elif everything == "false":
        if services == "":
            print("No services to build.")
        else:
            goBuild(getServicesCLI(services))
    else:
        print("Nothing to do.")

if __name__ == "__main__":
    main()
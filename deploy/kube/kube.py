import sys
import yaml
import pathlib2
from kubernetes import client, config

# Usage: kube.py [app] [service/path service/path] [registry] [tag] [namespace] [true/false] [folder]

app = sys.argv[1]
services = sys.argv[2]
registry = sys.argv[3]
tag = sys.argv[4]
namespace = sys.argv[5]
everything = sys.argv[6]
folder = sys.argv[7]


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


def readYaml(filePath):
    with open(filePath) as data:
        loadData = list(yaml.safe_load_all(data))
    return loadData


def loadYaml(data, newData):
    with open(data, 'w') as data:
        yaml.safe_dump_all(newData, data)


def patchDeployment(name, body):
    api = client.AppsV1Api()

    patch = api.patch_namespaced_deployment(
        name=name, namespace=namespace, body=body, pretty=True
    )

    print("\n[INFO] '"+name+"' container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            patch.metadata.namespace,
            patch.metadata.name,
            patch.metadata.generation,
            patch.spec.template.spec.containers[0].image,
        )
    )


def patchCronjob(name, body):
    api = client.BatchV1beta1Api()

    patch = api.patch_namespaced_cron_job(
        name=name, namespace=namespace, body=body, pretty=True
    )

    print("\n[INFO] '"+name+"' container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            patch.metadata.namespace,
            patch.metadata.name,
            patch.metadata.generation,
            patch.spec.jobTemplate.spec.template.spec.containers[0].image
        )
    )


def patchConfig(name, body):
    api = client.CoreV1Api()

    patch = api.patch_namespaced_config_map(
        name=name, namespace=namespace, body=body, pretty=True
    )

    print("\n[INFO] configmap '"+name+"' patched\n")
    print("NAME:\n%s\n" % patch.metadata.name)
    print("DATA:\n%s\n" % patch.data)


def multiDeployment(services):
    config.load_kube_config()

    for service in services:

        deploymentPath = "services/" + service + "/" + "kube" + "/" + "base" + "/" + "deployment.yaml"
        cronjobPath = "services/" + service + "/" + "kube" + "/" + "base" + "/" + "cronjob.yaml"

        configPathDevelopment = "services/" + service + "/" + "kube" + "/" + "overlays" + "/" + "stage" + "/" + "config.yaml"
        configPathProduction = "services/" + service + "/" + "kube" + "/" + "overlays" + "/" + "production" + "/" + "config.yaml"

        if namespace == "default":
            configPath = configPathDevelopment
        elif namespace == "production":
            configPath = configPathProduction
        else:
            print("Namespace not selected.")

        readIt = readYaml(configPath)
        configName = readIt[0]['metadata']['name']
        patchConfig(configName, configPath)

        if pathlib.Path(deploymentPath).is_file():

            filePath = deploymentPath
            readIt = readYaml(filePath)
            image = registry + '/' + app + '/' + service + ':' + tag

            readIt[1]['spec']['template']['spec']['containers'][0]['image'] = image

            loadYaml(deploymentPath, readIt)

            serviceName = readIt[1]['metadata']['name']

            updateDeployment(filePath, serviceName)


        elif pathlib.Path(cronjobPath).is_file():

            filePath = cronjobPath
            readIt = readYaml(filePath)
            image = registry + '/' + app + '/' + service + ':' + tag

            readIt[0]['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['image'] = image

            loadYaml(cronjobPath, readIt)

            serviceName = readIt[0]['metadata']['name']

            updateCronjob(filePath, serviceName)

        else:
            print('Files do not exist.')


def updateCronjob(cronjob, name):
    patchCronjob(name, cronjob)


def updateDeployment(deployment, name):
    patchDeployment(name, deployment)


def main():
    if everything == "true":
        multiDeployment(getServicesFolder(getAll(folder)))
    elif everything == "false":
        multiDeployment(getServicesCLI(services))

    else:
        print("Nothing to do.")



if __name__ == "__main__":
    main()
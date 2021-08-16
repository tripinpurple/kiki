import sys
import yaml
import pathlib
from kubernetes import client, config

# Usage: kube.py [app] [service/path service/path] [registry] [tag] [namespace]

app = sys.argv[1]
registry = sys.argv[3]
tag = sys.argv[4]
namespace = sys.argv[5]


def readYaml(filePath):
    with open(filePath) as data:
        loadData = list(yaml.safe_load_all(data))
    return loadData


def loadYaml(data, newData):
    with open(data, 'w') as data:
        yaml.safe_dump_all(newData, data)


def getServices(data):
    theList = []

    for line in data.split(' '):
        thePath = pathlib.Path(line)
        combinedPath = thePath.parts[1] + '/' + thePath.parts[2]
        theList.insert(0, combinedPath)

    sortedList = sorted(set(theList))
    return sortedList


def patchService(name, body):
    api = client.AppsV1Api()

    servicePatch = api.patch_namespaced_deployment(
        name=name, namespace=namespace, body=body
    )

    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            servicePatch.metadata.namespace,
            servicePatch.metadata.name,
            servicePatch.metadata.generation,
            servicePatch.spec.template.spec.containers[0].image,
        )
    )


def patchConfig(name, body):

    api = client.CoreV1Api()

    configMapPatch = api.patch_namespaced_config_map(
        name=name, namespace=namespace, body=body
    )

    print("\n[INFO] configmap `test-configmap` patched\n")
    print("NAME:\n%s\n" % configMapPatch.metadata.name)
    print("DATA:\n%s\n" % configMapPatch.data)


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
            print('Files no exist.')


def updateCronjob(cronjob, name):
    patchService(name, cronjob)


def updateDeployment(deployment, name):
    patchService(name, deployment)


def main():
    multiDeployment(getServices(sys.argv[2]))


if __name__ == "__main__":
    main()
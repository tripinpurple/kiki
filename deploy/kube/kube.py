import sys
import yaml
import pathlib2
from kubernetes import client, config
from kubernetes.client.rest import ApiException

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

    patch = api.patch_namespaced_deployment(name=name, body=body, namespace=namespace)

    print("[✓] '"+name+"' applied: deployment image ['"+patch.spec.template.spec.containers[0].image+"']")


def patchCronjob(name, body):
    api = client.BatchV1beta1Api()

    api.patch_namespaced_cron_job(name=name, body=body, namespace=namespace)

    print("[✓] '"+name+"' applied: cronJob")


def patchService(name, body):
    api = client.CoreV1Api()

    api.patch_namespaced_service(name=name, body=body, namespace=namespace)

    print("[✓] '"+name+"' applied: service ")


def patchConfig(name, body):
    api = client.CoreV1Api()

    api.patch_namespaced_config_map(name=name, namespace=namespace, body=body)

    print("[✓] '"+name+"' applied: config ")


def patchSecret(name, body):
    api = client.CoreV1Api()

    api.patch_namespaced_secret(name=name, body=body, namespace=namespace)

    print("[✓] '"+name+"' applied: secret ")


def createConfig(name, body):
    api = client.CoreV1Api()

    api.create_namespaced_config_map(body=body, namespace=namespace)

    print("[✓] '"+name+"' created: config ")


def createSecret(name, body):
    api = client.CoreV1Api()

    api.create_namespaced_secret(body=body, namespace=namespace)

    print("[✓] '"+name+"' created: secret ")


def multiDeployment(theServices):
    config.load_kube_config()

    for service in theServices:

        deploymentPath = "services/" + service + "/kube/base/deployment.yaml"
        cronjobPath = "services/" + service + "/kube/base/cronjob.yaml"

        configPathDevelopment = "services/" + service + "/kube/overlays/stage/config.yaml"
        configPathProduction = "services/" + service + "/kube/overlays/production/config.yaml"

        if pathlib2.Path(deploymentPath).is_file():

            readIt = readYaml(deploymentPath)

            image = registry + '/' + app + '/' + service + ':' + tag

            readIt[1]['spec']['template']['spec']['containers'][0]['image'] = image

            loadYaml(deploymentPath, readIt)

            deploymentName = readIt[1]['metadata']['name']

            patchDeployment(deploymentName, readIt[1])

            serviceName = readIt[1]['metadata']['name']

            patchService(serviceName, readIt[0])


        elif pathlib2.Path(cronjobPath).is_file():

            readIt = readYaml(cronjobPath)

            image = registry + '/' + app + '/' + service + ':' + tag

            readIt[0]['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['image'] = image

            loadYaml(cronjobPath, readIt)

            cronjobName = readIt[0]['metadata']['name']

            patchCronjob(cronjobName, readIt[0])

        else:
            print('Files do not exist!')

        if namespace == "default":
            configPath = configPathDevelopment
        elif namespace == "production":
            configPath = configPathProduction
        else:
            print("Namespace not selected!")

        readIt = readYaml(configPath)

        try:
            var = readIt[1]
            try:
                configName = readIt[0]['metadata']['name']
                secretName = readIt[1]['metadata']['name']
                patchConfig(configName, readIt[0])
                patchSecret(secretName, readIt[1])
            except ApiException as e:
                if e.reason == "Not Found":
                    configName = readIt[0]['metadata']['name']
                    secretName = readIt[1]['metadata']['name']
                    createConfig(configName, readIt[0])
                    createSecret(secretName, readIt[1])
                else:
                    print("Exception Raised!")
        except IndexError:
            if readIt[0]["kind"] == "ConfigMap":
                try:
                    configName = readIt[0]['metadata']['name']
                    patchConfig(configName, readIt[0])
                except ApiException as e:
                    if e.status == "Not Found":
                        configName = readIt[0]['metadata']['name']
                        createConfig(configName, readIt[0])
                    else:
                        print("Exception Raised!")

            elif readIt[0]["kind"] == "Secret":
                try:
                    secretName = readIt[0]['metadata']['name']
                    patchSecret(secretName, readIt[0])
                except ApiException as e:
                    if e.status == "Not Found":
                        secretName = readIt[0]['metadata']['name']
                        createSecret(secretName, readIt[0])
                    else:
                        print("Exception Raised!")
            else:
                print("Did not find Kind!")


def main():
    if everything == "true":
        multiDeployment(getServicesFolder(getAll(folder)))
    elif everything == "false":
        if services == "":
            print("Nothing to deploy!")
        else:
            multiDeployment(getServicesCLI(services))
    else:
        print("Nothing to do.")


if __name__ == "__main__":
    main()

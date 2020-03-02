import os
import yaml


def GetStateFilePath(repoFolder: str):
    if not os.path.isabs(repoFolder):
        repoFolder = os.path.join(os.getcwd(), repoFolder)
    return os.path.join(repoFolder, 'state.yaml')


def CheckStateDictIsValid(state: dict, resourceGroup: str, namespace: str, helmChart: str):
    return resourceGroup in state and \
           namespace in state[resourceGroup] and \
           helmChart in state[resourceGroup][namespace]


def AssertStateDictIsValid(state: dict, resourceGroup: str, namespace: str, helmChart: str):
    if not(CheckStateDictIsValid(state, resourceGroup, namespace, helmChart)):
        raise Exception(f'Helm chart {helmChart} in namespace {namespace} is not registered in state.')


def GetStateBranchname(resourceGroup: str, namespace: str, helmChart: str):
    return f'{resourceGroup}/{namespace}/{helmChart}'


def LoadState(repoFolder: str):
    stateFile = GetStateFilePath(repoFolder)
    if not os.path.isfile(stateFile):
        return {}

    with open(stateFile, 'r') as f:
        state = yaml.safe_load(f.read())

    return state


def DumpState(state: dict, repoFolder: str):
    stateFile = GetStateFilePath(repoFolder)

    os.makedirs(os.path.dirname(stateFile), exist_ok=True)
    with open(stateFile, 'w') as f:
        f.write(yaml.safe_dump(state))

    return stateFile


def StructureHelmChartData(version: str):
    return {
        'version': version
    }


def GetHelmChartData(state: dict, resourceGroup: str, namespace: str, helmChart: str):
    AssertStateDictIsValid(state, resourceGroup, namespace, helmChart)

    helmChartData = state[resourceGroup][namespace][helmChart]
    return helmChartData


def UpdateHelmVersion(state: dict, resourceGroup: str, namespace: str, helmChart: str, version: str):
    if resourceGroup not in state:
        state[resourceGroup] = {}
    if namespace not in state[resourceGroup]:
        state[resourceGroup][namespace] = {}
    if helmChart not in state[resourceGroup][namespace]:
        state[resourceGroup][namespace][helmChart] = {}

    state[resourceGroup][namespace][helmChart] = StructureHelmChartData(version)







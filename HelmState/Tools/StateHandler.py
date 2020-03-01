import os
import yaml


NAMESPACE_KEY = 'namespace'
HELM_CHART_KEY = 'helm-chart'


def GetStateFilePath(stateFolder: str):
    if not os.path.isabs(stateFolder):
        stateFolder = os.path.join(os.getcwd(), stateFolder)
    return os.path.join(stateFolder, 'state.yaml')


def CheckStateDictIsValid(state: dict, namespace: str, helmChart: str,
                          namespacekey = NAMESPACE_KEY, helmChartKey = HELM_CHART_KEY):
    return namespacekey not in state or \
            namespace not in state[namespacekey] or \
            helmChartKey not in state[namespacekey][namespace] or \
            helmChart not in state[namespacekey][namespace][helmChartKey]


def AssertStateDictIsValid(state: dict, namespace: str, helmChart: str,
                           namespacekey = NAMESPACE_KEY, helmChartKey = HELM_CHART_KEY):
    if not(CheckStateDictIsValid(state, namespace, helmChart,
                                 namespacekey, helmChartKey)):
        raise Exception(f'Helm chart {helmChart} in namespace {namespace} is not registered in state.')


def GetStateBranchname(resourceGroup: str, namespace: str, helmChart: str):
    return f'{resourceGroup}/{namespace}/{helmChart}'


def LoadState(stateFolder: str):
    stateFile = GetStateFilePath(stateFolder)
    if not os.path.isfile(stateFile):
        return {}

    with open(stateFile, 'r') as f:
        state = yaml.safe_load(f.read())

    return state


def DumpState(state: dict, stateFolder: str):
    stateFile = GetStateFilePath(stateFolder)

    os.makedirs(os.path.dirname(stateFile), exist_ok=True)
    with open(stateFile, 'w') as f:
        f.write(yaml.safe_dump(state))


def GetHelmVersion(state: dict, namespace: str, helmChart: str,
                  namespacekey = NAMESPACE_KEY, helmChartKey = HELM_CHART_KEY, asDict = True):
    AssertStateDictIsValid(state, namespace, helmChart, namespacekey, helmChartKey)

    version = state[namespacekey][namespace][helmChartKey][helmChart]
    if asDict:
        return {namespacekey: {namespace: {helmChartKey: {helmChart: version}}}}
    return version


def UpdateHelmVersion(state: dict, namespace: str, helmChart: str, version: str,
                      namespacekey = NAMESPACE_KEY, helmChartKey = HELM_CHART_KEY):
    if namespacekey not in state:
        state[namespacekey] = {}
    if namespace not in state[namespacekey]:
        state[namespacekey][namespace] = {}
    if helmChartKey not in state[namespacekey][namespace]:
        state[namespacekey][namespace][helmChartKey] = {}

    state[namespacekey][namespace][helmChartKey][helmChart] = version






import json
from typing import Union, List

import yaml
import sys
from HelmState.Tools import StateHandler
from HelmState.Tools import GitTools
from HelmState.Tools import ArgumentTools
from HelmState.Tools import DumpTools


def Main(args: list = None):
    arguments = ArgumentTools.ParseArguments(args)
    outputStr = HandleAction(arguments.action,
                             arguments.helm_chart,
                             arguments.version,
                             arguments.namespace,
                             arguments.resource_group,
                             arguments.message,
                             arguments.commits,
                             arguments.push,
                             arguments.folder,
                             arguments.output,
                             arguments.dumps,
                             arguments.master_branch,
                             arguments.remote,
                             arguments.remote_url,
                             arguments.offline)

    return outputStr


def HandleAction(action: str,
                 helmChart: Union[str, List[str]],
                 version: str = None,
                 namespace: str = 'default',
                 resourceGroup: str = 'default',
                 message: str = 'Auto state update',
                 commits: int = 1,
                 push: bool = False,
                 folder: str = './',
                 output: str = 'json',
                 dumps: str = None,
                 masterBranch: str = 'master',
                 remote: str = 'origin',
                 remoteUrl: str = None,
                 offline: bool = False):
    repoHelmCharts = helmChart if isinstance(helmChart, list) else [helmChart]
    outputData = {}
    repo = GitTools.GetRepo(folder, 
                            initializeIfNotExists=True, 
                            masterBranch=masterBranch, 
                            remote=remote, 
                            remoteUrl=remoteUrl,
                            push=push, 
                            offline=offline)
    if len(repoHelmCharts) == 0:
        repoHelmCharts = GitTools.GetHelmChartBranches(repo, resourceGroup, namespace, remote=remote, offline=offline)
    for repoHelmChart in repoHelmCharts:
        GitTools.CheckoutHelmChartBranch(repo, resourceGroup, namespace, repoHelmChart,
                                         masterBranch=masterBranch, remote=remote, offline=offline)
        if action == 'get':
            pass
        elif action == 'commit':
            if version is None:
                raise Exception('Please provide a version tag following the helm chart name. '
                                'Add -h/--help for more info.')
            state = StateHandler.LoadState(folder)
            StateHandler.UpdateHelmVersion(state, resourceGroup, namespace, repoHelmChart, version)
            GitTools.CommitState(repo, state, folder, resourceGroup, namespace, repoHelmChart, message,
                                 remote=remote, push=push, offline=offline)
        elif action == 'revert':
            GitTools.RevertState(repo, resourceGroup, namespace, repoHelmChart, commits, remote=remote, push=push, offline=offline)
        else:
            raise Exception('No matching action provided, please add -h/--help to get help.')

        state = StateHandler.LoadState(folder)
        helmChartData = StateHandler.GetHelmChartData(state, resourceGroup, namespace, repoHelmChart)
        if len(repoHelmCharts) > 1:
            outputData = DumpTools.MergeDictData(outputData, {repoHelmChart: helmChartData})
        else:
            outputData = helmChartData

    GitTools.CheckoutMasterBranch(repo, masterBranch=masterBranch, remote=remote, offline=offline)

    if output == 'json':
        outputStr = json.dumps(outputData, sort_keys=True, indent=4)
    elif output == 'yaml':
        outputStr = yaml.safe_dump(outputData)
    elif output == 'env':
        outputStr = DumpTools.DumpToEnv(outputData)
    else:
        raise Exception(f'Invalid output type specified: {output}, please add -h/--help to get help.')

    if dumps is not None:
        with open(dumps, 'w') as f:
            f.write(outputStr)

    return outputStr


if __name__ == "__main__":
    sys.stdout.write(Main())

import json
import yaml
from HelmState.Tools import StateHandler
from HelmState.Tools import GitTools
from HelmState.Tools import ArgumentTools


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
                             arguments.master_branch,
                             arguments.remote)

    print(outputStr)
    return outputStr


def HandleAction(action: str,
                 helmChart: str,
                 version: str = None,
                 namespace: str = 'default',
                 resourceGroup: str = 'default',
                 message: str = 'Auto state update',
                 commits: int = 1,
                 push: bool = False,
                 folder: str = './',
                 output: str = 'json',
                 masterBranch: str = 'master',
                 remote: str = 'remote'):

    repo = GitTools.GetRepoAndCheckoutBranch(folder, resourceGroup, namespace, helmChart, initializeIfNotExists=True,
                                             masterBranch=masterBranch, remote=remote, push=push)
    if action == 'get':
        pass
    elif action == 'commit':
        if version is None:
            raise Exception('Please provide a version tag following the helm chart name. '
                            'Add -h/--help for more info.')
        state = StateHandler.LoadState(folder)
        StateHandler.UpdateHelmVersion(state, resourceGroup, namespace, helmChart, version)
        GitTools.CommitState(repo, state, folder, resourceGroup, namespace, helmChart, message,
                             remote=remote, push=push)
    elif action == 'revert':
        GitTools.RevertState(repo, resourceGroup, namespace, helmChart, commits, remote=remote, push=push)
    else:
        raise Exception('No matching action provided, please add -h/--help to get help.')

    state = StateHandler.LoadState(folder)
    outputData = StateHandler.GetHelmVersion(state, resourceGroup, namespace, helmChart)

    if output == 'text':
        outputStr = StateHandler.GetHelmVersion(state, resourceGroup, namespace, helmChart, asDict=False)
    elif output == 'json':
        outputStr = json.dumps(outputData, sort_keys=True, indent=4)
    elif output == 'yaml':
        outputStr = yaml.safe_dump(outputData)
    else:
        raise Exception(f'Invalid output type specified: {output}, please add -h/--help to get help.')

    return outputStr



if __name__ == "__main__":
    Main()
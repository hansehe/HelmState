import git
import os
from HelmState.Tools import StateHandler


def GetRepo(stateFolder: str, resourceGroup: str, initializeIfNotExists = False):
    stateFile = StateHandler.GetStateFilePath(stateFolder, resourceGroup)
    submodule = os.path.dirname(stateFile)
    if not os.path.isdir(os.path.join(submodule, '.git')):
        if initializeIfNotExists:
            repo = git.Repo.init(submodule)
        else:
            raise Exception(f'State submodule {submodule} does not exist!')
    else:
        repo = git.Repo(submodule)

    return repo


def GetCommitCount(repo: git.Repo):
    count = repo.git.rev_list('--count', 'HEAD')
    return int(count)


def CommitState(state: dict, stateFolder: str, resourceGroup: str, message: str):
    StateHandler.DumpState(state, stateFolder, resourceGroup)
    repo = GetRepo(stateFolder, resourceGroup, initializeIfNotExists=True)
    stateFile = StateHandler.GetStateFilePath(stateFolder, resourceGroup)

    repo.index.add([stateFile])
    repo.index.commit(message)


def RevertState(stateFolder: str, resourceGroup: str, numberOfCommits = 1):
    repo = GetRepo(stateFolder, resourceGroup)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in module {resourceGroup}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)

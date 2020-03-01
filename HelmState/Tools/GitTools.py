import git
import os
from HelmState.Tools import StateHandler


def GetRepo(stateFolder: str, resourceGroup: str, initializeIfNotExists = False):
    stateFile = StateHandler.GetStateFilePath(stateFolder)
    repoFolder = os.path.dirname(stateFile)
    if not os.path.isdir(os.path.join(repoFolder, '.git')):
        if initializeIfNotExists:
            repo = git.Repo.init(repoFolder)
        else:
            raise Exception(f'State repoFolder {repoFolder} does not exist!')
    else:
        repo = git.Repo(repoFolder)
    repo.index.checkout(f'rg/{resourceGroup}', force=True)

    return repo


def GetCommitCount(repo: git.Repo):
    count = repo.git.rev_list('--count', 'HEAD')
    return int(count)


def CommitState(state: dict, stateFolder: str, resourceGroup: str, message: str):
    StateHandler.DumpState(state, stateFolder)
    repo = GetRepo(stateFolder, resourceGroup, initializeIfNotExists=True)
    stateFile = StateHandler.GetStateFilePath(stateFolder)

    repo.index.add([stateFile])
    repo.index.commit(message)


def RevertState(stateFolder: str, resourceGroup: str, numberOfCommits = 1):
    repo = GetRepo(stateFolder, resourceGroup)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in module {resourceGroup}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)


def CommitFiles(repo: git.Repo, branch: str, message: str, pushToOrigin: bool = False):
    current = repo.create_head(branch)
    current.checkout()
    master = repo.heads.master
    repo.git.pull('origin', master)

    if repo.index.diff(None) or repo.untracked_files:
        repo.git.add(A=True)
        repo.git.commit(m=message)
        if pushToOrigin:
            repo.git.push('--set-upstream', 'origin', current)
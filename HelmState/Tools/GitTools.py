import git
import os
from HelmState.Tools import StateHandler


def GetRepo(repoFolder: str, initializeIfNotExists=False):
    stateFile = StateHandler.GetStateFilePath(repoFolder)
    repoFolder = os.path.dirname(stateFile)
    if not os.path.isdir(os.path.join(repoFolder, '.git')):
        if initializeIfNotExists:
            repo = git.Repo.init(repoFolder)
        else:
            raise Exception(f'State repoFolder {repoFolder} does not exist!')
    else:
        repo = git.Repo(repoFolder)

    return repo


def GetCommitCount(repo: git.Repo):
    count = repo.git.rev_list('--count', 'HEAD')
    return int(count)


def CommitState(state: dict, repoFolder: str, message: str):
    StateHandler.DumpState(state, repoFolder)
    repo = GetRepo(repoFolder, initializeIfNotExists=True)
    stateFile = StateHandler.GetStateFilePath(repoFolder)

    repo.index.add([stateFile])
    repo.index.commit(message)


def RevertState(repoFolder: str, resourceGroup: str, numberOfCommits=1):
    repo = GetRepo(repoFolder)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in module {resourceGroup}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)


def CommitFiles(repo: git.Repo, branch: str, message: str, pushToOrigin: bool = True):
    if pushToOrigin:
        repo.git.pull('origin', 'master')
    if branch in repo.branches:
        current = repo.git.checkout(branch)
    else:
        current = repo.git.checkout('master', b=branch)

    if repo.index.diff(None) or repo.untracked_files:
        repo.git.add(A=True)
        repo.git.commit(m=message)
    if pushToOrigin:
        repo.git.push('--set-upstream', 'origin', current)

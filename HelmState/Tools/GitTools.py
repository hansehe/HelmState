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


def CommitFiles(repo: git.Repo, branch: str, message: str, files: list = None,
                remote: str = 'origin'):
    if repo.index.diff(None) or repo.untracked_files:
        if files is None:
            repo.git.add(A=True)
        else:
            repo.git.add(files)
        repo.git.commit(m=message)
    if remote in repo.remotes:
        repo.git.push('--set-upstream', remote, branch)


def CheckoutBranch(repo: git.Repo, branch: str,
                   masterBranch: str = 'master', remote: str = 'origin'):
    if branch in repo.branches:
        checkoutMessage = repo.git.checkout(branch)
    else:
        checkoutMessage = repo.git.checkout(masterBranch, b=branch)
    if 'Your branch is behind' in checkoutMessage:
        repo.git.pull(remote, branch)


def CommitState(state: dict, repoFolder: str, resourceGroup: str, namespace: str, helmChart: str, message: str,
                masterBranch: str = 'master', remote: str = 'origin'):
    StateHandler.DumpState(state, repoFolder)
    stateFile = StateHandler.GetStateFilePath(repoFolder)
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    repo = GetRepo(repoFolder, initializeIfNotExists=True)
    CheckoutBranch(repo, branch, masterBranch=masterBranch, remote=remote)
    CommitFiles(repo, branch, message, [stateFile], remote=remote)


def RevertState(repoFolder: str, resourceGroup: str, namespace: str, helmChart: str,
                numberOfCommits = 1, masterBranch: str = 'master', remote: str = 'origin'):
    repo = GetRepo(repoFolder, initializeIfNotExists=False)
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    CheckoutBranch(repo, branch, masterBranch=masterBranch, remote=remote)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in branch {branch}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)
    if remote in repo.remotes:
        repo.git.push('--set-upstream', '--force', remote, branch)
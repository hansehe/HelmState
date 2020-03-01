import git
import os
from HelmState.Tools import StateHandler


def CreateDefaultReadmeFile(repoFolder: str, filename = 'README.md', content: str = None):
    if content is None:
        content = '# Helm State \n'
        content += 'Get more info about the helm state tool at: https://github.com/hansehe/HelmState'

    defaultFile = os.path.join(repoFolder, filename)
    if not os.path.isfile(defaultFile):
        with open(defaultFile, 'w') as f:
            f.write(content)

    return defaultFile


def GetRepo(repoFolder: str, initializeIfNotExists=False,
            masterBranch: str = 'master', remote: str = 'origin', push: bool = True):
    stateFile = StateHandler.GetStateFilePath(repoFolder)
    repoFolder = os.path.dirname(stateFile)
    if not os.path.isdir(os.path.join(repoFolder, '.git')):
        if initializeIfNotExists:
            repo = git.Repo.init(repoFolder)
        else:
            raise Exception(f'State repoFolder {repoFolder} does not exist!')
    else:
        repo = git.Repo(repoFolder)

    if GetCommitCount(repo) == 0:
        defaultFile = CreateDefaultReadmeFile(repoFolder)
        CommitFiles(repo, masterBranch, 'initial commit', files=[defaultFile], remote=remote, push=push)

    return repo


def GetCommitCount(repo: git.Repo):
    try:
        count = repo.git.rev_list('--count', 'HEAD')
        return int(count)
    except git.exc.GitCommandError:
        return 0


def CommitFiles(repo: git.Repo, branch: str, message: str, files: list = None,
                remote: str = 'origin', push: bool = True):
    if repo.index.diff(None) or repo.untracked_files:
        if files is None:
            repo.git.add(A=True)
        else:
            repo.git.add(files)
        repo.git.commit(m=message)
    if remote in repo.remotes and push:
        repo.git.push('--set-upstream', remote, branch)


def CheckoutBranch(repo: git.Repo, branch: str,
                   masterBranch: str = 'master', remote: str = 'origin'):
    if branch in repo.branches:
        checkoutMessage = repo.git.checkout(branch)
    else:
        checkoutMessage = repo.git.checkout(masterBranch, b=branch)
    if 'Your branch is behind' in checkoutMessage:
        repo.git.pull(remote, branch)


def GetRepoAndCheckoutBranch(repoFolder: str, resourceGroup: str, namespace: str, helmChart: str, initializeIfNotExists = True,
                             masterBranch: str = 'master', remote: str = 'origin', push: bool = True):
    repo = GetRepo(repoFolder, initializeIfNotExists=initializeIfNotExists, masterBranch=masterBranch, remote=remote, push=push)
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    CheckoutBranch(repo, branch, masterBranch=masterBranch, remote=remote)
    return repo


def CommitState(repo: git.Repo, state: dict, repoFolder: str, resourceGroup: str, namespace: str, helmChart: str, message: str,
                remote: str = 'origin', push: bool = True):
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    stateFile = StateHandler.DumpState(state, repoFolder)
    CommitFiles(repo, branch, message, files=[stateFile], remote=remote, push=push)


def RevertState(repo: git.Repo, resourceGroup: str, namespace: str, helmChart: str,
                numberOfCommits = 1, remote: str = 'origin', push: bool = True):
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in branch {branch}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)
    if remote in repo.remotes and push:
        repo.git.push('--set-upstream', '--force', remote, branch)
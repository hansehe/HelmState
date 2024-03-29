from typing import List

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


def GetRepo(repoFolder: str, 
            initializeIfNotExists=False,
            masterBranch: str = 'master', 
            remote: str = 'origin', 
            remoteUrl: str = None, 
            push: bool = True, 
            offline: bool = False):
    stateFile = StateHandler.GetStateFilePath(repoFolder)
    repoFolder = os.path.dirname(stateFile)
    if not os.path.isdir(os.path.join(repoFolder, '.git')):
        if initializeIfNotExists:
            if remoteUrl is not None and not offline:
                repo = git.Repo.clone_from(remoteUrl, repoFolder)
            else:
                repo = git.Repo.init(repoFolder)
        else:
            raise Exception(f'State repoFolder {repoFolder} does not exist!')
    else:
        repo = git.Repo(repoFolder)

    if remoteUrl is not None:
        if remote in repo.remotes:
            repo.remotes[remote].set_url(remoteUrl)
        else:
            repo.create_remote(remote, remoteUrl)

    if GetCommitCount(repo) == 0:
        defaultFile = CreateDefaultReadmeFile(repoFolder)
        CommitFiles(repo, masterBranch, 'initial commit', files=[defaultFile], remote=remote, push=push, offline=offline)
    if not offline and remote in repo.remotes:
        repo.remotes[remote].update(prune=True)
    return repo


def GetCommitCount(repo: git.Repo):
    try:
        count = repo.git.rev_list('--count', 'HEAD')
        return int(count)
    except git.exc.GitCommandError:
        return 0


def NormalizeFile(repo: git.Repo, file: str):
    normalizedFile = os.path.normpath(file)
    if not os.path.isabs(normalizedFile):
        normalizedFile = os.path.join(os.path.normpath(repo.working_dir), normalizedFile)
    return normalizedFile


def NormalizeFiles(repo: git.Repo, files: list):
    normalizedFiles = []
    for file in files:
        normalizedFile = NormalizeFile(repo, file)
        normalizedFiles.append(normalizedFile)
    return normalizedFiles


def CheckForUntrackedChanges(repo: git.Repo, files: list = None):
    if files is None:
        return repo.index.diff(None) or repo.untracked_files

    aFileIsUntracked = False
    normalizedFiles = NormalizeFiles(repo, files)
    normalizedUntrackedFiles = NormalizeFiles(repo, repo.untracked_files)
    for normalizedFile in normalizedFiles:
        if normalizedFile in normalizedUntrackedFiles:
            aFileIsUntracked = True
            break

    return repo.index.diff(None, paths=normalizedFiles) or aFileIsUntracked


def CommitFiles(repo: git.Repo, branch: str, message: str, files: list = None,
                remote: str = 'origin', 
                push: bool = True, 
                offline: bool = False):
    if CheckForUntrackedChanges(repo, files):
        if files is None:
            repo.git.add(A=True)
        else:
            repo.git.add(files)
        repo.git.commit(m=message)
    if remote in repo.remotes and push and not offline:
        repo.git.push('--set-upstream', remote, branch)


def GetBranchState(repo: git.Repo, branch: str):
    commitsDiff = repo.git.rev_list('--left-right', '--count', f'{branch}...{branch}@{{u}}')
    numCommitsAhead, numCommitsBehind = commitsDiff.split('\t')
    return int(numCommitsAhead), int(numCommitsBehind)



def GetRemoteBranchNames(repo: git.Repo, 
                         remote: str = 'origin'):
    remoteBranches = repo.remotes[remote].refs
    remoteBranchNames = list(map(lambda x: str(x), remoteBranches))
    return remoteBranchNames


def PullBranch(repo: git.Repo, branch: str, 
               remote: str = 'origin', 
               checkoutBranchFromOrigin = False):
    if remote in repo.remotes:
        remoteBranches = GetRemoteBranchNames(repo, remote=remote)
        remoteBranch = f'{remote}/{branch}'
        if remoteBranch in remoteBranches:
            repo.index.reset(head=True)
            if checkoutBranchFromOrigin:
                repo.git.checkout(remoteBranch, b=branch)
            else:
                numCommitsAhead, numCommitsBehind = GetBranchState(repo, branch)
                if numCommitsBehind > 0:
                    repo.git.pull(remote, branch)
                repo.index.reset(head=True)
            return True
    return False


def CheckoutBranch(repo: git.Repo, branch: str,
                   masterBranch: str = 'master', 
                   remote: str = 'origin', 
                   offline: bool = False):
    if branch in repo.branches:
        repo.git.checkout(branch)
        if not offline:
            PullBranch(repo, branch, remote=remote)
    else:
        remoteExists = PullBranch(repo, branch, remote=remote, checkoutBranchFromOrigin=True) if not offline else False
        if not remoteExists:
            repo.git.checkout(masterBranch)
            if not offline:
                PullBranch(repo, masterBranch, remote=remote)
            repo.git.checkout(masterBranch, b=branch)


def CheckoutMasterBranch(repo: git.Repo,
                         masterBranch: str = 'master', 
                         remote: str = 'origin', 
                         offline: bool = False):
    CheckoutBranch(repo, masterBranch, masterBranch=masterBranch, remote=remote, offline=offline)


def CheckoutHelmChartBranch(repo: git.Repo, resourceGroup: str, namespace: str, helmChart: str,
                            masterBranch: str = 'master', 
                            remote: str = 'origin', 
                            offline: bool = False):
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    CheckoutBranch(repo, branch, masterBranch=masterBranch, remote=remote, offline=offline)


def GetHelmChartBranches(repo: git.Repo, resourceGroup: str, namespace: str,
                         remote: str = 'origin', 
                         offline: bool = False):
    helmCharts: List[str] = []
    repoBranches = list(map(lambda repoBranch: str(repoBranch), repo.branches))
    if not offline and remote in repo.remotes:
        remoteBranches = GetRemoteBranchNames(repo, remote=remote)
        for remoteBranch in remoteBranches:
            localBranch = remoteBranch.replace(f'{remote}/', '', 1)
            if localBranch not in repoBranches:
                repoBranches.append(localBranch)
    for branch in repoBranches:
        if branch.startswith(f'{resourceGroup}/{namespace}/'):
            helmCharts.append(str(branch).split('/')[2])
    return helmCharts


def CommitState(repo: git.Repo, state: dict, repoFolder: str, resourceGroup: str, namespace: str, helmChart: str, message: str,
                remote: str = 'origin', 
                push: bool = True, 
                offline: bool = False):
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    stateFile = StateHandler.DumpState(state, repoFolder)
    CommitFiles(repo, branch, message, files=[stateFile], remote=remote, push=push, offline=offline)


def RevertState(repo: git.Repo, resourceGroup: str, namespace: str, helmChart: str,
                numberOfCommits = 1, 
                remote: str = 'origin', 
                push: bool = True, 
                offline: bool = False):
    branch = StateHandler.GetStateBranchname(resourceGroup, namespace, helmChart)
    commitCount = GetCommitCount(repo)
    if commitCount <= numberOfCommits:
        raise Exception(f'Number of commits to revert ({numberOfCommits}) '
                        f'must be lower then counted commits ({commitCount}) in branch {branch}!')

    repo.head.reset(f'HEAD~{numberOfCommits}', index=True, working_tree=True)
    if remote in repo.remotes and push and not offline:
        repo.git.push('--set-upstream', '--force', remote, branch)

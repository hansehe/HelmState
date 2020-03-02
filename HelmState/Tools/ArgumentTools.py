import argparse
import os


def ParseArguments(args = None):
    parser = argparse.ArgumentParser()
    __AddStateHolderArguments(parser)
    arguments = parser.parse_args(args)
    return arguments


def __AddStateHolderArguments(parser: argparse.ArgumentParser):
    parser.add_argument("action", type=str,
                        help="Action, \r\n"
                             + "get current state with 'get', \r\n"
                             + "commit new state with 'commit', \r\n"
                             + "revert state with 'revert'.")

    parser.add_argument("-hc", "--helm-chart", type=str,
                        help="Set helm chart name.")

    parser.add_argument("-v", "--version", type=str,
                        help="Set helm chart version to commit.",
                        default=None)

    defaultNamespace = 'default'
    parser.add_argument("-n", "--namespace", type=str,
                        help=f"Set namespace. Default is '{defaultNamespace}'.",
                        default=defaultNamespace)

    defaultResourceGroup = 'default'
    parser.add_argument("-rg", "--resource-group", type=str,
                        help=f"Set resource group name. Default is '{defaultResourceGroup}'.",
                        default=defaultResourceGroup)

    defaultMessage = 'Auto state update'
    parser.add_argument("-m", "--message", type=str,
                        help=f"Set commit message. Default is '{defaultMessage}'.",
                        default=defaultMessage)

    defaultCommits = 1
    parser.add_argument("-c", "--commits", type=int,
                        help=f"Set number of commits to revert. Default is '{defaultCommits}'.",
                        default=defaultCommits)

    parser.add_argument("-p", "--push",
                        help="Push commits and reverts to origin.",
                        action='store_true')

    defaultFolder = os.getcwd()
    parser.add_argument("-f", "--folder", type=str,
                        help=f"Set repo folder containing all states. Default is '{defaultFolder}'.",
                        default=defaultFolder)

    defaultOutput = 'json'
    parser.add_argument("-o", "--output", type=str,
                        help=f"Set output type (json or yaml). Default output is '{defaultOutput}'.",
                        default=defaultOutput)

    defaultMaster = 'master'
    parser.add_argument("--master-branch", type=str,
                        help=f"Set master branch. Default master branch is '{defaultMaster}'.",
                        default=defaultMaster)

    defaultRemote = 'origin'
    parser.add_argument("--remote", type=str,
                        help=f"Set git remote prefix. Default remote is '{defaultRemote}'.",
                        default=defaultRemote)

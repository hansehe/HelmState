import argparse
import os


DEFAULT_STATE_FOLDER = os.path.join(os.getcwd(), 'state')


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

    parser.add_argument("-n", "--namespace", type=str,
                        help="Set namespace.",
                        default='default')

    parser.add_argument("-rg", "--resource-group", type=str,
                        help="Set resource group name.",
                        default='default')

    parser.add_argument("-m", "--message", type=str,
                        help="Set commit message.",
                        default='Auto state update')

    parser.add_argument("-c", "--commits", type=int,
                        help="Set number of commits to revert.",
                        default=1)

    parser.add_argument("-f", "--folder", type=str,
                        help="Set folder containing all states.",
                        default=DEFAULT_STATE_FOLDER)

    parser.add_argument("-o", "--output", type=str,
                        help="Set output type (text, json or yaml).",
                        default='text')

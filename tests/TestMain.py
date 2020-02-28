import unittest
import random
import os
import json
import yaml
from HelmState import Main
from HelmState.Tools import StateHandler


class TestMain(unittest.TestCase):
    stateFolder = os.path.join('tests', 'state')
    namespace = 'my-kubectl-namespace'
    helmChart = 'my-helm-chart'


    def GetDefaultArguments(self, resourceGroup: str, commits: int = 2, output = 'text'):
        random.seed()
        version = f'1.0.0-patch-{random.randint(0, 100)}'
        args = ['-hc', self.helmChart, '-v', version, '-rg', resourceGroup,
                '-n', self.namespace, '-f', self.stateFolder,
                '-c', str(commits), '-o', output, '-m', 'test commit']
        return args


    def test_commit(self, resourceGroup = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        args = ['commit'] + self.GetDefaultArguments(resourceGroup)
        Main.Main(args)


    def test_revert(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)
        args = ['revert'] + self.GetDefaultArguments(resourceGroup, commits=2)
        Main.Main(args)


    def test_get(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)
        args = ['get'] + self.GetDefaultArguments(resourceGroup)
        textOutput = Main.Main(args)
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='json')
        jsonOutput = json.loads(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='yaml')
        yamlOutput = yaml.safe_load(Main.Main(args))

        self.assertTrue(textOutput.startswith('1.0.0-patch-'))
        self.assertTrue(self.helmChart in jsonOutput[StateHandler.NAMESPACE_KEY][self.namespace][StateHandler.HELM_CHART_KEY])
        self.assertTrue(self.helmChart in yamlOutput[StateHandler.NAMESPACE_KEY][self.namespace][StateHandler.HELM_CHART_KEY])


if __name__ == '__main__':
    unittest.main()

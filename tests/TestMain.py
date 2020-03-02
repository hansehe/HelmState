import unittest
import random
import os
import json
import yaml
from HelmState import Main


class TestMain(unittest.TestCase):
    repoFolder = os.path.join('tests', 'state')
    namespace = 'my-kubectl-namespace'
    helmChart = 'my-helm-chart'


    def GetVersion(self):
        random.seed()
        version = f'1.0.0-patch-{random.randint(0, 100)}'
        return version


    def GetDefaultArguments(self, resourceGroup: str, version: str = '1.0.0', commits: int = 2, output = 'json'):
        args = ['-hc', self.helmChart, '-v', version, '-rg', resourceGroup,
                '-n', self.namespace, '-f', self.repoFolder,
                '-c', str(commits), '-o', output, '-m', 'test commit']
        return args


    def test_commit(self, resourceGroup = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        version = self.GetVersion()
        args = ['commit'] + self.GetDefaultArguments(resourceGroup, version=version)
        Main.Main(args)


    def test_revert(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)

        version = self.GetVersion()
        args = ['revert'] + self.GetDefaultArguments(resourceGroup, version=version, commits=2)
        Main.Main(args)


    def test_get(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)

        args = ['get'] + self.GetDefaultArguments(resourceGroup)
        jsonOutput = json.loads(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='yaml')
        yamlOutput = yaml.safe_load(Main.Main(args))

        self.assertTrue(jsonOutput['version'].startswith('1.0.0'))
        self.assertTrue(yamlOutput['version'].startswith('1.0.0'))


if __name__ == '__main__':
    unittest.main()

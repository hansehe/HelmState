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
    helmCharts = ['my-helm-chart1', 'my-helm-chart2']

    def GetVersion(self):
        random.seed()
        version = f'1.0.0-patch-{random.randint(0, 100)}'
        return version

    def GetDefaultArguments(self, resourceGroup: str, version: str = '1.0.0', commits: int = 2, output: str = 'json',
                            multipleHelmCharts: bool = False,
                            listAllHelmCharts: bool = False):
        args = []
        if not listAllHelmCharts:
            args = ['-hc']
            if multipleHelmCharts:
                args += self.helmCharts
            else:
                args += [self.helmChart]
        args += ['-v', version, '-rg', resourceGroup,
                 '-n', self.namespace, '-f', self.repoFolder,
                 '-c', str(commits), '-o', output, '-m', 'test commit',
                 '--dumps', os.path.join(self.repoFolder, 'output.yaml')]
        return args

    def test_commit(self, resourceGroup: str = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        version = self.GetVersion()
        args = ['commit'] + self.GetDefaultArguments(resourceGroup, version=version)
        Main.Main(args)
        args = ['commit'] + self.GetDefaultArguments(resourceGroup, version=version, multipleHelmCharts=True)
        Main.Main(args)

    def test_revert(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)
        self.test_commit(resourceGroup=resourceGroup)

        version = self.GetVersion()
        args = ['revert'] + self.GetDefaultArguments(resourceGroup, version=version, commits=2)
        Main.Main(args)
        args = ['revert'] + self.GetDefaultArguments(resourceGroup, version=version, commits=2, multipleHelmCharts=True)
        Main.Main(args)

    def test_get(self):
        resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'
        self.test_commit(resourceGroup=resourceGroup)

        args = ['get'] + self.GetDefaultArguments(resourceGroup)
        jsonOutput = json.loads(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='yaml')
        yamlOutput = yaml.safe_load(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='env')
        envOutput = Main.Main(args)

        self.assertTrue(jsonOutput['version'].startswith('1.0.0'))
        self.assertTrue(yamlOutput['version'].startswith('1.0.0'))
        self.assertTrue('VERSION=1.0.0' in envOutput)

        args = ['get'] + self.GetDefaultArguments(resourceGroup, multipleHelmCharts=True)
        jsonOutput = json.loads(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='yaml', multipleHelmCharts=True)
        yamlOutput = yaml.safe_load(Main.Main(args))
        args = ['get'] + self.GetDefaultArguments(resourceGroup, output='env', multipleHelmCharts=True)
        envOutput = Main.Main(args)

        self.assertTrue(jsonOutput[self.helmCharts[0]]['version'].startswith('1.0.0'))
        self.assertTrue(yamlOutput[self.helmCharts[0]]['version'].startswith('1.0.0'))
        self.assertTrue(f'{self.helmCharts[0].replace("-", "_").upper()}__VERSION=1.0.0' in envOutput)
        self.assertTrue(jsonOutput[self.helmCharts[1]]['version'].startswith('1.0.0'))
        self.assertTrue(yamlOutput[self.helmCharts[1]]['version'].startswith('1.0.0'))
        self.assertTrue(f'{self.helmCharts[1].replace("-", "_").upper()}__VERSION=1.0.0' in envOutput)

        args = ['get'] + self.GetDefaultArguments(resourceGroup, listAllHelmCharts=True)
        jsonOutput = json.loads(Main.Main(args))
        self.assertTrue(jsonOutput[self.helmChart]['version'].startswith('1.0.0'))
        self.assertTrue(jsonOutput[self.helmCharts[0]]['version'].startswith('1.0.0'))
        self.assertTrue(jsonOutput[self.helmCharts[1]]['version'].startswith('1.0.0'))


if __name__ == '__main__':
    unittest.main()

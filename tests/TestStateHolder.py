import unittest
import random
import os
from HelmState.Tools import StateHandler
from HelmState.Tools import GitTools


class TestStateHolder(unittest.TestCase):
    repoFolder = os.path.join('tests', 'state')
    namespace = 'my-kubectl-namespace'
    helmChart = 'my-helm-chart'

    def test_loadAndUpdateState(self, repoFolder: str = 'non-existent', resourceGroup: str = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        state = StateHandler.LoadState(repoFolder)
        random.seed()
        version = f'1.0.0-patch-{random.randint(0, 100)}'
        StateHandler.UpdateHelmVersion(state, resourceGroup, self.namespace, self.helmChart, version)
        self.assertTrue(StateHandler.GetHelmChartData(state, resourceGroup, self.namespace, self.helmChart)['version'] == version)
        return state

    def test_loadUpdateAndCommitState(self, numberOfCommits: int = 2, resourceGroup = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        states = []
        repo = GitTools.GetRepo(self.repoFolder)
        for n in range(numberOfCommits):
            GitTools.CheckoutHelmChartBranch(repo, resourceGroup, self.namespace, self.helmChart)
            state = self.test_loadAndUpdateState(repoFolder=self.repoFolder, resourceGroup=resourceGroup)
            GitTools.CommitState(repo, state, self.repoFolder, resourceGroup, self.namespace, self.helmChart, 'test commit')
            currentState = StateHandler.LoadState(self.repoFolder)
            states.append(state)

            self.assertTrue(StateHandler.GetHelmChartData(state, resourceGroup, self.namespace, self.helmChart)['version'] ==
                            StateHandler.GetHelmChartData(currentState, resourceGroup, self.namespace, self.helmChart)['version'])

        return states

    def test_loadUpdateCommitAndRevertState(self, resourceGroup: str = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        repo = GitTools.GetRepo(self.repoFolder)
        states = self.test_loadUpdateAndCommitState(numberOfCommits=3, resourceGroup=resourceGroup)
        GitTools.CheckoutHelmChartBranch(repo, resourceGroup, self.namespace, self.helmChart)
        GitTools.RevertState(repo, resourceGroup, self.namespace, self.helmChart, numberOfCommits=2)
        self.assertRaises(Exception, GitTools.RevertState, repo, resourceGroup,
                          self.namespace, self.helmChart, numberOfCommits=2)
        currentState = StateHandler.LoadState(self.repoFolder)

        self.assertTrue(StateHandler.GetHelmChartData(states[0], resourceGroup, self.namespace, self.helmChart)['version'] ==
                        StateHandler.GetHelmChartData(currentState, resourceGroup, self.namespace, self.helmChart)['version'])


if __name__ == '__main__':
    unittest.main()

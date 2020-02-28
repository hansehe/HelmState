import unittest
import random
import os
from HelmState.Tools import StateHandler
from HelmState.Tools import GitTools


class TestStateHolder(unittest.TestCase):
    stateFolder = os.path.join('tests', 'state')
    namespace = 'my-kubectl-namespace'
    helmChart = 'my-helm-chart'

    def test_loadAndUpdateState(self, stateFolder = 'non-existent', resourceGroup = 'rg-domain-dev'):
        state = StateHandler.LoadState(stateFolder, resourceGroup)
        random.seed()
        version = f'1.0.0-patch-{random.randint(0, 100)}'
        StateHandler.UpdateHelmVersion(state, self.namespace, self.helmChart, version)
        self.assertTrue(StateHandler.GetHelmVersion(state, self.namespace, self.helmChart, asDict=False) == version)
        helmChartState = StateHandler.GetHelmVersion(state, self.namespace, self.helmChart)
        self.assertTrue(StateHandler.GetHelmVersion(helmChartState, self.namespace, self.helmChart, asDict=False) == version)
        return state


    def test_loadUpdateAndCommitState(self, numberOfCommits = 2, resourceGroup = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        states = []
        for n in range(numberOfCommits):
            state = self.test_loadAndUpdateState(self.stateFolder, resourceGroup=resourceGroup)
            GitTools.CommitState(state, self.stateFolder, resourceGroup, 'test commit')
            currentState = StateHandler.LoadState(self.stateFolder, resourceGroup)
            states.append(state)

            self.assertTrue(StateHandler.GetHelmVersion(state, self.namespace, self.helmChart, asDict=False) ==
                            StateHandler.GetHelmVersion(currentState, self.namespace, self.helmChart, asDict=False))

        return states


    def test_loadUpdateCommitAndRevertState(self, resourceGroup = None):
        if resourceGroup is None:
            resourceGroup = f'rg-domain-dev-{random.randint(0, 1000)}'

        states = self.test_loadUpdateAndCommitState(numberOfCommits=3, resourceGroup=resourceGroup)
        GitTools.RevertState(self.stateFolder, resourceGroup, numberOfCommits=2)
        self.assertRaises(Exception, GitTools.RevertState, self.stateFolder, resourceGroup, numberOfCommits=1)
        currentState = StateHandler.LoadState(self.stateFolder, resourceGroup)

        self.assertTrue(StateHandler.GetHelmVersion(states[0], self.namespace, self.helmChart, asDict=False) ==
                        StateHandler.GetHelmVersion(currentState, self.namespace, self.helmChart, asDict=False))


if __name__ == '__main__':
    unittest.main()

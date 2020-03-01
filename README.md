# Helm State

[![PyPI version](https://badge.fury.io/py/HelmState.svg)](https://badge.fury.io/py/HelmState)
[![Build Status](https://travis-ci.com/hansehe/HelmState.svg?branch=master)](https://travis-ci.com/hansehe/HelmState)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

The Helm State tool is a simple [GitOps](https://www.gitops.tech/) tool with [helm](https://helm.sh/) and [kubernetes](https://kubernetes.io/) in mind.
The Helm State tool stores deployed helm versions in [git](https://git-scm.com/) branches, 
where it will be easy to track previously deployed versions and which version is currently running.

The full helm version state is stored in a `state.yaml` file versioned by a git branch with this naming convention:
- `my-resource_group/my-namespace/my-helm-chart`:

Content structure of `state.yaml`:
```yaml
my-resource-group:
  my-namespace:
    my-helm-chart: 1.0.0
```


## Install Or Upgrade
- pip install --upgrade HelmState

## Prerequisites
- python3x

## Usage
The Helm State is available as a command line tool with `helmstate`.

First of all, either clone or initialize a new repository to where the state will be stored.
Then, try out some of the commands below with current working directory set to the repository folder.

### Commit new helm states and push last commit
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0
helmstate commit --helm-chart my-helm-chart --version 1.0.1 --push
```

### Get current helm state
```
helmstate get --helm-chart my-helm-chart
```

### Revert current helm state 2 commits back and push last revert
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0
helmstate commit --helm-chart my-helm-chart --version 1.0.1
helmstate commit --helm-chart my-helm-chart --version 1.0.2
helmstate revert --helm-chart my-helm-chart --commits 1
helmstate revert --helm-chart my-helm-chart --commits 1 --push
```

### Split different environments in resource groups
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0 --resource-group my-resource-group
```

### Set kubectl namespace to where the helm artifact was deployed
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0 --namespace my-namespace --resource-group my-resource-group
```

### More details with help
```
helmstate --help
```

## Development

### Dependencies:
  - `pip install twine`
  - `pip install wheel`
  - `pip install -r requirements.txt`

### Publish New Version.
1. Configure [setup.py](./setup.py) with new version.
2. Package: `python setup.py bdist_wheel`
3. Publish: `twine upload dist/*`

### Run Unit Tests
- python -m unittest
- docker build .
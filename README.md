# Helm State

[![PyPI version](https://badge.fury.io/py/HelmState.svg)](https://badge.fury.io/py/HelmState)
[![Build Status](https://travis-ci.com/hansehe/HelmState.svg?branch=master)](https://travis-ci.com/hansehe/HelmState)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

The Helm State tool is a simple [GitOps](https://www.gitops.tech/) tool based on the [helm](https://helm.sh/) konsept with [kubernetes](https://kubernetes.io/).
The Helm State tool stores deployed helm versions in [git](https://git-scm.com/) submodules, where it will be easy to track previously deployed versions and which version is currently running.

The full helm version state is stored in a `yaml` file versioned by git in the resource group submodule:
```yaml
namespace:
  my-namespace:
    helm-chart:
      my-helm-chart: 1.0.0
```


## Install Or Upgrade
- pip install --upgrade HelmState

## Prerequisites
- python3x

## Usage
The Helm State is available as a command line tool with `helmstate`.

### Commit new helm state
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0
```

### Get current helm state
```
helmstate get --helm-chart my-helm-chart
```

### Revert current helm state 2 commits back
```
helmstate commit --helm-chart my-helm-chart --version 1.0.0
helmstate commit --helm-chart my-helm-chart --version 1.0.1
helmstate commit --helm-chart my-helm-chart --version 1.0.2
helmstate revert --helm-chart my-helm-chart --commits 2
```

### Split different environments in resource group submodules
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
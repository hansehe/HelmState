# Helm State

[![PyPI version](https://badge.fury.io/py/HelmState.svg)](https://badge.fury.io/py/HelmState)
[![Build Status](https://travis-ci.com/hansehe/HelmState.svg?branch=master)](https://travis-ci.com/hansehe/HelmState)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

## Install Or Upgrade
- pip install --upgrade HelmState

## Prerequisites
- python3x

## Usage
The Helm State is available as a command line tool with `helmstate`.

### Commit new helm state
```
helmstate commit --helm-chart my-helm --version 1.0.0
```

### Get current helm state
```
helmstate get --helm-chart my-helm
```

### Revert current helm state 2 commits back
```
helmstate commit --helm-chart my-helm --version 1.0.0
helmstate commit --helm-chart my-helm --version 1.0.1
helmstate commit --helm-chart my-helm --version 1.0.2
helmstate revert --helm-chart my-helm --commits 2
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
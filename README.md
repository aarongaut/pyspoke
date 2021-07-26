# pyspoke

A python library supporting pubsub and remote procedure calls on Linux.

# Overview

TBD

# Installation

## From [PyPI](https://pypi.org/project/pyspoke/)

Install using pip:

```
python3 -m pip install pyspoke
```

## From latest source

First install build dependencies:

```
python3 -m pip install build
```

Building the distribution:

```
git clone https://gitlab.com/samflam/pyspoke.git
cd pyspoke
make
```

To install, you can `pip install` the built wheel in `dist` or simply run

```
make install
```

# Testing

From the top level, do:

```
make test
```

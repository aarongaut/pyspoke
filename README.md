# pyspoke

A python library supporting pubsub and remote procedure calls on Linux.

# Overview

TBD

# Installation

## Using pip

Install from pip:

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

To install, you can install the built wheel in `dist` using pip or simply run

```
make install
```

# Testing

From the top level, do:

```
make test
```

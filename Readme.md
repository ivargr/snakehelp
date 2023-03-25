

# Snakehelp

A small Python package for making writing Snakemake pipelines easier to write, easier to maintain and with fewer bugs.

## Installation

```
pip install snakehelp
```

## About and usage

Snakemake-pipelines often end up with long wildcards paths, which are hard to read, often copied between rules and hard to debug when something doesn't work:

```snakemake

rule simulate:
    output:
        simulated_file = "data/{param1}/{param2}/{param3}/{param4}/data.csv"

rule some_analysis:
    output:
        simulated_file = "data/{param1}/{param2}/{param3}/{param4}/plot.png"
```

Often the `{param1}/{param2}/..` and so on are copy-pasted and hardcoded into several rules, so that when
you want to add a new parameter or do changes, you have to do the changes many places (and some are often forgotten).

This packages lets you instead define parameters as Python dataclasses, and then use these dataclasses in the Snakemake rules:

```python
from snakehelp import parameters
from typing import Literal

@parameters
class SimulatedData:
    param1: str = "some_default_value"
    param2: float = "3.14"
    param3: Literal["a", "b", "c"] = "a"
    param4: int = 100
    file_ending = ".csv"
```

```snakemake
rule simulation:
    output:
        simulated_file = SimulatedData.path()
```

This looks a bit magic, but the only thing `.path()` does is creating a valid Snakemake wildcard path:

```
'{param1,\\w+}/{param2,[+-]?([0-9]*[.])?[0-9]+}/{param3,a|b|c}/{param4,\\d+}.csv'
```

The addede benefits are:

* You only change the dataclass when you want to change something
* You can add `@parameters` to existing dataclasses to make them compatible with Snakemake rules (as long as the fields are either of classes with @parameters or base types)
* Regexes are automatically generated for you and added to the snakemake path (making errors and ambigious rules less likely)
* Classes can have references to other @parameter-classes, so you can easily create complex structures without duplicating code (or writing many complex paths manually)

## Some useful features

The `path()` method can take fixed parameters, which is useful when defining rules that require some specific value for some parameter:

    print(SimulatedData.path(param1="fixed_value"))
    fixed_value/{param2,[+-]?([0-9]*[.])?[0-9]+}/{param3,a|b|c}/{param4,\d+}.csv

You can nest @parameters-decorated classes:

```python
@parameters
class A:
    param1: int = 1
    param2: int = 2

@parameters
class B:
    a: A
    param3: int = 3
    file_ending = ".csv"

# B.path() will now give you a path that includes the parameters from A:
print(B.path())
# gives: {param1,\d+}/{param2,\d+}/{param3,\d+}.csv
```

You can create objects from Parameter-classes by calling the `from_flat_params()`-method. Here you can specify any parameters, also parameters for nested classes. This makes it easier to tests rules without having to manually write long paths:

```snakemake
rule test_something:
    output:
        B.from_flat_params(param1=100).file_path()
        # gives: '100/2/3.csv'
```

Note that `file_path()` can be called on objects to create an actual path, and `path()` can be called on the classes to generate a wildcard path.


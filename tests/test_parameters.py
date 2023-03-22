import os
import pytest
from snakehelp import parameters
from snakehelp.snakehelp import type_to_regex
from typing import Literal, Union


class WildcardMock:
    """Behaves as a Snakemake wildcards object. Initialize with kwargs."""
    def __init__(self, *args, **kwargs):
        assert len(args) == 0
        self._data = kwargs

    def __getattr__(self, item):
        return self._data[item]

    def items(self):
        return self._data.items()


@parameters
class MyParams:
    seed: int
    name: str
    ratio: float


@parameters
class MyParams2:
    param1: MyParams
    some_other_param: str


@parameters
class MyParams3:
    param1: Literal["test", "test2"]
    param2: str


@parameters
class MyParams4:
    seed: int
    name: str
    file_ending: Literal["file.npz"]


def test_init_parameters():
    assert MyParams.parameters == ["seed", "name", "ratio"]


def test_init_hierarchical_parameters():
    assert MyParams2.parameters == ["seed", "name", "ratio", "some_other_param"]


def test_init_parameters_with_literal():
    assert MyParams3.parameters == ["param1", "param2"]


def test_type_to_regex():
    assert type_to_regex(Union[str, int]) == "\\w+|\\d+"
    assert type_to_regex(Literal["test1", "test2"]) == "test1|test2"
    assert type_to_regex(int) == "\\d+"


def test_as_output():
    assert MyParams4.as_output() == r"{seed,\d+}/{name,\w+}/file.npz"


def test_as_input():
    wildcards = WildcardMock(seed="1", name="test", file_ending="file.npz")
    path = MyParams4.as_input()(wildcards)
    assert path == os.path.sep.join(["1", "test", "file.npz"])


def test_as_partial_input():
    # sometimes the input will only match some of the wildcards, but this should work
    wildcards = WildcardMock(seed="1", name="test", file_ending="file.npz", b="test", c="test2", d="test3")
    path = MyParams4.as_input()(wildcards)
    assert path == os.path.sep.join(["1", "test", "file.npz"])


def test_as_partial_input_end():
    # partial inputs where parameters match at the end
    # not iplemented
    pass


def test_as_input_hierarchical():
    wildcards = WildcardMock(seed="1", name="test", ratio="0.3", some_other_param="test2")
    path = MyParams2.as_input()(wildcards)
    assert path == os.path.sep.join(["1", "test", "0.3", "test2"])


@parameters
class ParamsWithUnion:
    param1: Union[int, str]
    param2: str


def test_union_params():
    assert ParamsWithUnion.parameters == ["param1", "param2"]
    assert ParamsWithUnion.as_output() == r"{param1,\d+|\w+}/{param2,\w+}"


@parameters
class ParamsA:
    a: float
    b: int

@parameters
class ParamsB:
    x: int
    y: int
    z: int

@parameters
class ParamsWithHierarchcicalUnion:
    name: str
    config: Union[ParamsA, ParamsB]
    ending: str


def test_union_and_hierarchical():
    assert ParamsWithHierarchcicalUnion.parameters == ["name", "config", "ending"]
    assert ParamsWithHierarchcicalUnion.as_output() == r"{name,\w+}/{config,.*}/{ending,\w+}"


def test_as_output_with_arguments():
    assert ParamsB.as_output() == r"{x,\d+}/{y,\d+}/{z,\d+}"
    assert ParamsB.as_output(y=10) == r"{x,\d+}/10/{z,\d+}"


def test_minimal_parameters():
    assert MyParams4.parameters == ["seed", "name", "file_ending"]
    assert MyParams4.minimal_parameters == ["seed", "name"]


@parameters
class Child:
    type: str
    ending: Literal["file.txt"]


@parameters
class Parent:
    param1: Child
    param2: int
    ending: Literal["results.txt"]


def test_children_with_literal_that_should_be_ignored():
    assert Parent.as_output() == r"{type,\w+}/{param2,\d+}/results.txt"



@parameters
class Combinatorial:
    param1: int
    param2: int


def test_combinatorial_parameters():
    files = Combinatorial.as_output(param1=[1, 2, 3], param2=[4, 5])
    assert len(files) == 6
    assert set(files) == set(["1/4", "1/5", "2/4", "2/5", "3/4", "3/5"])


if __name__ == "__main__":
    test_type_to_regex()
    #test_union_params()

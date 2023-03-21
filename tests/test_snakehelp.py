import os

import pytest
from snakehelp import Parameters
from snakehelp.snakehelp import type_to_regex
from dataclasses import dataclass
from typing import Literal


class WildcardMock:
    def __init__(self, *args, **kwargs):
        assert len(args) == 0
        self._data = kwargs

    def __getattr__(self, item):
        return self._data[item]

    def items(self):
        return self._data.items()


@dataclass
class MyParams(Parameters):
    seed: int
    name: str
    ratio: float


@dataclass
class MyParams2(Parameters):
    param1: MyParams
    some_other_param: str


@dataclass
class MyParams3(Parameters):
    param1: Literal["test", "test2"]
    param2: str


@dataclass
class MyParams4(Parameters):
    seed: int
    name: str
    file_ending: Literal[".npz"]


def test_init_parameters():
    assert MyParams.parameters == ["seed", "name", "ratio"]


def test_init_hierarchical_parameters():
    assert MyParams2.parameters == ["seed", "name", "ratio", "some_other_param"]


def test_init_parameters_with_literal():
    assert MyParams3.parameters == ["param1", "param2"]


def test_type_to_regex():
    assert type_to_regex(Literal["test1", "test2"]) == "test1|test2"
    assert type_to_regex(int) == "\d+"


def test_as_output():
    assert MyParams4.as_output() == "{seed,\d+}/{name,\w+}/{file_ending,\.npz}"


def test_as_input():
    wildcards = WildcardMock(seed="1", name="test", file_ending=".npz")
    path = MyParams4.as_input(wildcards)
    assert path == os.path.sep.join(["1", "test", ".npz"])


def test_as_input_hierarchical():
    pass

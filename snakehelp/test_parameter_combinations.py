from snakehelp.plotting import ParameterCombinations
from snakehelp.parameters import parameters
from typing import Literal


@parameters
class Config:
    param1: str = "hg38"
    read_length: int = 150
    method_name: str = "bwa"


@parameters
class Precision:
    config: Config = Config()
    file: Literal["precision"] = "precision"
    file_ending = ".txt"


@parameters
class Recall:
    config: Config
    file: Literal["recall"]
    file_ending = ".txt"


def test_parameter_combinations():
    combinations = ParameterCombinations(["read_length", "method_name"], [Precision, Recall])
    objects = combinations.combinations(read_length=[50, 100, 150], method_name=["bwa", "minimap2"])
    assert len(objects) == 12
    assert Precision(config=Config(read_length=100, method_name="bwa")) in objects

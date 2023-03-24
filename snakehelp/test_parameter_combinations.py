from snakehelp.parameter_combinations import ParameterCombinations
from snakehelp.parameters import parameters, result
from typing import Literal
import itertools


@parameters
class Config:
    param1: str = "hg38"
    read_length: int = 150
    method_name: str = "bwa"


@result
class Precision:
    config: Config = Config()


@result
class Recall:
    config: Config


def test_parameter_combinations():
    Precision.from_flat_params(read_length=100, method_name="bwa").store_result(0.5)
    Precision.from_flat_params(read_length=150, method_name="bwa").store_result(0.5)
    Precision.from_flat_params(read_length=100, method_name="minimap2").store_result(0.5)
    Precision.from_flat_params(read_length=150, method_name="minimap2").store_result(0.7)
    Recall.from_flat_params(read_length=100, method_name="bwa").store_result(0.5)
    Recall.from_flat_params(read_length=150, method_name="bwa").store_result(0.5)
    Recall.from_flat_params(read_length=100, method_name="minimap2").store_result(0.5)
    Recall.from_flat_params(read_length=150, method_name="minimap2").store_result(0.7)

    combinations = ParameterCombinations(["read_length", "method_name"], [Precision, Recall])
    objects = combinations.combinations(read_length=[100, 150], method_name=["bwa", "minimap2"])

    assert len(objects) == 4
    assert Precision(config=Config(read_length=100, method_name="bwa")) in itertools.chain(*objects)

    print(combinations.get_files(read_length=[100, 150], method_name=["bwa", "minimap2"]))

    df = combinations.get_results_dataframe(read_length=[100, 150], method_name=["bwa", "minimap2"])
    print(df)


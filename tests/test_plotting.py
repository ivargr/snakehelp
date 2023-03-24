from snakehelp.parameters import parameters
from typing import Literal
from dataclasses import dataclass
from snakehelp.plotting import PlotType
import pytest

@parameters
class Experiment:
    param1: str = "hg38"
    read_length: int = 10
    param3: str = "something"


@parameters
class Method:
    method_name: str = "bwa"
    n_threads: int = 4


@parameters
class MappedReads:
    experiment: Experiment
    method: Method


@parameters
class MappingRecall:
    mapped_reads: MappedReads
    accuracy_type: Literal["recall"]


default_values = {
    "method_name": {
        "value": "bwa",
        "range": ["bwa", "minimap"]
    },
}


def test():
    print(MappingRecall.get_fields())
    plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length")

    print(plot_type.parameter_types())

    with pytest.raises(AssertionError):
        plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length", facet_row="test123")

    plot = plot_type.plot({"method_name": ["bwa", "minimap"], "read_length": [50, 100, 150]})

    parameter_combinations = plot.get_parameter_combinations()
    print(parameter_combinations)
    print(parameter_combinations.combinations())


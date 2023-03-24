from snakehelp.parameters import parameters, result
from typing import Literal
from dataclasses import dataclass
from snakehelp.plotting import PlotType, Plot
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


@result
class MappingRecall:
    mapped_reads: MappedReads


default_values = {
    "method_name": {
        "value": "bwa",
        "range": ["bwa", "minimap"]
    },
}


def test_plot_type():
    plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length")
    with pytest.raises(AssertionError):
        plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length", facet_row="test123")


def test_simple_plot():
    MappingRecall.from_flat_params(method_name="bwa").store_result(0.5)
    MappingRecall.from_flat_params(method_name="minimap").store_result(0.5)

    plot_type = PlotType("bar", x="method_name", y=MappingRecall)
    plot = Plot(plot_type, "testplot", method_name=["bwa", "minimap"])

    # get file names
    print(plot.file_names())

    # generate plot
    plot.plot()




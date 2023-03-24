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


def test_plot_type():
    plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length")

    with pytest.raises(AssertionError):
        plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length", facet_row="test123")

    plot = plot_type.plot({"method_name": ["bwa", "minimap"], "read_length": [50, 100, 150]})
    print(plot.get_data_file_names())

    assert plot.get_data_file_names() == ['data/hg38/50/something/bwa/4/recall.txt',
                                          'data/hg38/50/something/minimap/4/recall.txt', 'data/hg38/100/something/bwa/4/recall.txt',
                                          'data/hg38/100/something/minimap/4/recall.txt', 'data/hg38/150/something/bwa/4/recall.txt',
                                          'data/hg38/150/something/minimap/4/recall.txt']

def test_simple_plot():
    recall1 = MappingRecall(method="bwa").store_result(0.5)
    recall2 = MappingRecall(method="minimap2").store_result(0.7)

    plot_type = PlotType("bar", x="method_name", y=MappingRecall)
    plot = plot_type.plot({"method_name": ["bwa", "minimap"]})
    df = plot.get_results_dataframe()
    print(df)




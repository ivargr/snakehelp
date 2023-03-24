from snakehelp.parameters import parameters
from typing import Literal
from dataclasses import dataclass
from snakehelp.plotting import PlotType

@parameters
class Experiment:
    param1: str
    read_length: int
    param3: str


@parameters
class Method:
    method_name: str
    n_threads: int


@parameters
class MappedReads:
    experiment: Experiment
    method: Method


@parameters
class MappingRecall:
    mapped_reads: MappedReads
    accuracy_type: Literal["recall"]


def test():
    print(MappingRecall.get_fields())
    plot_type = PlotType("bar", x="method_name", y=MappingRecall, facet_col="read_length")
    plot_type.plot()

from dataclasses import dataclass
from typing import Literal
#from .parameter_combinations import ParameterCombinations


@dataclass
class PlotType:
    """
    Defines a plot type. x, y, etc are either strings referring to a field of any @parameter-marked class OR
    a the class of a @result-marked class.
    """
    type: Literal["bar", "line", "scatter"]
    x: str
    y: str
    facet_col: str = None
    facet_row: str = None
    color: str = None
    labels: str = None

    def __post_init__(self):
        self._validate()

    def result_types(self):
        return [t for t in self.dimensions().values() if not isinstance(t, str)]

    def parameter_types(self):
        return [t for t in self.dimensions().values() if isinstance(t, str)]

    def get_fields(self):
        # all result types should have the same fields
        return self.result_types()[0].get_fields()

    def _validate(self):
        # checks that all dimensions are valid and work together
        result_types = self.result_types()
        parameter_types = self.parameter_types()

        assert len(result_types) >= 1, "Plot type is invalid. Dere must be at least one result type (not str)"
        assert len(result_types) + len(parameter_types) >= 2, "Plot must have at least two dimensions"

        # Check that result types are compatible, i.e. have the same fields
        parameters = result_types[0].parameters
        for result_type in result_types[1:]:
            assert result_type.parameters == parameters, \
                f"Type {result_type} has other parameters than {result_types[0]}. " \
                f"{result_type.parameters} != {parameters}. These results cannot be plotted together."

        for parameter in parameter_types:
            assert parameter in parameters, f"Parameter {parameter} is not a valid parameter for generating {result_types[0]}"

    def dimensions(self):
        dim = {
            "x": self.x,
            "y": self.y,
            "facet_col": self.facet_col,
            "facet_row:": self.facet_row,
            "color": self.color,
            "labels": self.labels
        }
        return {name: val for name, val in dim.items() if val is not None}

    def plot(self, data):
        return Plot(self, data)


def at_least_list(element):
    if isinstance(element, list):
        return element
    return [element]


class Plot:
    def __init__(self, plot_type: PlotType, data: dict):
        self._plot_type = plot_type
        self._data = data
        self._validate()
        self._prefix = 'data'

    def _validate(self):
        for name, value in self._data.items():
            assert name in self._plot_type.parameter_types(), \
                f"Specified data parameter {name} is not in the plot type's parameter: {self._plot_types.parameter_types()}"

        for parameter in self._plot_type.parameter_types():
            assert parameter in self._data, f"The plot type {self._plot_type} requires parameter {parameter} to be specified."

    def get_data_file_names(self):
        combinations = self.get_parameter_combinations().combinations()
        file_names = []
        for combination in combinations:
            file_names.append(self._get_result_path(combination))

        return file_names

from dataclasses import dataclass
from typing import Literal
#from .parameter_combinations import ParameterCombinations
from .parameters import ParameterLike
from .hierarchical_results import HierarchicalResults
import os
from typing import List
import itertools


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


class ParameterCombinations:
    def __init__(self, parameter_names, result_types):
        self.parameter_names = parameter_names
        self.result_types = result_types

        assert all([isinstance(t, str) for t in parameter_names]), "All parameter names must be strings"
        assert all([issubclass(t, ParameterLike) for t in result_types]), "All result types must be classes that are ParameterLike: %s" % result_types

    def combinations(self, **data):
        """
        Returns objects of the types in ResultTypes from all combinations of parameters
        """
        # wrap every data value in list and combine them
        data = {key: at_least_list(value) for key, value in data.items()}
        values = data.values()
        combinations = itertools.product(*values)
        combination_dicts = [
            {key: value for key, value in zip(data.keys(), combination)}
            for combination in combinations
        ]

        objects = []
        for result_type in self.result_types:
            for combination in combination_dicts:
                objects.append(result_type.from_flat_params(**combination))

        return objects


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

    def get_parameter_combinations(self):
        # makes a list of all parameter combinations needed for the plot
        # every element in the list can contain:
        #  - one element if it is a fixed parameter
        #  - several elements if is is a variable used in the plot

        # first make combinations with default values
        default_values = [field.default for field in self._plot_type.get_fields()]
        names = [field.name for field in self._plot_type.get_fields()]
        combinations = ParameterCombinations(names, default_values)

        for field in self._plot_type.get_fields():
            if field.name in self._data:
                combinations.set(field.name, self._data[field.name])

        return combinations

    def _get_parameter_path(self, parameters: List[str]) -> str:
        return self._prefix + os.path.sep + os.path.sep.join([str(p) for p in parameters])

    def _get_result_path(self, parameters):
        return self._get_parameter_path(parameters) + ".txt"

    def get_result(self, parameters: List[str]):
        file_name = self._get_result_path(parameters, result)
        return float(open(file_name).read().strip())

    def get_data_file_names(self):
        combinations = self.get_parameter_combinations().combinations()
        file_names = []
        for combination in combinations:
            file_names.append(self._get_result_path(combination))

        return file_names

    def get_results_dataframe(self):
        """
        Gets the results specified by result_names from all the parameter combinations.
        Returns a Pandas Dataframe.
        """
        combinations = self.get_parameter_combinations().combinations()
        results = []

        for combination in combinations:
            row = list(combination[:-1])
            result = self.get_result(combination)
            row.append(result)
            results.append(row)

        return pd.DataFrame(results, columns=parameters._names)

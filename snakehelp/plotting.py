from dataclasses import dataclass
from .parameters import ParameterLike, ResultLike
from typing import Literal
import plotly.express as px
import tabulate

from snakehelp.parameter_combinations import ParameterCombinations


#from .parameter_combinations import ParameterCombinations

plotting_functions = {
    "bar": px.bar,
    "line": px.line,
    "scatter": px.scatter,
    "scat": px.scatter,
    "box": px.box,
    "violin": px.violin
}


@dataclass
class PlotType:
    """
    Defines a plot type. x, y, etc are either strings referring to a field of any @parameter-marked class OR
    a the class of a @result-marked class.
    """
    type: Literal["bar", "line", "scatter", "box", "violin"] = "bar"
    x: str = None
    y: str = None
    facet_col: str = None
    facet_row: str = None
    color: str = None
    labels: str = None
    markers: bool = False
    layout: dict = None
    text: str = None

    def __post_init__(self):
        self._validate()

    @classmethod
    def from_yaml_dict(cls, yaml_dict):
        return cls(**yaml_dict)

    def result_types(self):
        return [t for t in self.dimensions().values() if not isinstance(t, str)]

    def parameter_types(self):
        return [t for t in self.dimensions().values() if isinstance(t, str)]

    def get_fields(self):
        # all result types should have the same fields
        fields = self.result_types()[0].get_fields()
        return fields

    def _validate(self):
        # checks that all dimensions are valid and work together
        result_types = self.result_types()
        parameter_types = self.parameter_types()

        assert len(result_types) >= 1, f"Plot type {self} is invalid. Dere must be at least one result type (not str). Parameters specified: {parameter_types}"
        assert len(result_types) + len(parameter_types) >= 2, "Plot must have at least two dimensions"

        # Check that result types are compatible, i.e. have the same fields
        parameters = result_types[0].parameters
        for result_type in result_types[1:]:
            assert result_type.parameters == parameters, \
                f"Type {result_type} has other parameters than {result_types[0]}. " \
                f"{result_type.parameters} != {parameters}. These results cannot be plotted together."

        for parameter in parameter_types:
            assert parameter in parameters, f"Parameter {parameter} is not a valid parameter for generating {result_types[0]}. Valid parameters are {parameters}"

    def dimensions(self):
        dim = {
            "x": self.x,
            "y": self.y,
            "facet_col": self.facet_col,
            "facet_row": self.facet_row,
            "color": self.color,
            "labels": self.labels
        }
        return {name: val for name, val in dim.items() if val is not None}

    def plot(self, out_base_name, **data):
        return Plot(self, out_base_name, **data)


class Plot:
    def __init__(self, plot_type: PlotType, out_base_name: str, **data):
        self._plot_type = plot_type
        self._out_base_name = out_base_name
        self._data = data
        self._validate()
        self._prefix = 'data'
        self._parameter_combinations = ParameterCombinations(self._plot_type.parameter_types(), self._plot_type.result_types())

    def _validate(self):
        possible_fields = [f.name for f in self._plot_type.get_fields()]
        for name, value in self._data.items():
            assert name in possible_fields, \
                f"Specified data parameter {name} is not in the possible fields that can be specified for generating the data: {possible_fields}"

        for parameter in self._plot_type.parameter_types():
            assert parameter in self._data, f"The plot type {self._plot_type} requires parameter {parameter} to be specified."

    def file_names(self):
        return self._parameter_combinations.get_files(**self._data)

    def plot(self, pretty_names_func=None):
        df = self._parameter_combinations.get_results_dataframe(**self._data)
        df.to_csv(self._out_base_name + ".csv", index=False)

        markdown_table = tabulate.tabulate(df, headers=df.columns, tablefmt="github")
        with open(self._out_base_name + ".txt", "w") as f:
            f.write(markdown_table + "\n")

        title = ""
        if "title" in self._data:
            title = self._data["title"]

        specification = {}
        for dimension, value in self._plot_type.dimensions().items():
            if type(value) != str and issubclass(value, ParameterLike):
                value = value.file_name
            specification[dimension] = value

        if self._plot_type.type != "scatter" and self._plot_type.markers:
            specification["markers"] = True
            assert self._plot_type.labels is not None, "When markers: True, you need to define labels in the plot config"
            specification["text"] = self._plot_type.labels

        assert self._plot_type.type in plotting_functions, "Plot type %s not supported" % self._plot_type.type
        func = plotting_functions[self._plot_type.type]
        fig = func(df, **specification, template="simple_white", title=title)

        # prettier facet titles, names, etc
        if pretty_names_func is not None:
            fig.for_each_annotation(lambda a: a.update(text=pretty_names_func(a.text.split("=")[-1])))
            fig.for_each_xaxis(lambda a: a.update(title_text=pretty_names_func(a.title.text.split("=")[-1])))
            fig.for_each_yaxis(lambda a: a.update(title_text=pretty_names_func(a.title.text.split("=")[-1])))
            fig.for_each_trace(lambda t: t.update(name=pretty_names_func(t.name)))

        if "text" in specification:
            fig.update_traces(textposition="bottom right")

        # fig.update_annotations(font=dict(size=20))
        # fig.update_layout(font=dict(size=20))
        if self._plot_type.layout is not None:
            fig.update_layout(**self._plot_type.layout)

        fig.show()
        fig.write_image(self._out_base_name + ".png")
        fig.write_html(self._out_base_name + ".html")

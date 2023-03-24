from dataclasses import dataclass


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

    def validate(self):
        # checks that all dimensions are valid and work together
        result_types = [t for t in self.dimensions().values() if not isinstance(t, str)]
        parameter_types = [t for t in self.dimensions().values() if isinstance(t, str)]

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
        return {name: val for name, val in dim if val is not None}

    def make_data_list(self, **data):
        pass

    def get_data_objects(self, **data):
        """
        Initializes the required objects with data necessary for producing the plot.
        """
        pass

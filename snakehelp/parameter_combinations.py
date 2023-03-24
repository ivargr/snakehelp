import itertools
import pandas as pd
from snakehelp.parameters import ParameterLike


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
        Returns objects of the types in ResultTypes from all combinations of parameters.

        Returna nested list. Eachs sublist contains all objects for a given set of parameters.
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
        for combination in combination_dicts:
            row = []
            for result_type in self.result_types:
                row.append(result_type.from_flat_params(**combination))
            objects.append(row)

        return objects

    def get_files(self, **data):
        """
        Returns the necessary files for getting the given data.
        """
        combinations = self.combinations(**data)
        files = [o.file_path() for o in itertools.chain(*combinations)]
        return files

    def get_results_dataframe(self, **data):
        """
        Gets the results specified by result_names from all the parameter combinations.
        Returns a Pandas Dataframe.
        """
        combinations = self.combinations(**data)

        data = []

        for combination in combinations:
            row = []
            first_result = combination[0]  # all results should be from the same parameters
            row.extend(first_result.flat_data())
            for result in combination:
                row.append(result.fetch_result())
            data.append(row)

        names = combinations[0][0].__class__.parameters + [result.__class__.__name__ for result in combinations[0]]
        return pd.DataFrame(data, columns=names)

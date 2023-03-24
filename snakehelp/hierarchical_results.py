from typing import List
import os
from pathlib import Path
import logging
import pandas as pd
from shared_memory_wrapper import from_file, to_file
from snakehelp.parameter_combinations import ParameterCombinations


class HierarchicalResults:
    def __init__(self, parameter_names: List[str], result_names: List[str], prefix=""):
        self._prefix = prefix
        self._parameter_names = parameter_names
        self._result_names = result_names

    def __str__(self):
        return "HierarchicalResults with parameters %s and results %s" % (self._parameter_names, self._result_names)

    def get_names(self):
        return self._parameter_names

    def _get_parameter_path(self, parameters: List[str]) -> str:
        return self._prefix + os.path.sep.join([str(p) for p in parameters])

    def _get_result_path(self, parameters, result):
        return self._get_parameter_path(parameters) + os.path.sep + result + ".txt"

    def get_result(self, parameters: List[str], result: str):
        assert len(parameters) <= len(self._parameter_names), "Got more parameters %d than in hieararchy %d" % (len(parameters), len(self._parameter_names))
        file_name = self._get_result_path(parameters, result)
        return from_file(file_name)
        #with open(file_name) as f:
        #    return float(f.read().strip())

    def get_result_file_names(self, parameters: ParameterCombinations, result_names):
        file_names = []
        combinations = parameters.combinations()
        for combination in combinations:
            # when no result names, last element in combination is result name
            if len(result_names) == 0:
                result_names = [combination[-1]]
                combination = combination[:-1]

            for result_name in result_names:
                file_names.append(self._get_result_path(combination, result_name))

        return file_names
        #return [self._prefix + os.path.sep + f for f in file_names]

    def get_results_dataframe(self, parameters: ParameterCombinations, result_names):
        """
        Gets the results specified by result_names from all the parameter combinations.
        Returns a Pandas Dataframe.
        """
        if isinstance(result_names, str):
            result_names = [result_names]

        for n in result_names:
            assert n in self._result_names

        combinations = parameters.combinations()
        results = []

        for combination in combinations:
            row = list(combination)
            for result_name in result_names:
                result = self.get_result(combination, result_name)
                row.append(result)
            results.append(row)

        return pd.DataFrame(results, columns=parameters._names + result_names)

    def store_result(self, parameters, result_name, result_value):
        path = self._get_parameter_path(parameters)
        logging.info("Storing to path %s" % path)
        Path(path).mkdir(parents=True, exist_ok=True)
        to_file(result_value, self._get_result_path(parameters, result_name))
        #with open(self._get_result_path(parameters, result_name), "w") as f:
        #    f.write(str(result_value) + "\n")

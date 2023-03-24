import itertools
from typing import List


class ParameterCombinations:
    def __init__(self, names: List[str], values: List):
        assert isinstance(values, list) and isinstance(names, list)
        self._names = names
        self._values = values

    def __str__(self):
        return str(self._names) + "\n" + str(self._values)

    @classmethod
    def from_path(cls, names, path):
        values = path.split("/")
        # if path is shorter, we allow fewer names
        names = names[0:len(values)]
        assert len(values) == len(names), "Got %d values and %d names" % (len(values), len(names))
        return cls(names, values)

    def set(self, name, value):
        assert name in self._names, "Name %s not in hiearchy %s" % (name, self._names)
        index = self._names.index(name)
        self._values[index] = value

    def combinations(self):
        # wrap strs in list to make product work
        values = [[str(v)] if isinstance(v, (str, int, float)) else v for v in self._values]
        return [list(i) for i in itertools.product(*values)]

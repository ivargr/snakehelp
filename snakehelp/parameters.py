import itertools
import os
from collections import namedtuple
from pathlib import Path
from dataclasses import dataclass, fields
from types import UnionType
from typing import get_origin, Literal, Union, get_args
from snakehelp.snakehelp import classproperty, string_is_valid_type, type_to_regex
from .config import get_data_folder
from shared_memory_wrapper import to_file, from_file
import dataclasses

class ParameterLike:
    pass


class ResultLike:
    pass


def result(base_class):
    class Result(parameters(base_class)):
        """
        A Result is simply a Parameter where the file name is by default the result's class name
        """
        file_name = base_class.__name__
        file_ending = ".txt"

    Result.__name__ = base_class.__name__
    Result.__qualname__ = base_class.__qualname__

    return Result


def parameters(base_class):
    """
    Decorator to make a class into a class that can be used as parameters.
    """
    class Parameters(dataclass(base_class), ParameterLike):
        file_name = base_class.file_name if hasattr(base_class, "file_name") else None
        file_ending = base_class.file_ending if hasattr(base_class, "file_ending") else ""

        @classproperty
        def _field_names(cls):
            return [field.name for field in fields(cls)]

        @classmethod
        def field(cls, name):
            """
            Returns the field with given name if it exists
            """
            matches = [f for f in fields(cls) if f.name == name]
            assert len(matches) == 1, f"Tried to access field {name} on {cls}. Does not exist."
            return matches[0]

        @classmethod
        def get_fields(cls, minimal=False, minimal_children=False):
            """
            Returns a list of tuples (field_name, field_type)

            If minimal is True, Literal types with only one possible value are ignored, i.e. only
            arguments that are necessary for uniquely representing the object are included.

            minimal_children specifies only whether children should be minimal.
            """
            field_tuple = namedtuple("Field", ["name", "type", "default"])
            out = []
            for field in fields(cls):
                if minimal and get_origin(field.type) == Literal and len(get_args(field.type)) == 1:
                    continue

                if field.type in (int, str, float):
                    out.append(field_tuple(field.name, field.type, field.default))
                elif get_origin(field.type) in (Literal, Union, UnionType):
                    default = field.default
                    if get_origin(field.type) == Literal and len(get_args(field.type)) == 1:
                        default = get_args(field.type)[0]
                    out.append(field_tuple(field.name, field.type, default))
                else:
                    assert hasattr(field.type, "get_fields"), "Field type %s is not valid. " \
                                                              "Must be a base type or a class decorated with @parameters" % field.type
                    out.extend(field.type.get_fields(minimal=minimal_children, minimal_children=minimal_children))

            return out

        @classproperty
        def parameters(cls):
            """
            Returns a list of names of parameters.
            """
            return [field.name for field in cls.get_fields()]

        @classproperty
        def minimal_parameters(cls):
            """
            Returns a list of the minimum set of parameters needed to uniquely represent
            this objeckt, meaning that Literal parameters with only one possible value are ignored.
            """
            return [field.name for field in cls.get_fields(minimal=True)]

        @classmethod
        def as_input(cls):
            """
            Returns an input-function that can be used by Snakemake.
            """

            def func(wildcards):
                assert hasattr(wildcards,
                               "items"), "As input can only be called with a dictlike object with an items() method"

                fields = cls.get_fields()
                # create a path from the wildcards and the parameters
                # can maybe be done by just calling output with these wildcards.
                return cls.as_output(**{name: t for name, t in wildcards.items() if name in cls.parameters})

                path = []

                """
                for i, (name, value) in enumerate(wildcards.items()):
                    if i >= len(fields):
                        break
                    assert name == fields[i].name, f"Parsing {cls}. Invalid at {i}, name: {name}, expected {fields[i].name}"
                    assert string_is_valid_type(value, fields[i].type), f"{value} is not a valid as type {fields[i].type}"
                    path.append(value)

                return os.path.sep.join(path)
                """

            return func

        @classmethod
        def path(cls, **kwargs):
            return cls.as_output(**kwargs)

        def data(self):
            data = []
            for field in fields(self.__class__):
                data.append(getattr(self, field.name))
            return data

        def flat_data(self):
            data = []
            for element in self.data():
                if isinstance(element, ParameterLike):
                    data.extend(element.flat_data())
                else:
                    assert isinstance(element, (int, str, float)), "Invalid type %s" % type(element)
                    data.append(element)
            return data

        def file_path(self):
            file_name = ""
            if self.file_name is not None:
                file_name = os.path.sep + self.file_name
            return get_data_folder() + os.path.sep.join(map(str, self.flat_data())) + file_name + self.file_ending

        def store_result(self, result):
            file = self.file_path()
            path = os.path.sep.join(file.split(os.path.sep)[:-1])
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(file, "w") as f:
                f.write(str(result))
            #to_file(result, path)

        def fetch_result(self):
            with open(self.file_path()) as f:
                data = f.read().strip()
                try:
                    data = float(data)
                except ValueError:
                    data = data

                return data
            #return from_file(self.file_path())

        @classmethod
        def from_flat_params(cls, **params):
            """
            Creates an object from keyword arguments.
            Keyword arguments may specify a parameter in a subobject.
            """
            data = {}
            for field in fields(cls):
                if hasattr(field.type, "get_fields"):
                    data[field.name] = field.type.from_flat_params(**params)
                else:
                    if field.name in params:
                        data[field.name] = params[field.name]
                    else:
                        assert not isinstance(field.default, dataclasses._MISSING_TYPE), \
                            f"Field {field.name} in class {cls} does not have a default value " \
                            f"set and no value was provided for it when calling from_flat_params."
                        data[field.name] = field.default

            return cls(**data)

        @classmethod
        def as_output(cls, **kwargs):
            """
            Returns a valid Snakemake wildcard string with regex so force types

            Keyword arguments can be specified to fix certain variables to values.
            """
            names_with_regexes = []
            if get_data_folder() != "":
                names_with_regexes.append([get_data_folder().replace(os.path.sep, "")])

            for name in kwargs:
                if name != "file_ending" and name != "file_name":
                    assert name in cls.parameters, "Trying to force a field '%s' which is not among the available fields which are %s" % (name, cls.parameters)


            for field in cls.get_fields(minimal_children=False):
                if field.name in kwargs:
                    # value has been specified. If this is a list, we want to return multiple possible values
                    forced_values = kwargs[field.name]
                    if not isinstance(forced_values, list):
                        forced_values = [forced_values]

                    for forced_value in forced_values:
                        assert string_is_valid_type(forced_value, field.type), \
                            f"Trying to set field {field.name} to value {forced_value}, " \
                            f"but this is not compatible with the field type {field.type}."

                    names_with_regexes.append([str(v) for v in forced_values])
                else:
                    if get_origin(field.type) == Literal and len(get_args(field.type)) == 1:
                        # literal types enforces a single value, should not be wildcards
                        names_with_regexes.append([get_args(field.type)[0]])
                    else:
                        names_with_regexes.append(["{" + field.name + "," + type_to_regex(field.type) + "}"])

            # file name
            file_name = cls.file_name
            if file_name is not None or "file_name" in kwargs:
                if "file_name" in kwargs:
                    file_name = kwargs["file_name"]

                if not isinstance(file_name, list):
                    file_name = [file_name]

                names_with_regexes.append(file_name)

            # file ending can be overwritten
            file_ending = cls.file_ending
            if "file_ending" in kwargs:
                file_ending = kwargs["file_ending"]

            if not isinstance(file_ending, list):
                file_ending = [file_ending]

            names_with_regexes.append(file_ending)
            out_files = itertools.product(*names_with_regexes)

            try:
                # join everything expect file ending (last element) with path sep
                out_files = [os.path.sep.join(out_file[:-1]) + out_file[-1] for out_file in out_files]
            except TypeError:
                print(out_files)
                raise

            if len(out_files) == 1:
                return out_files[0]
            else:
                return out_files

            #return os.path.sep.join(names_with_regexes)

    Parameters.__name__ = base_class.__name__
    Parameters.__qualname__ = base_class.__qualname__

    return Parameters


def get_path_from_flat_parameter_list(parameters):
    pass


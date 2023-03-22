import itertools
import os
from collections import namedtuple
from dataclasses import dataclass, fields
from types import UnionType
from typing import get_origin, Literal, Union, get_args
from snakehelp.snakehelp import classproperty, string_is_valid_type, type_to_regex
from .config import get_data_folder


def parameters(base_class):
    """
    Decorator to make a class into a class that can be used as parameters.
    """
    class Parameters(dataclass(base_class)):
        @classproperty
        def _field_names(cls):
            return [field.name for field in fields(cls)]

        @classmethod
        def get_fields(cls, minimal=False, minimal_children=False):
            """
            Returns a list of tuples (field_name, field_type)

            If minimal is True, Literal types with only one possible value are ignored, i.e. only
            arguments that are necessary for uniquely representing the object are included.

            minimal_children specifies only whether children should be minimal.
            """
            field_tuple = namedtuple("Field", ["name", "type"])
            out = []
            for field in fields(cls):
                if minimal and get_origin(field.type) == Literal and len(get_args(field.type)) == 1:
                    continue

                if field.type in (int, str, float):
                    out.append(field_tuple(field.name, field.type))
                elif get_origin(field.type) in (Literal, Union, UnionType):
                    out.append(field_tuple(field.name, field.type))
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
        def as_output(cls, **kwargs):
            """
            Returns a valid Snakemake wildcard string with regex so force types

            Keyword arguments can be specified to fix certain variables to values.
            """
            names_with_regexes = []
            if get_data_folder() != "":
                names_with_regexes.append(get_data_folder())

            for name in kwargs:
                assert name in cls.parameters, "Trying to force a field '%s' which is not among the available fields which are %s" % (name, cls.parameters)


            for field in cls.get_fields(minimal_children=True):
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

            out_files = itertools.product(*names_with_regexes)
            out_files = [os.path.sep.join(out_file) for out_file in out_files]

            if len(out_files) == 1:
                return out_files[0]
            else:
                return out_files

            #return os.path.sep.join(names_with_regexes)

    Parameters.__name__ = base_class.__name__
    Parameters.__qualname__ = base_class.__qualname__

    return Parameters

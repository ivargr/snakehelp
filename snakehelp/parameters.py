import os
from collections import namedtuple
from dataclasses import dataclass, fields
from typing import get_origin, Literal
from snakehelp.snakehelp import classproperty, string_is_valid_type, type_to_regex


def parameters(base_class):
    """
    Decorator to make a class into a class that can be used as parameters.
    """
    class Parameters(dataclass(base_class)):
        @classproperty
        def _field_names(cls):
            return [field.name for field in fields(cls)]

        @classmethod
        def get_fields(cls):
            """
            Returns a list of tuples (field_name, field_type)
            """
            field_tuple = namedtuple("Field", ["name", "type"])
            out = []
            for field in fields(cls):
                if field.type in (int, str, float):
                    out.append(field_tuple(field.name, field.type))
                elif get_origin(field.type) == Literal:
                    out.append(field_tuple(field.name, field.type))
                else:
                    assert hasattr(field.type, "get_fields"), "Field type %s is not valid. " \
                                                              "Must be a base type or a class decorated with @parameters" % field.type
                    out.extend(field.type.get_fields())

            return out

        @classproperty
        def parameters(cls):
            """
            Returns a list of names of parameters.
            """
            return [field.name for field in cls.get_fields()]

        @classmethod
        def as_input(cls, wildcards):
            """
            Tries to return a valid snakemake input-file by using the given wildcards (as many as possible, starting from the first).

            If fields are Union-types, there may be multible possible paths that can be created. This method checks that there
            is no ambiguity, and raises an Exception if there is.
            """
            assert hasattr(wildcards,
                           "items"), "As input can only be called with a dictlike object with an items() method"

            fields = cls.get_fields()

            path = []

            for i, (name, value) in enumerate(wildcards.items()):
                assert name == fields[i].name
                assert string_is_valid_type(value, fields[i].type)
                path.append(value)

            return os.path.sep.join(path)

        @classmethod
        def as_output(cls):
            """
            Returns a valid Snakemake wildcard string with regex so force types
            """
            names_with_regexes = ["{" + field.name + "," + type_to_regex(field.type) + "}" for field in
                                  cls.get_fields()]
            return os.path.sep.join(names_with_regexes)


    Parameters.__name__ = base_class.__name__
    Parameters.__qualname__ = base_class.__qualname__
    return Parameters

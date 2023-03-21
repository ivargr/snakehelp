import os
from collections import namedtuple
from dataclasses import dataclass, fields
from typing import Union, Literal, get_origin, get_args
import re


class ClassProperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


classproperty = ClassProperty


@dataclass
class Parameters:
    """
    Class that should be subclassed when defining custom parameters.
    """

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
                assert issubclass(field.type, Parameters), "Field type %s is not valid" % field.type
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
        assert hasattr(wildcards, "items"), "As input can only be called with a dictlike object with an items() method"

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
        names_with_regexes = ["{" + field.name + "," + type_to_regex(field.type) + "}" for field in cls.get_fields()]
        return os.path.sep.join(names_with_regexes)


def type_to_regex(type):
    if type == int:
        return "\d+"
    elif type == float:
        return "[+-]?([0-9]*[.])?[0-9]+"
    elif type == str:
        return "\w+"
    elif get_origin(type) == Literal:
        return "|".join([re.escape(arg) for arg in get_args(type)])

    raise Exception("Invalid type %s" % type)


def string_is_valid_type(string, type):
    if type == str:
        return True
    elif type == int:
        return string.isdigit()
    elif type == float:
        try:
            float(string)
            return True
        except ValueError:
            return False
    elif get_origin(type) == Literal:
        return string in get_args(type)
    else:
        raise Exception("Type %s not implemented" % type)

import os
from collections import namedtuple
from dataclasses import dataclass, fields
#from types import UnionType
from typing import Literal, get_origin, get_args, Union
import re


class ClassProperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


classproperty = ClassProperty

def is_parameter_type(object):
    return hasattr(object, "get_fields")


def is_base_type(type):
    return type in (str, float, bool, int)


def type_to_regex(type):
    if type == int:
        return "\\d+"
    if type == float:
        return "[+-]?([0-9]*[.])?[0-9]+"
    if type == str:
        return "\\w+"
    if get_origin(type) == Literal:
        return "|".join([re.escape(str(arg)) for arg in get_args(type)])
    elif get_origin(type) in (Union,):
        if all(is_base_type(t) for t in get_args(type)):
            # all types are base type, we can give a regex for each
            return "|".join([type_to_regex(t) for t in get_args(type)])
        else:
            # There is one or more objects, we can have anything
            return ".*"
    elif is_parameter_type(type):
        # normal parameter-objects are strings in the path
        return "\w+"

    raise Exception("Invalid type %s" % type)


def string_is_valid_type(string, type):
    if type == str:
        return True
    elif type == int:
        return isinstance(string, int) or string.isdigit()
    elif type == float:
        try:
            float(string)
            return True
        except ValueError:
            return False
    elif get_origin(type) == Literal:
        return string in get_args(type)
    elif get_origin(type) in [Union]:
        return any((string_is_valid_type(string, t) for t in get_args(type)))
    elif is_parameter_type(type):
        return isinstance(string, str)
    else:
        raise Exception("Type %s not implemented" % type)



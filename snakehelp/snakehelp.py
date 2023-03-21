import os
from collections import namedtuple
from dataclasses import dataclass, fields
from typing import Literal, get_origin, get_args
import re


class ClassProperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


classproperty = ClassProperty


def type_to_regex(type):
    if type == int:
        return "\\d+"
    elif type == float:
        return "[+-]?([0-9]*[.])?[0-9]+"
    elif type == str:
        return "\\w+"
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



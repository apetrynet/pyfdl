import json

from typing import IO, Union

from .base import (
    Base,
    DimensionsFloat,
    DimensionsInt,
    Point,
    RoundStrategy,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION,
    TypedList
)
from .header import Header
from .framing_intent import FramingIntent
from .framing_decision import FramingDecision
from .canvas import Canvas
from .context import Context
from .canvas_template import CanvasTemplate
from .pyfdl import FDL
from .errors import FDLError

__all__ = [
    'Base',
    'Canvas',
    'CanvasTemplate',
    'Context',
    'DimensionsFloat',
    'DimensionsInt',
    'FDL',
    'FDLError',
    'FDL_SCHEMA_MAJOR',
    'FDL_SCHEMA_MINOR',
    'FDL_SCHEMA_VERSION',
    'FramingDecision',
    'FramingIntent',
    'Header',
    'load',
    'loads',
    'Point',
    'RoundStrategy',
    'TypedList'
]

__version__ = "0.1.0"


def load(fp: IO, validate: bool = True) -> FDL:
    raw = fp.read()
    return loads(raw, validate=validate)


def loads(s: str, validate: bool = True) -> FDL:
    fdl = FDL.from_dict(json.loads(s))

    if validate:
        fdl.validate()

    return fdl


def dump(obj: FDL, fp: IO, validate: bool = True, indent: Union[int, None] = 2):
    fp.write(dumps(obj, validate=validate, indent=indent))


def dumps(obj: FDL, validate: bool = True, indent: Union[int, None] = 2) -> str:
    if validate:
        obj.validate()

    return json.dumps(obj.to_dict(), indent=indent, sort_keys=False)

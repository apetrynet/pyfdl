import json

from typing import IO

from .base import (
    Base,
    DimensionsFloat,
    DimensionsInt,
    Point,
    RoundStrategy,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION
)
from .header import Header
from .fraaming_intent import FramingIntent
from .framing_decision import FramingDecision
from .canvas import Canvas
from .context import Context
from .canvas_template import CanvasTemplate
from .fdl import FDL
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
    'RoundStrategy'
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


def dump(obj: FDL, fp: IO, validate: bool = True):
    fp.write(dumps(obj, validate=validate))


def dumps(obj: FDL, validate: bool = True) -> str:
    if validate:
        obj.validate()

    return json.dumps(obj.to_dict(), indent=2, sort_keys=False)

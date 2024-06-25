import json

from typing import IO, Union

from .base import (
    Base,
    DimensionsFloat,
    DimensionsInt,
    Point,
    RoundStrategy,
    DEFAULT_ROUNDING_STRATEGY,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION,
    TypedCollection
)
from .header import Header
from .framing_intent import FramingIntent
from .framing_decision import FramingDecision
from .canvas import Canvas
from .context import Context
from .canvas_template import CanvasTemplate
from .pyfdl import FDL
from .errors import FDLError, FDLValidationError

__all__ = [
    'Base',
    'Canvas',
    'CanvasTemplate',
    'Context',
    'DEFAULT_ROUNDING_STRATEGY',
    'DimensionsFloat',
    'DimensionsInt',
    'FDL',
    'FDLError',
    'FDLValidationError',
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
    'TypedCollection'
]

__version__ = "0.1.0"


def load(fp: IO, validate: bool = True) -> FDL:
    """
    Load an FDL from a file.

    Args:
        fp: file pointer
        validate: validate incoming json with jsonschema

    Raises:
        jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec

    Returns:
        FDL:
    """
    raw = fp.read()
    return loads(raw, validate=validate)


def loads(s: str, validate: bool = True) -> FDL:
    """Load an FDL from string.

    Args:
        s: string representation of an FDL
        validate: validate incoming json with jsonschema

    Returns:
        FDL:

    """
    fdl = FDL.from_dict(json.loads(s))

    if validate:
        fdl.validate()

    return fdl


def dump(obj: FDL, fp: IO, validate: bool = True, indent: Union[int, None] = 2):
    """Dump an FDL to a file.

    Args:
        obj: object to serialize
        fp: file pointer
        validate: validate outgoing json with jsonschema
        indent: amount of spaces
    """
    fp.write(dumps(obj, validate=validate, indent=indent))


def dumps(obj: FDL, validate: bool = True, indent: Union[int, None] = 2) -> str:
    """Dump an FDL to string

    Args:
        obj: object to serialize
        validate: validate outgoing json with jsonschema
        indent: amount of spaces

    Returns:
        string: representation of the resulting json
    """
    if validate:
        obj.validate()

    return json.dumps(obj.to_dict(), indent=indent, sort_keys=False)

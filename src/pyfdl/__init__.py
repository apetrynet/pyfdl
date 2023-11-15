import os
import json
import jsonschema

from typing import IO
from pathlib import Path

from .classes import (
    FDL,
    Header,
    FramingIntent,
    FramingDecision,
    Canvas,
    Context,
    CanvasTemplate,
    Dimensions,
    Point,
    RoundStrategy,
    FDL_MAJOR,
    FDL_MINOR,
    FDL_VERSION
)
from .errors import FDLError

__all__ = [
    'FDL',
    'Header',
    'FramingIntent',
    'FramingDecision',
    'Canvas',
    'Context',
    'CanvasTemplate',
    'Dimensions',
    'Point',
    'RoundStrategy',
    'FDL_MAJOR',
    'FDL_MINOR',
    'FDL_VERSION',
    'load'
]


def load_schema(path: Path) -> dict:
    with path.open('rb') as fp:
        schema = json.load(fp)

    return schema


def load(fp: IO, validate: bool = False) -> FDL:
    raw = json.load(fp)
    if validate:
        if not os.getenv('FDL_SCHEMA', None):
            raise FDLError("No FDL_SCHEMA environment variable set. Please provide a path to the current FDL schema.")

        schema = load_schema(Path(os.getenv('FDL_SCHEMA')))
        jsonschema.validate(raw, schema)

    fdl = FDL.from_object(raw)

    return fdl

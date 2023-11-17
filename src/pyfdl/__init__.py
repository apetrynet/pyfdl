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
    DimensionsFloat,
    DimensionsInt,
    PointFloat,
    RoundStrategy,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION
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
    'DimensionsFloat',
    'DimensionsInt',
    'PointFloat',
    'RoundStrategy',
    'FDL_SCHEMA_MAJOR',
    'FDL_SCHEMA_MINOR',
    'FDL_SCHEMA_VERSION',
    'load'
]

__version__ = "0.1.0"

FDL_SCHEMA_FILE = Path(__file__).parent.joinpath(
    f'schema',
    f'v{FDL_SCHEMA_MAJOR}.{FDL_SCHEMA_MINOR}',
    f'Python_FDL_Checker'
)


def load_schema(path: Path) -> dict:
    with path.open('rb') as fp:
        schema = json.load(fp)

    return schema


def load(fp: IO, validate: bool = False) -> FDL:
    raw = fp.read()
    return loads(raw, validate=validate)


def loads(string: str, validate: bool = False) -> FDL:
    raw = json.loads(string)
    if validate:
        schema = load_schema(FDL_SCHEMA_FILE)
        jsonschema.validate(raw, schema)

    fdl = FDL.from_object(raw)

    return fdl

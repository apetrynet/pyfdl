from .config import set_rounding, DEFAULT_ROUNDING_STRATEGY
from .canvas import Canvas as Canvas
from .canvastemplate import CanvasTemplate as CanvasTemplate
from .common import (
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION,
    PATH_HIERARCHY,
    TypedCollection,
)
from .clipid import ClipID as ClipID
from .context import Context as Context
from .errors import FDLError, FDLValidationError
from .fdl import FDL as FDL
from .fdlchecker import FDLValidator, validate_fdl
from .framingdecision import FramingDecision as FramingDecision
from .framingintent import FramingIntent as FramingIntent
from .handlers import read_from_file, read_from_string, write_to_file, write_to_string
from .header import Header as Header, Version as Version
from .rounding import RoundStrategy as RoundStrategy, fdl_round
from .common import find_by_attr, find_by_id, find_by_label
from .canvastemplate import (
    Geometry,
    TransformationResult,
    calculate_scale_factor,
    get_anchor_from_path,
    get_dimensions_from_path,
)
from .types import DimensionsFloat, DimensionsInt, PointFloat

# Backward compatibility alias
CanvasTemplateRound = RoundStrategy

__all__ = [
    "Canvas",
    "CanvasTemplate",
    "CanvasTemplateRound",
    "ClipID",
    "Context",
    "DEFAULT_ROUNDING_STRATEGY",
    "DimensionsFloat",
    "DimensionsInt",
    "FDL",
    "FDLError",
    "FDLValidationError",
    "FDLValidator",
    "FDL_SCHEMA_MAJOR",
    "FDL_SCHEMA_MINOR",
    "FDL_SCHEMA_VERSION",
    "FramingDecision",
    "FramingIntent",
    "Geometry",
    "Header",
    "PATH_HIERARCHY",
    "PointFloat",
    "RoundStrategy",
    "TransformationResult",
    "TypedCollection",
    "Version",
    "calculate_scale_factor",
    "config",
    "fdl_round",
    "find_by_attr",
    "find_by_id",
    "find_by_label",
    "get_anchor_from_path",
    "get_dimensions_from_path",
    "read_from_file",
    "read_from_string",
    "rounding",
    "set_rounding",
    "validate_fdl",
    "write_to_file",
    "write_to_string",
]

__version__ = "0.1.0.dev0"

set_rounding(DEFAULT_ROUNDING_STRATEGY)

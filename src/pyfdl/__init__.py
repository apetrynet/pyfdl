from .config import set_rounding, DEFAULT_ROUNDING_STRATEGY
from .canvas import Canvas as Canvas
from .canvastemplate import CanvasTemplate as CanvasTemplate
from .common import (
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION,
    Dimensions,
    Point,
    TypedCollection,
)
from .clipid import ClipID
from .context import Context
from .errors import FDLError, FDLValidationError
from .fdl import FDL
from .framingdecision import FramingDecision
from .framingintent import FramingIntent
from .handlers import read_from_file, read_from_string, write_to_file, write_to_string
from .header import Header
from .rounding import RoundStrategy

__all__ = [
    "Canvas",
    "CanvasTemplate",
    "ClipID",
    "Context",
    "config",
    "Dimensions",
    "FDL",
    "FDLError",
    "FDLValidationError",
    "FDL_SCHEMA_MAJOR",
    "FDL_SCHEMA_MINOR",
    "FDL_SCHEMA_VERSION",
    "FramingDecision",
    "FramingIntent",
    "Header",
    "Point",
    "read_from_file",
    "read_from_string",
    "rounding",
    "RoundStrategy",
    "TypedCollection",
    "write_to_file",
    "write_to_string",
]

__version__ = "0.1.0.dev0"

config.set_rounding(config.DEFAULT_ROUNDING_STRATEGY)

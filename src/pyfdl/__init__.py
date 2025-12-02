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
from .clipid import ClipID as ClipID
from .context import Context as Context
from .errors import FDLError, FDLValidationError
from .fdl import FDL as FDL
from .framingdecision import FramingDecision as FramingDecision
from .framingintent import FramingIntent as FramingIntent
from .handlers import read_from_file, read_from_string, write_to_file, write_to_string
from .header import Header as Header
from .rounding import RoundStrategy as RoundStrategy

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

set_rounding(DEFAULT_ROUNDING_STRATEGY)

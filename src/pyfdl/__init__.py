from .canvas import Canvas as Canvas
from .canvas_template import CanvasTemplate as CanvasTemplate
from .common import (
    DEFAULT_ROUNDING_STRATEGY,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION,
    NO_ROUNDING,
    Base,
    Dimensions,
    Point,
    RoundStrategy,
    TypedCollection,
)
from .context import Context
from .errors import FDLError, FDLValidationError
from .fdl import FDL
from .framing_decision import FramingDecision
from .framing_intent import FramingIntent
from .handlers import read_from_file, read_from_string, write_to_file, write_to_string
from .header import Header
from .rounding import set_rounding_strategy, get_rounding_strategy


__all__ = [
    "Base",
    "Canvas",
    "CanvasTemplate",
    "Context",
    "DEFAULT_ROUNDING_STRATEGY",
    "Dimensions",
    "FDL",
    "FDLError",
    "FDLValidationError",
    "FDL_SCHEMA_MAJOR",
    "FDL_SCHEMA_MINOR",
    "FDL_SCHEMA_VERSION",
    "FramingDecision",
    "FramingIntent",
    "get_rounding_strategy",
    "Header",
    "NO_ROUNDING",
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

set_rounding_strategy(DEFAULT_ROUNDING_STRATEGY)

import tempfile
from pathlib import Path

import pytest

import pyfdl
import pyfdl.config
import pyfdl.rounding


@pytest.fixture(autouse=True)
def consistent_rounding():
    pyfdl.config.set_rounding(pyfdl.config.DEFAULT_ROUNDING_STRATEGY)


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    yield

    files = list(Path(tempfile.gettempdir()).glob("*.fdl"))
    files += Path(tempfile.gettempdir()).glob("*.yml")
    # Remove temp files
    for file in files:
        file.unlink(missing_ok=True)


@pytest.fixture
def sample_dimensions_float():
    return pyfdl.Dimensions(width=25.92, height=21.60)


@pytest.fixture
def sample_dimensions_int():
    return pyfdl.Dimensions(width=16, height=9, dtype=int)


@pytest.fixture
def sample_framing_intent_obj():
    framing_intent = pyfdl.FramingIntent(
        label="1.78-1 Framing",
        id="FDLSMP03",
        aspect_ratio=pyfdl.Dimensions[int](width=16, height=9),
        protection=0.088,
    )

    return framing_intent


@pytest.fixture
def sample_framing_decision_obj():
    fd = pyfdl.FramingDecision(
        label="1.78-1 Framing",
        id="20220310-FDLSMP03",
        framing_intent_id="FDLSMP03",
        dimensions=pyfdl.Dimensions(width=4728, height=3456),
        anchor_point=pyfdl.Point(x=228, y=432),
        protection_dimensions=pyfdl.Dimensions(width=5184, height=3790),
        protection_anchor_point=pyfdl.Point(x=0, y=265),
    )
    return fd


@pytest.fixture
def sample_canvas_obj():
    canvas = pyfdl.Canvas(
        label="Open Gate RAW",
        id="20220310",
        source_canvas_id="20220310",
        dimensions=pyfdl.Dimensions(width=5184, height=4320),
        effective_dimensions=pyfdl.Dimensions(width=5184, height=4320),
        effective_anchor_point=pyfdl.Point(x=0, y=0),
        photosite_dimensions=pyfdl.Dimensions(width=5184, height=4320),
        physical_dimensions=pyfdl.Dimensions(width=25.92, height=21.60),
        anamorphic_squeeze=1.30,
        framing_decisions=pyfdl.TypedCollection[pyfdl.FramingDecision](),
    )

    return canvas


@pytest.fixture
def sample_context_obj():
    ctx = pyfdl.Context(
        label="PanavisionDXL2",
        context_creator="ASC FDL Committee",
        canvases=pyfdl.TypedCollection[pyfdl.Canvas]()
    )

    return ctx


@pytest.fixture
def sample_canvas_template_obj():
    canvas_template = pyfdl.CanvasTemplate(
        label="VFX Pull",
        id="VX220310",
        target_dimensions=pyfdl.Dimensions[int](width=4096, height=2304),
        target_anamorphic_squeeze=1.00,
        fit_source="framing_decision.dimensions",
        fit_method="width",
        alignment_method_vertical="center",
        alignment_method_horizontal="center",
        preserve_from_source_canvas="canvas.dimensions",
        round=pyfdl.rounding.RoundStrategy(even="even", mode="up"),
    )
    return canvas_template


@pytest.fixture
def sample_rounding_strategy_obj():
    return pyfdl.rounding.RoundStrategy(even="even", mode="up")


@pytest.fixture
def simple_handler():
    class SimpleHandler:
        def __init__(self):
            self.name = "simple"
            self.suffixes = [".ext"]

        def read_from_string(self, s: str) -> str:
            return s

    return SimpleHandler

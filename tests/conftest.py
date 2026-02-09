import tempfile
from pathlib import Path

import pytest

import fdl
import fdl.config
import fdl.rounding


@pytest.fixture(autouse=True)
def consistent_rounding():
    fdl.config.set_rounding(fdl.config.DEFAULT_ROUNDING_STRATEGY)


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
    return fdl.DimensionsFloat(width=25.92, height=21.60)


@pytest.fixture
def sample_dimensions_int():
    return fdl.DimensionsInt(width=16, height=9)


@pytest.fixture
def sample_framing_intent_obj():
    framing_intent = fdl.FramingIntent(
        label="1.78-1 Framing",
        id="FDLSMP03",
        aspect_ratio=fdl.DimensionsInt(width=16, height=9),
        protection=0.088,
    )

    return framing_intent


@pytest.fixture
def sample_framing_decision_obj():
    fd = fdl.FramingDecision(
        label="1.78-1 Framing",
        id="20220310-FDLSMP03",
        framing_intent_id="FDLSMP03",
        dimensions=fdl.DimensionsFloat(width=4728, height=3456),
        anchor_point=fdl.PointFloat(x=228, y=432),
        protection_dimensions=fdl.DimensionsFloat(width=5184, height=3790),
        protection_anchor_point=fdl.PointFloat(x=0, y=265),
    )
    return fd


@pytest.fixture
def sample_canvas_obj():
    canvas = fdl.Canvas(
        label="Open Gate RAW",
        id="20220310",
        source_canvas_id="20220310",
        dimensions=fdl.DimensionsInt(width=5184, height=4320),
        effective_dimensions=fdl.DimensionsInt(width=5184, height=4320),
        effective_anchor_point=fdl.PointFloat(x=0, y=0),
        photosite_dimensions=fdl.DimensionsInt(width=5184, height=4320),
        physical_dimensions=fdl.DimensionsFloat(width=25.92, height=21.60),
        anamorphic_squeeze=1.30,
        framing_decisions=fdl.TypedCollection[fdl.FramingDecision](),
    )

    return canvas


@pytest.fixture
def sample_context_obj():
    ctx = fdl.Context(
        label="PanavisionDXL2",
        context_creator="ASC FDL Committee",
        canvases=fdl.TypedCollection[fdl.Canvas]()
    )

    return ctx


@pytest.fixture
def sample_canvas_template_obj():
    canvas_template = fdl.CanvasTemplate(
        label="VFX Pull",
        id="VX220310",
        target_dimensions=fdl.DimensionsInt(width=4096, height=2304),
        target_anamorphic_squeeze=1.00,
        fit_source="framing_decision.dimensions",
        fit_method="width",
        alignment_method_vertical="center",
        alignment_method_horizontal="center",
        preserve_from_source_canvas="canvas.dimensions",
        round=fdl.rounding.RoundStrategy(even="even", mode="up"),
    )
    return canvas_template


@pytest.fixture
def sample_rounding_strategy_obj():
    return fdl.rounding.RoundStrategy(even="even", mode="up")


@pytest.fixture
def simple_handler():
    class SimpleHandler:
        def __init__(self):
            self.name = "simple"
            self.suffixes = [".ext"]

        def read_from_string(self, s: str) -> str:
            return s

    return SimpleHandler

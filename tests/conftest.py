import pytest
import pyfdl


@pytest.fixture
def base_subclass():
    class BaseSubclass(pyfdl.Base):
        # Holds a list of known attributes
        attributes = ["id", "string", "point", "dimensions", "collection", "round"]
        # Maps attribute names that clash with reserved builtin functions to safe alternatives (id -> id_)
        kwarg_map = {"id": "id_", "round": "round_"}
        # Map keys to custom classes
        object_map = {
            "point": pyfdl.Point,
            "dimensions": pyfdl.Dimensions,
            "collection": pyfdl.FramingIntent,
            "round": pyfdl.RoundStrategy
        }
        # List of required attributes
        required = ["id", "string.point"]
        # Default values for attributes
        defaults = {"id": "my_id"}

        def __init__(
                self,
                id_=None,
                string=None,
                point=None,
                dimensions=None,
                collection=None,
                round_=None
        ):
            super().__init__()
            self.id = id_
            self.string = string
            self.point = point
            self.dimensions = dimensions
            self.collection = collection or pyfdl.TypedCollection(pyfdl.FramingIntent)
            self.round = round_

            # Make sure we have a rounding strategy
            if pyfdl.Base.rounding_strategy is None:
                pyfdl.Base.set_rounding_strategy()

    return BaseSubclass


@pytest.fixture
def base_class_kwargs(sample_framing_intent, sample_framing_intent_obj, sample_rounding_strategy_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    collection.add(sample_framing_intent_obj)
    kwargs = {
        "id_": "my_id",
        "string": "hello",
        "point": pyfdl.Point(x=0, y=0),
        "dimensions": pyfdl.Dimensions(width=1920, height=1080),
        "collection": collection,
        "round_": sample_rounding_strategy_obj
    }

    return kwargs


@pytest.fixture
def base_class_dict():
    d = {
        "id": "my_id",
        "string": "hello",
        "point": {"x": 0, "y": 0},
        "dimensions": {"width": 1920, "height": 1080},
        "collection": [
            {"label": "1.78-1", "id": "FDLSMP03", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.088}
        ],
        "round": {"even": "even", "mode": "round"}
    }

    return d


@pytest.fixture
def sample_dimensions_float():
    return pyfdl.Dimensions(width=25.92, height=21.60)


@pytest.fixture
def sample_dimensions_int():
    return pyfdl.Dimensions(width=16, height=9, dtype=int)


@pytest.fixture
def sample_point() -> dict:
    point = {"x": 196, "y": 288}
    return point


@pytest.fixture
def sample_header() -> dict:
    header = {
        "uuid": "0E6D12BB-5D9A-461C-803E-5696E9CC8989",
        "version": {"major": 0, "minor": 1},
        "fdl_creator": "ASC FDL Committee",
        "default_framing_intent": "FDLSMP03"
    }
    return header


@pytest.fixture
def sample_header_kwargs() -> dict:
    header = {
        "_uuid": "0E6D12BB-5D9A-461C-803E-5696E9CC8989",
        "version": {"major": 0, "minor": 1},
        "fdl_creator": "ASC FDL Committee",
        "default_framing_intent": "FDLSMP03"
    }
    return header


@pytest.fixture
def sample_framing_intent_obj():
    framing_intent = pyfdl.FramingIntent(
        label="1.78-1 Framing",
        id_="FDLSMP03",
        aspect_ratio=pyfdl.Dimensions(width=16, height=9, dtype=int),
        protection=0.088
    )

    return framing_intent


@pytest.fixture
def sample_framing_intent() -> dict:
    framing_intent = {
        "label": "1.78-1 Framing",
        "id": "FDLSMP03",
        "aspect_ratio": {"width": 16, "height": 9},
        "protection": 0.088
    }
    return framing_intent


@pytest.fixture
def sample_framing_intent_kwargs() -> dict:
    framing_intent = {
        "label": "1.78-1 Framing",
        "id_": "FDLSMP03",
        "aspect_ratio": {"width": 16, "height": 9},
        "protection": 0.088
    }
    return framing_intent


@pytest.fixture
def sample_framing_decision() -> dict:
    fd = {
        "label": "1.78-1 Framing",
        "id": "20220310-FDLSMP03",
        "framing_intent_id": "FDLSMP03",
        "dimensions": {"width": 4728, "height": 3456},
        "anchor_point": {"x": 228, "y": 432},
        "protection_dimensions": {"width": 5184, "height": 3790},
        "protection_anchor_point": {"x": 0, "y": 265}
    }
    return fd


@pytest.fixture
def sample_framing_decision_kwargs() -> dict:
    fd = {
        "label": "1.78-1 Framing",
        "id_": "20220310-FDLSMP03",
        "framing_intent_id": "FDLSMP03",
        "dimensions": {"width": 4728, "height": 3456},
        "anchor_point": {"x": 228, "y": 432},
        "protection_dimensions": {"width": 5184, "height": 3790},
        "protection_anchor_point": {"x": 0, "y": 265}
    }
    return fd


@pytest.fixture
def sample_canvas() -> dict:
    canvas = {
        "label": "Open Gate RAW",
        "id": "20220310",
        "source_canvas_id": "20220310",
        "dimensions": {"width": 5184, "height": 4320},
        "effective_dimensions": {"width": 5184, "height": 4320},
        "effective_anchor_point": {"x": 0, "y": 0},
        "photosite_dimensions": {"width": 5184, "height": 4320},
        "physical_dimensions": {"width": 25.92, "height": 21.60},
        "anamorphic_squeeze": 1.30,
        "framing_decisions": []
    }

    return canvas


@pytest.fixture
def sample_canvas_kwargs() -> dict:
    canvas = {
        "label": "Open Gate RAW",
        "id_": "20220310",
        "source_canvas_id": "20220310",
        "dimensions": {"width": 5184, "height": 4320},
        "effective_dimensions": {"width": 5184, "height": 4320},
        "effective_anchor_point": {"x": 0, "y": 0},
        "photosite_dimensions": {"width": 5184, "height": 4320},
        "physical_dimensions": {"width": 25.92, "height": 21.60},
        "anamorphic_squeeze": 1.30,
        "framing_decisions": []
    }

    return canvas


@pytest.fixture
def sample_context() -> dict:
    ctx = {
        "label": "PanavisionDXL2",
        "context_creator": "ASC FDL Committee",
        "canvases": []
    }
    return ctx


@pytest.fixture()
def sample_canvas_template() -> dict:
    canvas_template = {
        "label": "VFX Pull",
        "id": "VX220310",
        "target_dimensions": {"width": 4096, "height": 2304},
        "target_anamorphic_squeeze": 1.00,
        "fit_source": "framing_decision.dimensions",
        "fit_method": "width",
        "alignment_method_vertical": "center",
        "alignment_method_horizontal": "center",
        "preserve_from_source_canvas": "canvas.dimensions",
        "round": {"even": "even", "mode": "up"}
    }
    return canvas_template


@pytest.fixture()
def sample_canvas_template_kwargs() -> dict:
    canvas_template = {
        "label": "VFX Pull",
        "id_": "VX220310",
        "target_dimensions": {"width": 4096, "height": 2304},
        "target_anamorphic_squeeze": 1.00,
        "fit_source": "framing_decision.dimensions",
        "fit_method": "width",
        "alignment_method_vertical": "center",
        "alignment_method_horizontal": "center",
        "preserve_from_source_canvas": "canvas.dimensions",
        "round_": {"even": "even", "mode": "up"}
    }
    return canvas_template


@pytest.fixture
def sample_rounding_strategy_obj():
    return pyfdl.RoundStrategy(even="even", mode="up")


@pytest.fixture
def sample_rounding_strategy() -> dict:
    return {"even": "even", "mode": "up"}

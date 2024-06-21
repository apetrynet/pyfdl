import pytest


@pytest.fixture
def sample_dimensions_float() -> dict:
    dim = {"width": 25.92, "height": 21.60}
    return dim


@pytest.fixture
def sample_dimensions_int() -> dict:
    dim = {"width": 16, "height": 9}
    return dim


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
        "_id": "FDLSMP03",
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
        "_id": "20220310-FDLSMP03",
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
        "_id": "20220310",
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
        "_id": "VX220310",
        "target_dimensions": {"width": 4096, "height": 2304},
        "target_anamorphic_squeeze": 1.00,
        "fit_source": "framing_decision.dimensions",
        "fit_method": "width",
        "alignment_method_vertical": "center",
        "alignment_method_horizontal": "center",
        "preserve_from_source_canvas": "canvas.dimensions",
        "_round": {"even": "even", "mode": "up"}
    }
    return canvas_template


@pytest.fixture
def sample_rounding_strategy() -> dict:
    return {"even": "even", "mode": "up"}

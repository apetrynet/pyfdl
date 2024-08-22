import pytest

import pyfdl


@pytest.mark.parametrize(
    ("fit_source", "fail"),
    [
        ("framing_decision.dimensions", "IWillFail"),
        ("framing_decision.protection_dimensions", "IWillFail"),
        ("canvas.dimensions", "IWillFail"),
        ("canvas.effective_dimensions", "IWillFail"),
    ],
)
def test_fit_source_enum_validation(fit_source, fail):
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.fit_source = fit_source
    assert canvas_template.fit_source == fit_source

    with pytest.raises(pyfdl.FDLError):
        canvas_template.fit_source = fail


@pytest.mark.parametrize(
    ("fit_method", "fail"),
    [("width", "IWillFail"), ("height", "IWillFail"), ("fit_all", "IWillFail"), ("fill", "IWillFail")],
)
def test_fit_method_enum_validation(fit_method, fail):
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.fit_method = fit_method
    assert canvas_template.fit_method == fit_method

    with pytest.raises(pyfdl.FDLError):
        canvas_template.fit_method = fail


@pytest.mark.parametrize(
    ("alignment", "fail"),
    [
        ("center", "IWillFail"),
        ("top", "IWillFail"),
        ("bottom", "IWillFail"),
    ],
)
def test_alignment_method_vertical_enum_validation(alignment, fail):
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.alignment_method_vertical = alignment
    assert canvas_template.alignment_method_vertical == alignment

    with pytest.raises(pyfdl.FDLError):
        canvas_template.alignment_method_vertical = fail


@pytest.mark.parametrize(
    ("alignment", "fail"),
    [
        ("left", "IWillFail"),
        ("center", "IWillFail"),
        ("right", "IWillFail"),
    ],
)
def test_alignment_method_horizontal_enum_validation(alignment, fail):
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.alignment_method_horizontal = alignment
    assert canvas_template.alignment_method_horizontal == alignment

    with pytest.raises(pyfdl.FDLError):
        canvas_template.alignment_method_horizontal = fail


@pytest.mark.parametrize(
    ("preserve", "fail"),
    [
        ("none", "IWillFail"),
        ("framing_decision.dimensions", "IWillFail"),
        ("framing_decision.protection_dimensions", "IWillFail"),
        ("canvas.dimensions", "IWillFail"),
        ("canvas.effective_dimensions", "IWillFail"),
    ],
)
def test_preserve_from_source_canvas_enum_validation(preserve, fail):
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.preserve_from_source_canvas = preserve
    assert canvas_template.preserve_from_source_canvas == preserve

    with pytest.raises(pyfdl.FDLError):
        canvas_template.preserve_from_source_canvas = fail


@pytest.mark.parametrize(
    ("source_width", "squeeze_factor", "target_squeeze", "expected"),
    [
        (100, 2, 1, 200),
        (100, 2, 2, 100),
        (100, 2, 1.5, 200 / 1.5),
        (100, 2, 0, 100),  # target anamorphic squeeze of 0 is same as source
    ],
)
def test_get_desqueezed_width(sample_canvas_template_obj, source_width, squeeze_factor, target_squeeze, expected):
    template = sample_canvas_template_obj
    template.target_anamorphic_squeeze = target_squeeze
    assert template.get_desqueezed_width(source_width, squeeze_factor) == expected


@pytest.mark.parametrize(
    ("fit_method", "target_dim", "source_dim", "source_sqz", "expected"),
    [
        ("width", (1920, 1080), (960, 540), 1, 2),
        ("height", (1920, 1080), (960, 540), 1, 2),
        ("fit_all", (1920, 1080), (960, 540), 1, 2),
        ("fill", (1920, 1080), (960, 540), 1, 2),
        ("width", (1920, 1080), (960, 1080), 2, 1),
        ("height", (1920, 1080), (960, 1080), 2, 1),
        ("fit_all", (1920, 1080), (960, 1080), 2, 1),
        ("fill", (1920, 1080), (960, 1080), 2, 1),
        ("width", (1000, 500), (250, 500), 1, 4),
        ("height", (1000, 500), (250, 500), 1, 1),
        ("fit_all", (1000, 500), (250, 500), 1, 1),
        ("fill", (1000, 500), (250, 500), 1, 4),
        ("width", (960, 540), (1920, 1080), 1, 0.5),
        ("height", (960, 540), (1920, 1080), 1, 0.5),
        ("fit_all", (960, 540), (1920, 1080), 1, 0.5),
        ("fill", (960, 540), (1920, 1080), 1, 0.5),
        ("width", (250, 500), (1000, 500), 1, 0.25),
        ("height", (250, 500), (1000, 500), 1, 1),
        ("fit_all", (250, 500), (1000, 500), 1, 0.25),
        ("fill", (250, 500), (1000, 500), 1, 1),
    ],
)
def test_get_scale_factor(sample_canvas_template_obj, fit_method, target_dim, source_dim, source_sqz, expected):
    template = sample_canvas_template_obj
    template.target_dimensions.width, template.target_dimensions.height = target_dim
    template.fit_method = fit_method
    assert template.get_scale_factor(pyfdl.Dimensions(*source_dim), source_sqz) == expected


@pytest.mark.parametrize(
    ("fit_method", "target_dim", "source_dim", "source_sqz", "expected"),
    [  # Same aspect
        ("width", (1920, 1080), (960, 540), 1, (1920, 1080)),
        ("height", (1920, 1080), (960, 540), 1, (1920, 1080)),
        ("fit_all", (1920, 1080), (960, 540), 1, (1920, 1080)),
        ("fill", (1920, 1080), (960, 540), 1, (1920, 1080)),
        # Same aspect, but difference squeeze
        ("width", (1920, 1080), (480, 540), 2, (1920, 1080)),
        ("height", (1920, 1080), (480, 540), 2, (1920, 1080)),
        ("fit_all", (1920, 1080), (480, 540), 2, (1920, 1080)),
        ("fill", (1920, 1080), (480, 540), 2, (1920, 1080)),
        # Taller than target
        ("width", (1920, 1080), (540, 960), 1, (1920, 1080)),
        ("height", (1920, 1080), (540, 960), 1, (607.5, 1080)),
        ("fit_all", (1920, 1080), (540, 960), 1, (607.5, 1080)),
        ("fill", (1920, 1080), (540, 960), 1, (1920, 1080)),
        # Wider than target
        ("width", (1920, 1080), (960, 500), 1, (1920, 1000)),
        ("height", (1920, 1080), (960, 500), 1, (1920, 1080)),
        ("fit_all", (1920, 1080), (960, 500), 1, (1920, 1000)),
        ("fill", (1920, 1080), (960, 500), 1, (1920, 1080)),
    ],
)
def test_fit_source_to_target(sample_canvas_template_obj, fit_method, target_dim, source_dim, source_sqz, expected):
    template = sample_canvas_template_obj
    template.target_dimensions.width, template.target_dimensions.height = target_dim
    template.fit_method = fit_method

    assert template.fit_source_to_target(pyfdl.Dimensions(*source_dim), source_sqz) == pyfdl.Dimensions(*expected)


@pytest.mark.parametrize(
    ("fit_source", "preserve", "expected"),
    [
        (
            "framing_decision.dimensions",
            "canvas.dimensions",
            [
                "framing_decision.dimensions",
                "framing_decision.protection_dimensions",
                "canvas.effective_dimensions",
                "canvas.dimensions",
            ],
        ),
        ("framing_decision.dimensions", "framing_decision.dimensions", ["framing_decision.dimensions"]),
        ("framing_decision.dimensions", "none", ["framing_decision.dimensions"]),
        ("framing_decision.dimensions", None, ["framing_decision.dimensions"]),
    ],
)
def test_get_transfer_keys(sample_canvas_template_obj, fit_source, preserve, expected):
    template = sample_canvas_template_obj
    template.fit_source = fit_source
    template.preserve_from_source_canvas = preserve
    assert template.get_transfer_keys() == expected

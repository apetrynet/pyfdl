import pytest

import pyfdl


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
        ("width", (1920, 1080), {"width": 960, "height": 540}, 1, 2),
        ("height", (1920, 1080), {"width": 960, "height": 540}, 1, 2),
        ("fit_all", (1920, 1080), {"width": 960, "height": 540}, 1, 2),
        ("fill", (1920, 1080), {"width": 960, "height": 540}, 1, 2),
        ("width", (1920, 1080), {"width": 960, "height": 1080}, 2, 1),
        ("height", (1920, 1080), {"width": 960, "height": 1080}, 2, 1),
        ("fit_all", (1920, 1080), {"width": 960, "height": 1080}, 2, 1),
        ("fill", (1920, 1080), {"width": 960, "height": 1080}, 2, 1),
        ("width", (1000, 500), {"width": 250, "height": 500}, 1, 4),
        ("height", (1000, 500), {"width": 250, "height": 500}, 1, 1),
        ("fit_all", (1000, 500), {"width": 250, "height": 500}, 1, 1),
        ("fill", (1000, 500), {"width": 250, "height": 500}, 1, 4),
        ("width", (960, 540), {"width": 1920, "height": 1080}, 1, 0.5),
        ("height", (960, 540), {"width": 1920, "height": 1080}, 1, 0.5),
        ("fit_all", (960, 540), {"width": 1920, "height": 1080}, 1, 0.5),
        ("fill", (960, 540), {"width": 1920, "height": 1080}, 1, 0.5),
        ("width", (250, 500), {"width": 1000, "height": 500}, 1, 0.25),
        ("height", (250, 500), {"width": 1000, "height": 500}, 1, 1),
        ("fit_all", (250, 500), {"width": 1000, "height": 500}, 1, 0.25),
        ("fill", (250, 500), {"width": 1000, "height": 500}, 1, 1),
    ],
)
def test_get_scale_factor(sample_canvas_template_obj, fit_method, target_dim, source_dim, source_sqz, expected):
    template = sample_canvas_template_obj
    template.target_dimensions.width, template.target_dimensions.height = target_dim
    template.fit_method = fit_method
    assert template.get_scale_factor(pyfdl.Dimensions(**source_dim), source_sqz) == expected


@pytest.mark.parametrize(
    ("fit_method", "target_dim", "source_dim", "source_sqz", "expected"),
    [  # Same aspect
        ("width", (1920, 1080), {"width": 960, "height": 540}, 1, {"width": 1920, "height": 1080}),
        ("height", (1920, 1080), {"width": 960, "height": 540}, 1, {"width": 1920, "height": 1080}),
        ("fit_all", (1920, 1080), {"width": 960, "height": 540}, 1, {"width": 1920, "height": 1080}),
        ("fill", (1920, 1080), {"width": 960, "height": 540}, 1, {"width": 1920, "height": 1080}),
        # Same aspect, but difference squeeze
        ("width", (1920, 1080), {"width": 480, "height": 540}, 2, {"width": 1920, "height": 1080}),
        ("height", (1920, 1080), {"width": 480, "height": 540}, 2, {"width": 1920, "height": 1080}),
        ("fit_all", (1920, 1080), {"width": 480, "height": 540}, 2, {"width": 1920, "height": 1080}),
        ("fill", (1920, 1080), {"width": 480, "height": 540}, 2, {"width": 1920, "height": 1080}),
        # Taller than target
        ("width", (1920, 1080), {"width": 540, "height": 960}, 1, {"width": 1920, "height": 1080}),
        ("height", (1920, 1080), {"width": 540, "height": 960}, 1, {"width": 607.5, "height": 1080}),
        ("fit_all", (1920, 1080), {"width": 540, "height": 960}, 1, {"width": 607.5, "height": 1080}),
        ("fill", (1920, 1080), {"width": 540, "height": 960}, 1, {"width": 1920, "height": 1080}),
        # Wider than target
        ("width", (1920, 1080), {"width": 960, "height": 500}, 1, {"width": 1920, "height": 1000}),
        ("height", (1920, 1080), {"width": 960, "height": 500}, 1, {"width": 1920, "height": 1080}),
        ("fit_all", (1920, 1080), {"width": 960, "height": 500}, 1, {"width": 1920, "height": 1000}),
        ("fill", (1920, 1080), {"width": 960, "height": 500}, 1, {"width": 1920, "height": 1080}),
    ],
)
def test_fit_source_to_target(sample_canvas_template_obj, fit_method, target_dim, source_dim, source_sqz, expected):
    template = sample_canvas_template_obj
    template.target_dimensions.width, template.target_dimensions.height = target_dim
    template.fit_method = fit_method

    assert template.fit_source_to_target(pyfdl.Dimensions(**source_dim), source_sqz) == pyfdl.Dimensions(**expected)


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

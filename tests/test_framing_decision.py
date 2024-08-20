import pytest

import pyfdl


@pytest.mark.parametrize(
    "intent_ratio,canvas_dim,canvas_eff,canvas_sqz,protection,expected_dim,expected_prot",
    [
        # one to one
        ((16, 9), (1920, 1080), None, 1, 0, (1920, 1080), None),
        # one to one squeeze 2
        ((16, 9), (960, 1080), None, 2, 0, (960, 1080), None),
        # 10% protection
        ((16, 9), (1920, 1080), (1920, 1080), 1, 0.1, (1920 - 192, 1080 - 108), (1920, 1080)),
        # effective canvas and 10% protection
        ((16, 9), (1920, 1080), (1920 - 192, 1080 - 108), 1, 0.1, (1556, 874), (1920 - 192, 1080 - 108)),
        # Wide intent
        ((235, 100), (1920, 1080), (1920, 1080), 1, 0, (1920, 818), None),
        # Tall intent
        ((4, 3), (1920, 1080), (1920, 1080), 1, 0, (1440, 1080), None),
    ],
)
def test_from_framing_intent(
    sample_framing_intent_obj,
    sample_canvas_obj,
    intent_ratio,
    canvas_dim,
    canvas_eff,
    canvas_sqz,
    protection,
    expected_dim,
    expected_prot,
):
    intent = sample_framing_intent_obj
    intent.aspect_ratio = pyfdl.Dimensions(*intent_ratio)
    intent.protection = protection
    canvas = sample_canvas_obj
    canvas.dimensions = pyfdl.Dimensions(*canvas_dim)
    canvas.anamorphic_squeeze = canvas_sqz
    if canvas_eff is not None:
        canvas.effective_dimensions = pyfdl.Dimensions(*canvas_eff)
    else:
        canvas.effective_dimensions = None

    # Override rounding to match values in samples
    pyfdl.set_rounding_strategy({"even": "even", "mode": "round"})
    result = pyfdl.FramingDecision.from_framing_intent(canvas=canvas, framing_intent=intent)
    assert result.dimensions == pyfdl.Dimensions(*expected_dim)

    if expected_prot is not None:
        assert result.protection_dimensions == pyfdl.Dimensions(*expected_prot)
    else:
        assert result.protection_dimensions is None


@pytest.mark.parametrize(
    "h_method, v_method, protection_dim, protection_pnt, expected",
    [
        ("left", "top", None, None, (0, 0)),
        ("left", "top", (550, 550), (0, 0), (25, 25)),
        ("left", "center", None, None, (0, 250)),
        ("left", "center", (550, 550), (0, 225), (25, 250)),
        ("left", "bottom", None, None, (0, 500)),
        ("left", "bottom", (550, 550), (0, 450), (25, 475)),
        ("center", "top", None, None, (250, 0)),
        ("center", "top", (550, 550), (225, 0), (250, 25)),
        ("center", "center", None, None, (250, 250)),
        ("center", "center", (550, 550), (225, 225), (250, 250)),
        ("center", "bottom", None, None, (250, 500)),
        ("center", "bottom", (550, 550), (225, 450), (250, 475)),
        ("right", "top", None, None, (500, 0)),
        ("right", "top", (550, 550), (450, 0), (475, 25)),
        ("right", "center", None, None, (500, 250)),
        ("right", "center", (550, 550), (450, 225), (475, 250)),
        ("right", "bottom", None, None, (500, 500)),
        ("right", "bottom", (550, 550), (450, 450), (475, 475)),
    ],
)
def test_adjust_anchor_point(h_method, v_method, protection_dim, protection_pnt, expected):
    canvas = pyfdl.Canvas(dimensions=pyfdl.Dimensions(width=1000, height=1000))
    framing_decision = pyfdl.FramingDecision(dimensions=pyfdl.Dimensions(width=500, height=500))
    if protection_dim is not None:
        framing_decision.protection_dimensions = pyfdl.Dimensions(*protection_dim)
        framing_decision.protection_anchor_point = pyfdl.Point(*protection_pnt)

    framing_decision.adjust_anchor_point(canvas=canvas, h_method=h_method, v_method=v_method)
    assert framing_decision.anchor_point == pyfdl.Point(*expected)


@pytest.mark.parametrize(
    "h_method, v_method, expected",
    [
        ("left", "top", (0, 0)),
        ("left", "center", (0, 225)),
        ("left", "bottom", (0, 450)),
        (
            "center",
            "top",
            (225, 0),
        ),
        ("center", "center", (225, 225)),
        ("center", "bottom", (225, 450)),
        ("right", "top", (450, 0)),
        ("right", "center", (450, 225)),
        ("right", "bottom", (450, 450)),
    ],
)
def test_adjust_protection_anchor_point(h_method, v_method, expected):
    canvas = pyfdl.Canvas(dimensions=pyfdl.Dimensions(width=1000, height=1000))
    framing_decision = pyfdl.FramingDecision(protection_dimensions=pyfdl.Dimensions(width=550, height=550))

    framing_decision.adjust_protection_anchor_point(canvas=canvas, h_method=h_method, v_method=v_method)
    assert framing_decision.protection_anchor_point == pyfdl.Point(*expected)

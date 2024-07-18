import pytest

import pyfdl


def test_dimensions_int():
    dim = pyfdl.Dimensions(width=1920, height=1080)
    assert dim.dtype == float
    canvas = pyfdl.Canvas()

    # property method makes sure dimensions have dtype int
    canvas.dimensions = dim
    assert dim.dtype == int


def test_source_canvas_id(sample_canvas_obj):
    fdl = pyfdl.FDL()
    fdl.apply_defaults()

    fdl.place_canvas_in_context(context_label="context1", canvas=sample_canvas_obj)
    assert fdl.validate() is None
    fdl.contexts[0].canvases.remove(sample_canvas_obj.id)

    sample_canvas_obj.id = "456"
    sample_canvas_obj.source_canvas_id = "123"
    fdl.place_canvas_in_context(context_label="context2", canvas=sample_canvas_obj)

    with pytest.raises(pyfdl.FDLValidationError) as err:
        fdl.validate()

    assert f'{sample_canvas_obj.source_canvas_id} (canvas.source_canvas_id) not found in ' in str(err)


def test_place_framing_intent(sample_framing_intent_obj, sample_canvas_obj, sample_framing_decision_obj):
    intent = sample_framing_intent_obj
    canvas = sample_canvas_obj

    decision_id = canvas.place_framing_intent(intent)
    assert decision_id == f'{canvas.id}-{intent.id}'

    decision = canvas.framing_decisions.get(decision_id)
    assert decision == sample_framing_decision_obj


def test_get_dimensions(sample_canvas_obj):
    assert sample_canvas_obj.get_dimensions() == (
        sample_canvas_obj.effective_dimensions,
        sample_canvas_obj.effective_anchor_point
    )
    sample_canvas_obj.effective_dimensions = None
    assert sample_canvas_obj.get_dimensions() == (
        sample_canvas_obj.dimensions,
        pyfdl.Point(x=0, y=0)
    )


def test_from_canvas_template(sample_canvas_obj, sample_framing_decision_obj, sample_canvas_template_obj):
    canvas = sample_canvas_obj
    canvas_template = sample_canvas_template_obj
    framing_decision = sample_framing_decision_obj
    new_canvas = pyfdl.Canvas.from_canvas_template(
        canvas_template,
        canvas,
        framing_decision
    )

    assert isinstance(new_canvas, pyfdl.Canvas)
    assert new_canvas.dimensions != canvas.dimensions


def test_from_adjust_anchor_point(sample_canvas_obj):
    canvas = sample_canvas_obj
    canvas.effective_anchor_point = pyfdl.Point(x=10, y=10)
    canvas.adjust_effective_anchor_point()

    assert canvas.effective_anchor_point == pyfdl.Point(x=0, y=0)

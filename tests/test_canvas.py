import pytest

import pyfdl


def test_canvas_instance_from_dict(sample_canvas):
    canvas = pyfdl.Canvas.from_dict(sample_canvas)
    assert isinstance(canvas, pyfdl.Canvas)
    assert canvas.to_dict() == sample_canvas


def test_canvas_instance_from_kwargs(sample_canvas, sample_canvas_kwargs):
    canvas = pyfdl.Canvas(**sample_canvas_kwargs)
    assert isinstance(canvas, pyfdl.Canvas)
    assert canvas.to_dict() == sample_canvas
    assert canvas.check_required() == []


def test_canvas_linked_requirements(sample_canvas_kwargs):
    # check linked requirements "effective_dimensions.effective_anchor_point"
    kwargs = sample_canvas_kwargs.copy()
    kwargs.pop('effective_anchor_point')
    canvas = pyfdl.Canvas(**kwargs)
    assert canvas.check_required() == ['effective_anchor_point']
    del canvas

    kwargs.pop('effective_dimensions')
    canvas = pyfdl.Canvas(**kwargs)
    assert canvas.check_required() == []


def test_source_canvas_id(sample_canvas_kwargs, sample_canvas):
    fdl = pyfdl.FDL()
    fdl.apply_defaults()

    canvas1 = pyfdl.Canvas.from_dict(sample_canvas)

    fdl.place_canvas_in_context(context_label="context1", canvas=canvas1)
    assert fdl.validate() is None

    canvas2 = pyfdl.Canvas.from_dict(sample_canvas)
    canvas2.id = "456"
    canvas2.source_canvas_id = "123"

    fdl.place_canvas_in_context(context_label="context2", canvas=canvas2)

    with pytest.raises(pyfdl.FDLValidationError) as err:
        fdl.validate()

    assert f'{canvas2.source_canvas_id} (canvas.source_canvas_id) not found in ' in str(err)


def test_place_framing_intent(sample_framing_intent, sample_canvas, sample_framing_decision):
    intent = pyfdl.FramingIntent.from_dict(sample_framing_intent)
    canvas = pyfdl.Canvas.from_dict(sample_canvas)

    decision_id = canvas.place_framing_intent(intent)
    assert decision_id == f'{canvas.id}-{intent.id}'

    decision = canvas.framing_decisions.get_item(decision_id)
    facit_decision = pyfdl.FramingDecision.from_dict(sample_framing_decision)
    assert decision == facit_decision

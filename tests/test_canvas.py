import pytest

import fdl
import fdl.config
from fdl.rounding import RoundStrategy


def test_source_canvas_id(sample_canvas_obj):
    my_fdl = fdl.FDL()
    my_fdl.place_canvas_in_context(context_label="context1", canvas=sample_canvas_obj)
    assert my_fdl.validate_fdl() is None
    my_fdl.contexts[0].canvases.remove(sample_canvas_obj.id)

    sample_canvas_obj.id = "456"
    sample_canvas_obj.source_canvas_id = "123"
    my_fdl.place_canvas_in_context(context_label="context2", canvas=sample_canvas_obj)

    with pytest.raises(fdl.FDLValidationError) as err:
        my_fdl.validate_fdl()

    assert f'canvas.source_canvas_id: "{sample_canvas_obj.source_canvas_id}" not found among ' in str(err)


def test_place_framing_intent(sample_framing_intent_obj, sample_canvas_obj, sample_framing_decision_obj):
    intent = sample_framing_intent_obj
    canvas = sample_canvas_obj

    # Overriding rounding to match sample values
    fdl.config.set_rounding(RoundStrategy(even="even", mode="round"))
    decision_id = canvas.place_framing_intent(intent)
    assert decision_id == f"{canvas.id}-{intent.id}"

    decision = canvas.framing_decisions.get_by_id(decision_id)
    assert decision == sample_framing_decision_obj


def test_from_adjust_anchor_point(sample_canvas_obj):
    canvas = sample_canvas_obj
    canvas.effective_anchor_point = fdl.PointFloat(x=10, y=10)
    canvas.adjust_effective_anchor_point()

    assert canvas.effective_anchor_point == fdl.PointFloat(x=0, y=0)

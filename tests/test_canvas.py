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


def test_source_canvas_id(sample_canvas_kwargs):
    tc = pyfdl.TypedCollection(pyfdl.Canvas)

    kwargs = sample_canvas_kwargs.copy()
    _id = kwargs.pop('source_canvas_id')
    cv1 = pyfdl.Canvas(**kwargs)
    tc.add_item(cv1)
    # This should fail because a canvas with id 123 is not in container
    with pytest.raises(pyfdl.FDLError) as err:
        cv1.source_canvas_id = '123'

    assert '"source_canvas_id" 123 must either be self.id' in str(err.value)
    cv1.source_canvas_id = _id

    kwargs['_id'] = '123'
    cv2 = pyfdl.Canvas(**kwargs)

    # This should fail because cv2 is not in a container and id is not equal its own
    with pytest.raises(pyfdl.FDLError) as err:
        cv2.source_canvas_id = cv1.id

    assert f'"source_canvas_id" {cv1.id} must either be self.id' in str(err.value)

    tc.add_item(cv2)
    cv2.source_canvas_id = cv1.id

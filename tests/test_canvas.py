import pyfdl


def test_canvas_instance_from_dict(sample_canvas):
    canvas = pyfdl.Canvas.from_dict(sample_canvas)
    assert isinstance(canvas, pyfdl.Canvas)
    assert canvas.to_dict() == sample_canvas


def test_canvas_instance_from_kwargs(sample_canvas, sample_canvas_kwargs):
    canvas1 = pyfdl.Canvas(**sample_canvas_kwargs)
    assert isinstance(canvas1, pyfdl.Canvas)
    assert canvas1.to_dict() == sample_canvas
    assert canvas1.check_required() == []


def test_canvas_linked_requirements(sample_canvas_kwargs):
    # check linked requirements "effective_dimensions.effective_anchor_point"
    kwargs = sample_canvas_kwargs.copy()
    kwargs.pop('effective_anchor_point')
    canvas2 = pyfdl.Canvas(**kwargs)
    assert canvas2.check_required() == ['effective_anchor_point']

    kwargs.pop('effective_dimensions')
    canvas3 = pyfdl.Canvas(**kwargs)
    assert canvas3.check_required() == []

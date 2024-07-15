import pyfdl


def test_framing_decision_from_dict(sample_framing_decision):
    fd = pyfdl.FramingDecision.from_dict(sample_framing_decision)
    assert isinstance(fd, pyfdl.FramingDecision)
    assert fd.check_required() == []
    assert isinstance(fd.dimensions, pyfdl.Dimensions)
    assert isinstance(fd.protection_anchor_point, pyfdl.Point)
    assert fd.to_dict() == sample_framing_decision


def test_framing_decision_from_kwargs(sample_framing_decision, sample_framing_decision_kwargs):
    fd = pyfdl.FramingDecision(**sample_framing_decision_kwargs)
    assert isinstance(fd, pyfdl.FramingDecision)
    assert fd.check_required() == []
    assert fd.to_dict() == sample_framing_decision


def test_framing_decision_required():
    fd = pyfdl.FramingDecision()
    assert fd.check_required() == fd.required

    fd.id = "MyID"
    fd.framing_intent_id = "SomeOtherID"
    fd.dimensions = pyfdl.Dimensions(width=1920, height=1080)
    fd.anchor_point = pyfdl.Point(x=0, y=0)

    assert fd.check_required() == []

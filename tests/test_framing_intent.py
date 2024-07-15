import pyfdl


def test_framing_intent_from_dict(sample_framing_intent):
    fi = pyfdl.FramingIntent.from_dict(sample_framing_intent)
    assert isinstance(fi, pyfdl.FramingIntent)
    assert fi.check_required() == []
    assert isinstance(fi.aspect_ratio, pyfdl.Dimensions)
    assert fi.to_dict() == sample_framing_intent


def test_framing_intent_from_kwargs(sample_framing_intent, sample_framing_intent_kwargs):
    fi = pyfdl.FramingIntent(**sample_framing_intent_kwargs)
    assert isinstance(fi, pyfdl.FramingIntent)
    assert fi.check_required() == []
    assert fi.to_dict() == sample_framing_intent


def test_framing_intent_required():
    fi = pyfdl.FramingIntent()
    assert fi.check_required() == fi.required

    fi.id = "MyID"
    fi.aspect_ratio = pyfdl.Dimensions(width=16, height=9)
    assert fi.check_required() == []

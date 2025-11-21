import pytest

import pyfdl
import pyfdl.rounding
import pyfdl.config as config


def test_typed_collection_init():
    collection = pyfdl.TypedCollection[pyfdl.FramingIntent]()
    assert collection._cls == pyfdl.FramingIntent


def test_typed_collection_append(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection[pyfdl.FramingIntent]()
    collection.append(sample_framing_intent_obj)
    assert len(collection) == 1

    with pytest.raises(ValueError) as err:
        collection.append("just_a_string")

    assert f'This collection only accepts items of type: "{pyfdl.FramingIntent.__name__}"' in str(err)

    with pytest.raises(ValueError) as err:
        collection.append(sample_framing_intent_obj)

    assert "already exists in collection" in str(err)


def test_typed_collection_get_by_id(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection[pyfdl.FramingIntent]()
    framing_intent = sample_framing_intent_obj
    collection.append(framing_intent)
    assert collection.get_by_id(framing_intent.id) == framing_intent
    assert collection.get_by_id("not_present") is None


def test_typed_collection_remove(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection[pyfdl.FramingIntent]()
    framing_intent = sample_framing_intent_obj
    collection.append(framing_intent)
    collection.remove(framing_intent.id)
    assert len(collection) == 0

    collection.append(framing_intent)
    collection.remove("unknown")
    assert len(collection) == 1


def test_typed_collection_contains(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection[pyfdl.FramingIntent]()
    framing_intent = sample_framing_intent_obj
    assert (framing_intent in collection) is False
    assert bool(collection) is False

    collection.append(framing_intent)
    assert (framing_intent in collection) is True
    assert bool(collection) is True

    assert collection[0] == framing_intent


@pytest.mark.parametrize(
    "dtype",
    [
        int,
        float
    ]
)
def test_dimensions_init(dtype):
    dim = pyfdl.Dimensions[dtype](width=1000, height=1000)
    assert dim.width.__class__ == dtype
    assert dim.height.__class__ == dtype


def test_dimensions_scale_by():
    # Overriding rounding to match values in sample
    config.set_rounding(pyfdl.rounding.RoundStrategy(even="even", mode="round"))
    dim_1 = pyfdl.Dimensions[int](width=1, height=2)
    dim_1.scale_by(2)
    assert (dim_1.width, dim_1.height) == (2, 4)

    dim_2 = pyfdl.Dimensions[float](width=1.1, height=2.2)
    dim_2.scale_by(2)
    assert (dim_2.width, dim_2.height) == (2.2, 4.4)

    # Check if scaling follows rounding rules
    dim_3 = pyfdl.Dimensions[int](width=1, height=2)
    config.set_rounding(pyfdl.rounding.RoundStrategy(even="whole", mode="up"))
    dim_3.scale_by(2.1)
    assert (dim_3.width, dim_3.height) == (3, 5)


def test_dimensions_duplicate():
    dim_1 = pyfdl.Dimensions[float](width=1.1, height=2.2)
    dim_2 = dim_1.duplicate()
    assert dim_1 == dim_2
    assert dim_1.width.__class__ == dim_2.width.__class__
    assert id(dim_1) != id(dim_2)


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, True),
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1081}, True),
        ({"width": 1920, "height": 1080}, {"width": 1919, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1079}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, False),
    ],
)
def test_dimensions_lt(source_dim, compare_dim, expected):
    assert (pyfdl.Dimensions(**source_dim) < pyfdl.Dimensions(**compare_dim)) is expected


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, True),
    ],
)
def test_dimensions_eq(source_dim, compare_dim, expected):
    assert (pyfdl.Dimensions(**source_dim) == pyfdl.Dimensions(**compare_dim)) is expected


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1919, "height": 1080}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1079}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, False),
    ],
)
def test_dimensions_gt(source_dim, compare_dim, expected):
    assert (pyfdl.Dimensions(**source_dim) > pyfdl.Dimensions(**compare_dim)) is expected


@pytest.mark.parametrize(
    "dtype",
    [
        int,
        float
    ]
)
def test_point_init(dtype):
    point = pyfdl.Point[dtype](x=1000, y=1000)
    assert point.x.__class__ == dtype
    assert point.y.__class__ == dtype

    point1 = pyfdl.Point()
    assert point1.x == 0
    assert point1.y == 0

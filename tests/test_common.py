import pytest

import pyfdl


def test_set_rounding_strategy(base_subclass, sample_rounding_strategy_obj):
    assert pyfdl.rounding_strategy() == pyfdl.RoundStrategy(**pyfdl.DEFAULT_ROUNDING_STRATEGY)

    override = {"even": "whole", "mode": "up"}
    pyfdl.set_rounding_strategy(rules=override)
    assert pyfdl.rounding_strategy().to_dict() == override


def test_base_empty(base_subclass):
    obj = base_subclass()
    assert isinstance(obj, base_subclass)


def test_base_from_dict(base_subclass, base_class_dict):
    obj1 = base_subclass.from_dict(base_class_dict)

    assert isinstance(obj1, base_subclass)
    assert obj1.id == "my_id"
    assert obj1.string == "hello"
    assert isinstance(obj1.point, pyfdl.Point)
    assert isinstance(obj1.dimensions, pyfdl.Dimensions)
    assert isinstance(obj1.collection, pyfdl.TypedCollection)
    assert obj1.collection._cls == pyfdl.FramingIntent
    assert isinstance(obj1.collection[0], pyfdl.FramingIntent)
    assert isinstance(obj1.round, pyfdl.RoundStrategy)


def test_base_from_kwargs(base_subclass, base_class_kwargs):
    obj1 = base_subclass(**base_class_kwargs)
    assert isinstance(obj1, base_subclass)
    assert obj1.id == "my_id"
    assert obj1.string == "hello"
    assert isinstance(obj1.point, pyfdl.Point)
    assert isinstance(obj1.dimensions, pyfdl.Dimensions)
    assert isinstance(obj1.collection, pyfdl.TypedCollection)
    assert obj1.collection._cls == pyfdl.FramingIntent
    assert isinstance(obj1.collection[0], pyfdl.FramingIntent)
    assert isinstance(obj1.round, pyfdl.RoundStrategy)


def test_base_apply_defaults(base_subclass):
    obj = base_subclass()
    assert obj.id is None
    obj.apply_defaults()
    assert obj.id == "my_id"
    assert isinstance(obj.instance, pyfdl.RoundStrategy)
    assert isinstance(obj.callable, str)
    assert obj.self_reference == obj.id


def test_base_check_required(base_subclass):
    obj = base_subclass()
    assert obj.check_required() == ["id"]

    # Check linked.requirements
    obj.string = "part one"
    assert obj.check_required() == ["id", "point"]

    obj.id = "my_id"
    obj.point = pyfdl.Point(x=0, y=0)
    assert obj.check_required() == []


def test_base_to_dict(base_subclass, base_class_dict):
    obj = base_subclass.from_dict(base_class_dict)
    assert obj.to_dict() == base_class_dict

    obj.id = None
    with pytest.raises(pyfdl.FDLError):
        obj.to_dict()


def test_base_generate_uuid(base_subclass):
    assert isinstance(base_subclass.generate_uuid(), str)


def test_typed_collection_ids(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    assert collection.ids == []

    collection.add(sample_framing_intent_obj)
    assert collection.ids == [sample_framing_intent_obj.id]


def test_typed_collection_add(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    framing_intent = sample_framing_intent_obj
    collection.add(framing_intent)
    assert len(collection) == 1

    # Add something of wrong type
    with pytest.raises(TypeError):
        collection.add(pyfdl.Point(x=10, y=10))

    # Add duplicate "id"
    with pytest.raises(pyfdl.FDLError) as err:
        collection.add(framing_intent)

    assert "already exists." in str(err)

    # Add something with "id_attribute" not set
    framing_intent_1 = pyfdl.FramingIntent()
    with pytest.raises(pyfdl.FDLError) as err:
        collection.add(framing_intent_1)

    assert "Item must have a valid identifier" in str(err)


def test_typed_collection_get(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    framing_intent = sample_framing_intent_obj
    collection.add(framing_intent)
    assert collection.get(framing_intent.id) == framing_intent
    assert collection.get("not_present") is None


def test_typed_collection_remove(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    framing_intent = sample_framing_intent_obj
    collection.add(framing_intent)
    assert len(collection) == 1
    collection.remove(framing_intent.id)
    assert len(collection) == 0
    assert bool(collection) is False


def test_typed_collection_to_list(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    framing_intent = sample_framing_intent_obj
    collection.add(framing_intent)

    assert collection.to_list() == [framing_intent.to_dict()]


def test_typed_collection_contents(sample_framing_intent_obj):
    collection = pyfdl.TypedCollection(pyfdl.FramingIntent)
    framing_intent = sample_framing_intent_obj
    collection.add(framing_intent)
    assert framing_intent in collection
    assert framing_intent.id in collection
    assert [_fi for _fi in collection] == [framing_intent]


def test_dimensions_to_dict():
    dim_1 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=int)
    assert dim_1.to_dict() == {"width": 1, "height": 2}

    dim_2 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=float)
    assert dim_2.to_dict() == {"width": 1.1, "height": 2.2}


def test_dimensions_scale_by():
    # Overriding rounding to match values in sample
    pyfdl.set_rounding_strategy({"even": "even", "mode": "round"})
    dim_1 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=int)
    dim_1.scale_by(2)
    assert (dim_1.width, dim_1.height) == (2, 4)

    dim_2 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=float)
    dim_2.scale_by(2)
    assert (dim_2.width, dim_2.height) == (2.2, 4.4)

    # Check if scaling follows rounding rules
    dim_3 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=int)
    pyfdl.set_rounding_strategy({"even": "whole", "mode": "up"})
    dim_3.scale_by(2)
    assert (dim_3.width, dim_3.height) == (3, 5)


def test_dimensions_copy():
    dim_1 = pyfdl.Dimensions(width=1.1, height=2.2, dtype=int)
    dim_2 = dim_1.copy()
    assert dim_1 == dim_2
    assert dim_1.dtype == dim_2.dtype


@pytest.mark.parametrize(
    "source_dim,compare_dim,expected",
    [
        ((1920, 1080), (1921, 1080), True),
        ((1920, 1080), (1920, 1081), True),
        ((1920, 1080), (1921, 1081), True),
        ((1920, 1080), (1919, 1080), False),
        ((1920, 1080), (1920, 1079), False),
        ((1920, 1080), (1920, 1080), False),
    ],
)
def test_dimensions_lt(source_dim, compare_dim, expected):
    assert bool(pyfdl.Dimensions(*source_dim) < pyfdl.Dimensions(*compare_dim)) is expected


@pytest.mark.parametrize(
    "source_dim,compare_dim,expected",
    [((1920, 1080), (1921, 1080), False), ((1920, 1080), (1920, 1081), False), ((1920, 1080), (1920, 1080), True)],
)
def test_dimensions_eq(source_dim, compare_dim, expected):
    assert bool(pyfdl.Dimensions(*source_dim) == pyfdl.Dimensions(*compare_dim)) is expected


@pytest.mark.parametrize(
    "source_dim,compare_dim,expected",
    [
        ((1920, 1080), (1921, 1080), False),
        ((1920, 1080), (1920, 1081), False),
        ((1920, 1080), (1921, 1081), False),
        ((1920, 1080), (1919, 1080), True),
        ((1920, 1080), (1920, 1079), True),
        ((1920, 1080), (1920, 1080), False),
    ],
)
def test_dimensions_gt(source_dim, compare_dim, expected):
    assert bool(pyfdl.Dimensions(*source_dim) > pyfdl.Dimensions(*compare_dim)) is expected


def test_rounding_strategy_validation():
    rs = pyfdl.RoundStrategy()
    with pytest.raises(pyfdl.FDLError) as err:
        rs.even = "wrong"

    assert '"wrong" is not a valid option for "even".' in str(err.value)

    with pytest.raises(pyfdl.FDLError) as err:
        rs.mode = "wrong"

    assert '"wrong" is not a valid option for "mode".' in str(err.value)


@pytest.mark.parametrize(
    "rules,dimensions,dtype,expected",
    [
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, int, (20, 80)),
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, float, (20, 80)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, int, (18, 78)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, float, (18, 78)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, int, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, float, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, int, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, float, (20, 80)),
        ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, int, (20, 80)),
        ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, float, (20, 80)),
        ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, int, (19, 79)),
        ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, float, (19, 79)),
        ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, int, (20, 80)),
        ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, float, (20, 80)),
        ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, int, (19, 79)),
        ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, float, (19, 79)),
    ],
)
def test_rounding_strategy_rounding(rules, dimensions, dtype, expected):
    rnd = pyfdl.RoundStrategy.from_dict(rules)
    dim = pyfdl.Dimensions(**dimensions, dtype=dtype)
    result = rnd.round_dimensions(dim)

    assert (result.width, result.height) == expected

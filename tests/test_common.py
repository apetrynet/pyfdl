import pytest

import pyfdl


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


def test_base_set_rounding_strategy(base_subclass, sample_rounding_strategy_obj):
    obj = base_subclass()
    assert obj.rounding_strategy.to_dict() == pyfdl.DEFAULT_ROUNDING_STRATEGY

    override = {"even": "whole", "mode": "up"}
    obj.set_rounding_strategy(rules=override)
    assert obj.rounding_strategy.to_dict() == override


def test_base_generate_uuid(base_subclass):
    assert isinstance(base_subclass.generate_uuid(), str)


def test_dimensions_point_from_dict(sample_point):
    point1 = pyfdl.Point.from_dict(sample_point)
    assert isinstance(point1, pyfdl.Point)
    assert point1.check_required() == []
    assert point1.to_dict() == sample_point


def test_dimensions_point_from_kwargs(sample_point):
    point2 = pyfdl.Point(**sample_point)
    assert isinstance(point2, pyfdl.Point)
    assert point2.check_required() == []
    assert point2.to_dict() == sample_point

    point3 = pyfdl.Point(x=16, y=9)
    assert isinstance(point3, pyfdl.Point)
    assert point3.check_required() == []
    assert point3.x == 16
    assert point3.y == 9

    with pytest.raises(TypeError) as err:
        pyfdl.Point()

    assert "missing 2 required positional arguments: 'x' and 'y'" in str(err.value)


def test_rounding_strategy_validation():
    rs = pyfdl.RoundStrategy()
    with pytest.raises(pyfdl.FDLError) as err:
        rs.even = 'wrong'

    assert '"wrong" is not a valid option for "even".' in str(err.value)

    with pytest.raises(pyfdl.FDLError) as err:
        rs.mode = 'wrong'

    assert '"wrong" is not a valid option for "mode".' in str(err.value)


def test_rounding_strategy_default_values():
    rs = pyfdl.RoundStrategy()
    assert rs.check_required() == ['even', 'mode']

    rs.apply_defaults()
    assert rs.even == 'even'
    assert rs.mode == 'up'
    assert rs.check_required() == []


def test_rounding_strategy_from_dict(sample_rounding_strategy):
    rs = pyfdl.RoundStrategy.from_dict(sample_rounding_strategy)
    assert isinstance(rs, pyfdl.RoundStrategy)
    assert rs.even == "even"
    assert rs.mode == "up"


def test_typed_collection(sample_framing_intent, sample_framing_intent_kwargs):
    td = pyfdl.TypedCollection(pyfdl.FramingIntent)
    fi = pyfdl.FramingIntent.from_dict(sample_framing_intent)
    td.add(fi)

    assert td.to_list() == [fi.to_dict()]
    assert td.ids == [f"{fi.id}"]

    assert fi in td
    assert fi.id in td
    assert td.get(fi.id) == fi
    assert [_fi for _fi in td] == [fi]

    td.remove(fi.id)
    assert len(td) == 0
    assert bool(td) is False

    with pytest.raises(TypeError) as err:
        td.add(pyfdl.Point(x=10, y=10))

    assert "This container does not accept items of type:" in str(err.value)

    # Test missing id
    fi1 = pyfdl.FramingIntent()
    with pytest.raises(pyfdl.FDLError) as err:
        td.add(fi1)

    assert f"Item must have a valid identifier (\"id\")" in str(err.value)

    # Test duplicate id's
    td.add(fi)
    kwargs = sample_framing_intent_kwargs.copy()
    kwargs['label'] = 'somethingelse'
    fi2 = pyfdl.FramingIntent(**kwargs)
    with pytest.raises(pyfdl.FDLError) as err:
        td.add(fi2)

    assert f"FramingIntent.id (\"{fi.id}\") already exists." in str(err.value)

    # Test object with alternative id_attribute
    td1 = pyfdl.TypedCollection(pyfdl.Context)
    ctx1 = pyfdl.Context(label='context1')
    td1.add(ctx1)

    with pytest.raises(pyfdl.FDLError) as err:
        td1.add(ctx1)

    assert f"Context.label (\"{ctx1.label}\") already exists." in str(err)

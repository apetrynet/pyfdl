import pytest

import pyfdl


def test_dimensions_int_from_dict(sample_dimensions_int):
    dim1 = pyfdl.DimensionsInt.from_dict(sample_dimensions_int)
    assert isinstance(dim1, pyfdl.DimensionsInt)
    assert dim1.check_required() == []
    assert dim1.to_dict() == sample_dimensions_int


def test_dimensions_int_from_kwargs(sample_dimensions_int):
    dim2 = pyfdl.DimensionsInt(**sample_dimensions_int)
    assert isinstance(dim2, pyfdl.DimensionsInt)
    assert dim2.check_required() == []
    assert dim2.to_dict() == sample_dimensions_int

    # Check that values are stores as ints
    dim3 = pyfdl.DimensionsInt(width=16.0, height=9.0)
    assert isinstance(dim3, pyfdl.DimensionsInt)
    assert dim3.check_required() == []
    assert str(dim3.width) == str(16)
    assert str(dim3.height) == str(9)

    with pytest.raises(TypeError) as err:
        pyfdl.DimensionsInt()

    assert "missing 2 required positional arguments: 'width' and 'height'" in str(err.value)


def test_dimensions_float_from_dict(sample_dimensions_float):
    dim1 = pyfdl.DimensionsFloat.from_dict(sample_dimensions_float)
    assert isinstance(dim1, pyfdl.DimensionsFloat)
    assert dim1.check_required() == []
    assert dim1.to_dict() == sample_dimensions_float


def test_dimensions_float_from_kwargs(sample_dimensions_float):
    dim2 = pyfdl.DimensionsFloat(**sample_dimensions_float)
    assert isinstance(dim2, pyfdl.DimensionsFloat)
    assert dim2.check_required() == []
    assert dim2.to_dict() == sample_dimensions_float

    dim3 = pyfdl.DimensionsFloat(width=16, height=9)
    assert isinstance(dim3, pyfdl.DimensionsFloat)
    assert dim3.check_required() == []
    assert str(dim3.width) == str(16)
    assert str(dim3.height) == str(9)

    dim4 = pyfdl.DimensionsFloat(width=16.0, height=9.0)
    assert isinstance(dim4, pyfdl.DimensionsFloat)
    assert dim4.check_required() == []
    assert str(dim4.width) == str(16.0)
    assert str(dim4.height) == str(9.0)

    with pytest.raises(TypeError) as err:
        pyfdl.DimensionsFloat()

    assert "missing 2 required positional arguments: 'width' and 'height'" in str(err.value)


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


def test_typed_init_list():
    vl1 = pyfdl.TypedList(pyfdl.Point)
    assert isinstance(vl1, pyfdl.TypedList)
    assert vl1 == []

    point = pyfdl.Point(x=10, y=10)
    vl2 = pyfdl.TypedList(pyfdl.Point, [point])
    assert isinstance(vl2, pyfdl.TypedList)
    assert vl2[0] == point


def test_typed_list_raise():
    vl = pyfdl.TypedList(pyfdl.Point)
    with pytest.raises(TypeError):
        vl.append('string')


def test_typed_list_append():
    point = pyfdl.Point(x=10, y=10)
    vl1 = pyfdl.TypedList(pyfdl.Point)
    vl1.append(point)
    assert vl1[0] == point


def test_typed_list_extend():
    points = [pyfdl.Point(x=10, y=10)]
    vl1 = pyfdl.TypedList(pyfdl.Point)
    vl1.extend(points)
    assert len(vl1) == 1
    assert vl1[0] == points[0]


def test_typed_list_insert():
    points = [pyfdl.Point(x=10, y=10), pyfdl.Point(x=30, y=30)]
    expected_points = [pyfdl.Point(x=10, y=10), pyfdl.Point(x=20, y=20), pyfdl.Point(x=30, y=30)]
    vl1 = pyfdl.TypedList(pyfdl.Point, points)
    vl1.insert(1, pyfdl.Point(x=20, y=20))
    assert len(vl1) == 3
    assert repr(vl1) == repr(expected_points)


def test_typed_container(sample_framing_intent, sample_framing_intent_kwargs):
    td = pyfdl.TypedContainer(pyfdl.FramingIntent)
    fi = pyfdl.FramingIntent.from_dict(sample_framing_intent)
    td.add_item(fi)

    assert fi in td
    assert fi.id in td
    assert td.get_item(fi.id) == fi
    assert [_fi for _fi in td] == [fi]

    td.remove_item(fi.id)
    assert len(td) == 0
    assert bool(td) is False

    with pytest.raises(TypeError) as err:
        td.add_item(pyfdl.Point(x=10, y=10))

    assert "This container does not accept items of type:" in str(err.value)

    # Test missing id
    fi1 = pyfdl.FramingIntent()
    with pytest.raises(pyfdl.FDLError) as err:
        td.add_item(fi1)

    assert f"Item must have a valid ID" in str(err.value)

    # Test duplicate id's
    td.add_item(fi)
    kwargs = sample_framing_intent_kwargs.copy()
    kwargs['label'] = 'somethingelse'
    fi2 = pyfdl.FramingIntent(**kwargs)
    with pytest.raises(pyfdl.FDLError) as err:
        td.add_item(fi2)

    assert f"FramingIntent.id ({fi.id}) already exists." in str(err.value)

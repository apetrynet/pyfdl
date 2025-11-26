import pytest
from pydantic_core import PydanticSerializationError

import pyfdl
from pyfdl import config as config


def test_set_rounding_strategy():
    assert config.get_rounding() == pyfdl.config.DEFAULT_ROUNDING_STRATEGY

    override = pyfdl.rounding.RoundStrategy(even="whole", mode="up")
    config.set_rounding(override)
    assert config.get_rounding() == override


def test_rounding_strategy_validation():
    rs = pyfdl.rounding.RoundStrategy(even=None, mode=None)
    with pytest.raises(PydanticSerializationError) as err:
        rs.model_dump()

    rs.even = "wrong"
    with pytest.raises(PydanticSerializationError):
        rs.model_dump()

    rs.even = "whole"
    rs.mode = "wrong"
    with pytest.raises(PydanticSerializationError):
        rs.model_dump()


# TODO: commented lines are in case we decide to reinstate the dtype argument in Dimensions
@pytest.mark.parametrize(
    ("rules", "dimensions", "dtype", "expected"),
    [
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, int, (20, 80)),
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, float, (20, 80)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, int, (18, 78)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, float, (18, 78)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, int, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, float, (20, 80)),
        # ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, int, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, float, (20, 80)),
        # ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, int, (20, 80)),
        ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, float, (20, 80)),
        # ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, int, (19, 79)),
        ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, float, (19, 79)),
        # ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, int, (20, 80)),
        ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, float, (20, 80)),
        # ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, int, (19, 79)),
        ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, float, (19, 79)),
    ],
)
def test_rounding_strategy_rounding(rules, dimensions, dtype, expected):
    rnd = pyfdl.rounding.RoundStrategy(**rules)
    dim = pyfdl.Dimensions[dtype](**dimensions)
    result = rnd.round_dimensions(dim)

    assert (result.width, result.height) == expected

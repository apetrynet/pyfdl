import pytest
from pydantic_core import PydanticSerializationError

import fdl
from fdl import config as config


def test_set_rounding_strategy():
    assert config.get_rounding() == fdl.config.DEFAULT_ROUNDING_STRATEGY

    override = fdl.rounding.RoundStrategy(even="whole", mode="up")
    config.set_rounding(override)
    assert config.get_rounding() == override


def test_rounding_strategy_validation():
    rs = fdl.rounding.RoundStrategy(even=None, mode=None)
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
    ("rules", "dimensions", "cls", "expected"),
    [
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, fdl.DimensionsInt, (20, 80)),
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, fdl.DimensionsFloat, (20, 80)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, fdl.DimensionsInt, (18, 78)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, fdl.DimensionsFloat, (18, 78)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, fdl.DimensionsInt, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, fdl.DimensionsFloat, (20, 80)),
        # ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, fdl.DimensionsInt, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, fdl.DimensionsFloat, (20, 80)),
        # ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsInt, (20, 80)),
        ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsFloat, (20, 80)),
        # ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsInt, (19, 79)),
        ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsFloat, (19, 79)),
        # ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsInt, (20, 80)),
        ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, fdl.DimensionsFloat, (20, 80)),
        # ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, fdl.DimensionsInt, (19, 79)),
        ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, fdl.DimensionsFloat, (19, 79)),
    ],
)
def test_rounding_strategy_rounding(rules, dimensions, cls, expected):
    rnd = fdl.rounding.RoundStrategy(**rules)
    dim = cls(**dimensions)
    result = rnd.round_dimensions(dim)

    assert (result.width, result.height) == expected

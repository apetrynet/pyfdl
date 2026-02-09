import math
from typing import TypeVar, Annotated, Literal, Union, get_args

from pydantic import BaseModel, Field, model_serializer

Dimensions = TypeVar("Dimensions")
Point = TypeVar("Point")

ValidEven = Literal["whole", "even"]
ValidMode = Literal["up", "down", "round"]


def fdl_round(value: float, even: str, mode: str) -> int:
    """Round a single float value according to FDL rounding rules.

    Handles negative values and rounding to whole or even numbers.

    Parameters
    ----------
    value : float
        The value to round.
    even : str
        Either "whole" or "even" to control rounding to whole or even numbers.
    mode : str
        Either "up", "down", or "round" to control rounding direction.

    Returns
    -------
    int
        The rounded value.
    """
    sign = 1
    if value < 0:
        sign = -1
        value = abs(value)

    if mode == "up":
        v = math.ceil(value)
    elif mode == "down":
        v = math.floor(value)
    else:  # round to nearest
        v = int(round(value))

    if even == "even":
        if mode == "up":
            v = v if v % 2 == 0 else v + 1
        elif mode == "down":
            v = v if v % 2 == 0 else v - 1
        else:
            if v % 2 != 0:
                up = v + 1
                down = v - 1
                v = up if abs(up - value) <= abs(down - value) else down

    return sign * v


class RoundStrategy(BaseModel):
    even: Annotated[Union[ValidEven, None], Field(default="even")]
    mode: Annotated[Union[ValidMode, None], Field(default="up")]

    @property
    def rules(self) -> dict:
        return self.model_dump()

    def round_dimensions(self, dimensions: Dimensions) -> Dimensions:
        """Round the provided dimensions based on the rules defined in this object.

        Uses fdl_round internally for consistent rounding behavior.
        """
        new_dim = dimensions.__class__()
        new_dim.width = fdl_round(dimensions.width, self.even, self.mode)
        new_dim.height = fdl_round(dimensions.height, self.even, self.mode)
        return new_dim

    def round_point(self, point: Point) -> Point:
        """Round the provided point based on the rules defined in this object.

        Uses fdl_round internally for consistent rounding behavior.
        """
        new_point = point.__class__()
        new_point.x = fdl_round(point.x, self.even, self.mode)
        new_point.y = fdl_round(point.y, self.even, self.mode)
        return new_point

    @model_serializer()
    def check_values(self) -> dict[str, str]:
        if self.even is None or self.even not in get_args(ValidEven):
            raise ValueError(
                f'"{self.even}" is not a valid option for even. '
                f"Please use one of the following: {get_args(ValidEven)}"
            )

        if self.mode is None or self.mode not in get_args(ValidMode):
            raise ValueError(
                f'"{self.mode}" is not a valid option for mode. '
                f"Please use one of the following: {get_args(ValidMode)}"
            )

        return {"even": self.even, "mode": self.mode}

    def __eq__(self, other):
        return self.even == other.even and self.mode == other.mode

    def __bool__(self):
        # Returns True when strategy has values (should be serialized)
        # Returns False when both are None (can be excluded)
        return self.even is not None or self.mode is not None

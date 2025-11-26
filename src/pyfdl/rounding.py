import math
from typing import TypeVar, Annotated, Literal, Union, get_args

from pydantic import BaseModel, Field, model_serializer

Dimensions = TypeVar("Dimensions")

ValidEven = Literal["whole", "even"]
ValidMode = Literal["up", "down", "round"]


class RoundStrategy(BaseModel):
    even: Annotated[Union[ValidEven, None], Field(default="even")]
    mode: Annotated[Union[ValidMode, None], Field(default="up")]

    @property
    def rules(self) -> dict:
        return self.model_dump()

    def round_dimensions(self, dimensions: Dimensions) -> Dimensions:
        """
        Round the provided dimensions based on the rules defined in this object

        Args:
            dimensions:

        Returns:
            dimensions: rounded based on rules

        """

        mode_map = {"up": math.ceil, "down": math.floor, "round": round}

        width = dimensions.width
        height = dimensions.height

        adjust = 1
        if self.even == "even":
            adjust = 2

        if self.mode is not None:
            width = mode_map[self.mode](width / adjust) * adjust
            height = mode_map[self.mode](height / adjust) * adjust

        new_dim = dimensions.__class__()
        new_dim.width = width
        new_dim.height = height

        return new_dim

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

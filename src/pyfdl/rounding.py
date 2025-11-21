import math
from typing import TypeVar, Annotated, Literal

from pydantic import BaseModel, Field, model_serializer

Dimensions = TypeVar("Dimensions")

ValidEven = Literal["whole", "even"]
ValidMode = Literal["up", "down", "round"]


class RoundStrategy(BaseModel):
    even: Annotated[ValidEven, Field(default="even")] = None
    mode: Annotated[ValidMode, Field(default="up")] = None

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

        return dimensions.__class__(width=width, height=height)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.even == other.get("even") and self.mode == other.get("mode")

        return self.even == other.even and self.mode == other.mode

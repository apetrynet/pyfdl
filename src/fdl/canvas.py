from typing import Union, Annotated

from pydantic import BaseModel, Field, field_validator, field_serializer

from fdl.common import TypedCollection
from fdl.types import DimensionsInt, DimensionsFloat, PointFloat
from fdl.framingdecision import FramingDecision
from fdl.framingintent import FramingIntent


class Canvas(BaseModel):
    label: Union[str, None] = None
    id: Annotated[str, Field(min_length=1, max_length=32)]
    source_canvas_id: Annotated[str, Field(min_length=1, max_length=32)]
    dimensions: Annotated[
        DimensionsInt,
        Field(default_factory=DimensionsInt, exclude_if=lambda dim: not dim),
    ]
    effective_dimensions: Union[DimensionsInt, None] = None
    effective_anchor_point: Union[PointFloat, None] = None
    photosite_dimensions: Union[DimensionsInt, None] = None
    physical_dimensions: Union[DimensionsFloat, None] = None
    anamorphic_squeeze: Annotated[float, Field(default=1)]
    framing_decisions: TypedCollection[FramingDecision] = TypedCollection[
        FramingDecision
    ]()

    def place_framing_intent(self, framing_intent: FramingIntent) -> str:
        """Create a new FramingDecision based on the provided FramingIntent
        and add it to the collection of framing decisions.

        Args:
            framing_intent: framing intent to place in canvas

        Returns:
            framing_decision_id: id of the newly created framing decision
        """
        framing_decision = FramingDecision.from_framing_intent(self, framing_intent)
        self.framing_decisions.append(framing_decision)

        return framing_decision.id

    def adjust_effective_anchor_point(self) -> None:
        """Adjust the `effective_anchor_point` of this `Canvas` if `effective_dimensions` are set."""
        if self.effective_dimensions is None:
            return

        self.effective_anchor_point = PointFloat(
            x=(self.dimensions.width - self.effective_dimensions.width) / 2,
            y=(self.dimensions.height - self.effective_dimensions.height) / 2,
        )

    @field_validator("effective_anchor_point", mode="after")
    @classmethod
    def _check_effective_dimensions(cls, value, info) -> PointFloat | None:
        if info.data.get("effective_dimensions") is not None:
            if value is None:
                raise ValueError(
                    "effective_anchor_point must be provided when effective_dimensions is present"
                )
        return value

    @field_serializer("effective_anchor_point")
    def _check_effective_anchor_point(
        self, point: PointFloat | None,
    ) -> PointFloat | None:
        if not self.effective_dimensions:
            return None

        if point is None:
            raise ValueError(
                "Effective anchor point is required when effective dimensions are provided"
            )
        return point

    def __eq__(self, other) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __hash__(self):
        return hash((self.id,))

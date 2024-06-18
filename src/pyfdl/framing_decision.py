from typing import Union

from pyfdl import Base, DimensionsFloat, Point, TypedCollection
from pyfdl.base import round_to_even


class FramingDecision(Base):
    attributes = [
        'label',
        'id',
        'framing_intent_id',
        'dimensions',
        'anchor_point',
        'protection_dimensions',
        'protection_anchor_point'
    ]
    kwarg_map = {'id': '_id'}
    object_map = {
        'dimensions': DimensionsFloat,
        'anchor_point': Point,
        'protection_dimensions': DimensionsFloat,
        'protection_anchor_point': Point
    }
    required = ['id', 'framing_intent_id', 'dimensions', 'anchor_point']

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            framing_intent_id: str = None,
            dimensions: DimensionsFloat = None,
            anchor_point: Point = None,
            protection_dimensions: DimensionsFloat = None,
            protection_anchor_point: Point = None
    ):
        self.label = label
        self.id = _id
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point

    @classmethod
    def from_framing_intent(cls, canvas: 'Canvas', framing_intent: 'FramingIntent') -> 'FramingDecision':
        framing_decision = FramingDecision(
            _id=f'{canvas.id}-{framing_intent.id}',
            label=framing_intent.label,
            framing_intent_id=framing_intent.id
        )

        active_dimensions, active_anchor_point = canvas.get_dimensions()

        # Compare aspect ratios of framing intent and canvas
        intent_aspect = framing_intent.aspect_ratio.width / framing_intent.aspect_ratio.height
        canvas_aspect = active_dimensions.width / active_dimensions.height
        if intent_aspect >= canvas_aspect:
            width = active_dimensions.width
            height = round_to_even((width * canvas.anamorphic_squeeze) / intent_aspect)
            # height = (width * self.anamorphic_squeeze) / intent_aspect

        else:
            width = round_to_even(active_dimensions.height * intent_aspect)
            # width = active_dimensions.height * intent_aspect
            height = active_dimensions.height

        if framing_intent.protection > 0:
            protection_dimensions = DimensionsFloat(width=width, height=height)
            protection_anchor_point = Point(
                x=active_anchor_point.x + (active_dimensions.width - protection_dimensions.width) / 2,
                y=active_anchor_point.y + (active_dimensions.height - protection_dimensions.height) / 2
            )
            framing_decision.protection_dimensions = protection_dimensions
            framing_decision.protection_anchor_point = protection_anchor_point

        # We use the protection dimensions as base for dimensions if they're set
        if framing_decision.protection_dimensions is not None:
            width = framing_decision.protection_dimensions.width
            height = framing_decision.protection_dimensions.height

        dimensions = DimensionsFloat(
            width=round_to_even(width * (1 - framing_intent.protection)),
            height=round_to_even(height * (1 - framing_intent.protection))
        )
        framing_decision.dimensions = dimensions

        offset_point = framing_decision.protection_anchor_point or active_anchor_point
        offset_dimensions = framing_decision.protection_dimensions or dimensions

        anchor_point = Point(
            x=offset_point.x + (offset_dimensions.width - dimensions.width) / 2,
            y=offset_point.y + (offset_dimensions.height - dimensions.height) / 2
        )
        framing_decision.anchor_point = anchor_point

        return framing_decision

    def __eq__(self, other):
        return (
                self.id == other.id and
                self.dimensions == other.dimensions and
                self.anchor_point == other.anchor_point and
                self.protection_dimensions == other.protection_dimensions and
                self.protection_anchor_point == other.protection_anchor_point
        )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'label="{self.label}", id="{self.id}", framing_intent_id="{self.framing_intent_id}"'
            f')'
        )

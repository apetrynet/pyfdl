from typing import Union, Type

from pyfdl import Base, DimensionsFloat, Point, TypedCollection


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
            protection_anchor_point: Point = None,
            parent: TypedCollection = None
    ):
        self.parent = parent
        self.label = label
        self.id = _id
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point

    @property
    def parent(self) -> Union[TypedCollection, None]:
        return self._parent

    @parent.setter
    def parent(self, parent: TypedCollection):
        self._parent = parent

    # TODO this should perhaps live in Canvas? Canvas.new_framing_decision()
    @classmethod
    def new(cls, canvas: Type['Canvas'], framing_intent: Type['FramingIntent']) -> 'FramingDecision':
        canvas_dimensions, canvas_anchor_point = canvas.get_dimensions()
        aspect_quotient = framing_intent.aspect_ratio.height / framing_intent.aspect_ratio.width
        protection_dimensions = DimensionsFloat(
            width=canvas_dimensions.width,
            height=canvas_dimensions.width * canvas.anamorphic_squeeze * aspect_quotient
        )
        fd = FramingDecision(
            _id=f'{canvas.id}-{framing_intent.id}',
            framing_intent_id=framing_intent.id,
            protection_dimensions=protection_dimensions,
            protection_anchor_point=anchor_point
        )

        return fd

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'label="{self.label}", id="{self.id}", framing_intent_id="{self.framing_intent_id}"'
            f')'
        )

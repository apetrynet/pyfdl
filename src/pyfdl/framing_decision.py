from pyfdl import Base, DimensionsFloat, Point


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

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'label="{self.label}", id="{self.id}", framing_intent_id="{self.framing_intent_id}"'
            f')'
        )

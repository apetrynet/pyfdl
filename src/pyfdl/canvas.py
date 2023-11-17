from pyfdl import DimensionsInt, PointFloat, DimensionsFloat, FramingDecision
from pyfdl.base import Base


class Canvas(Base):
    attributes = [
        'label',
        'id',
        'source_canvas_id',
        'dimensions',
        'effective_dimensions',
        'effective_anchor_point',
        'photosite_dimensions',
        'physical_dimensions',
        'anamorphic_squeeze',
        'framing_decisions'
    ]
    kwarg_map = {'id': '_id'}
    object_map = {
        'dimensions': DimensionsInt,
        'effective_dimensions': DimensionsInt,
        'effective_anchor_point': PointFloat,
        'photosite_dimensions': DimensionsInt,
        'physical_dimensions': DimensionsFloat,
        'framing_decisions': FramingDecision
    }
    required = ['id', 'source_canvas_id', 'dimensions', 'effective_dimensions.effective_anchor_point']
    defaults = {'anamorphic_squeeze': 1}

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            source_canvas_id: str = None,
            dimensions: DimensionsInt = None,
            effective_dimensions: DimensionsInt = None,
            effective_anchor_point: PointFloat = None,
            photosite_dimensions: DimensionsInt = None,
            physical_dimensions: DimensionsFloat = None,
            anamorphic_squeeze: float = None,
            framing_decisions: list = None
    ):
        self.label = label
        self.id = _id
        self.source_canvas_id = source_canvas_id or self.id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze
        self.framing_decisions = framing_decisions or []

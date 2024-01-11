from typing import Union

from pyfdl import Base, DimensionsInt, Point, DimensionsFloat, FramingDecision, TypedContainer
from pyfdl.errors import FDLError


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
        'effective_anchor_point': Point,
        'photosite_dimensions': DimensionsInt,
        'physical_dimensions': DimensionsFloat,
        'framing_decisions': FramingDecision
    }
    required = ['id', 'source_canvas_id', 'dimensions', 'effective_dimensions.effective_anchor_point']
    defaults = {'source_canvas_id': 'self.id', 'anamorphic_squeeze': 1}

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            source_canvas_id: str = None,
            dimensions: DimensionsInt = None,
            effective_dimensions: DimensionsInt = None,
            effective_anchor_point: Point = None,
            photosite_dimensions: DimensionsInt = None,
            physical_dimensions: DimensionsFloat = None,
            anamorphic_squeeze: float = None,
            framing_decisions: TypedContainer = None,
            parent: TypedContainer = None
    ):
        self.parent = parent
        self.label = label
        self.id = _id
        self.source_canvas_id = source_canvas_id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze
        self.framing_decisions = framing_decisions or TypedContainer(FramingDecision)

    @property
    def parent(self) -> Union[TypedContainer, None]:
        return self._parent

    @parent.setter
    def parent(self, parent: TypedContainer):
        self._parent = parent

    @property
    def source_canvas_id(self) -> str:
        return self._source_canvas_id

    @source_canvas_id.setter
    def source_canvas_id(self, canvas_id: str):
        if not canvas_id:
            return

        if self.parent and canvas_id in self.parent or canvas_id == self.id:
            self._source_canvas_id = canvas_id

        else:
            raise FDLError(
                f'"source_canvas_id" {canvas_id} must either be self.id or the id of another canvas in '
                f'the registered canvases. {self.parent}'
            )

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id}")'

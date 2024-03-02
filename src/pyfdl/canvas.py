from typing import Union, Tuple, Type

from pyfdl import Base, DimensionsInt, Point, DimensionsFloat, FramingDecision, TypedCollection, FramingIntent
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
            framing_decisions: TypedCollection = None,
            parent: TypedCollection = None
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
        self.framing_decisions = framing_decisions or TypedCollection(FramingDecision)

    def place_framing_intent(self, framing_intent: FramingIntent) -> str:
        """Create a new [FramingDecision](framing_decision.md#Framing Decision) based on the provided
        [FramingIntent](framing_intent.md#Framing Intent) and add it to the
        collection of framing decisions.

        The framing decision's properties are calculated for you.
        If the canvas has effective dimensions set, these will be used for the calculations. Otherwise, we use the
        dimensions

        Args:
            framing_intent: framing intent to place in canvas

        Returns:
            framing_decision_id: id of the newly created framing decision

        """
        active_dimensions, active_anchor_point = self.get_dimensions()

        # Compare aspect ratios of canvas and framing intent
        intent_quotient = framing_intent.aspect_ratio.width / framing_intent.aspect_ratio.height
        canvas_quotient = active_dimensions.width / active_dimensions.height
        if intent_quotient >= canvas_quotient:
            # Need to calculate height
            aspect_quotient = framing_intent.aspect_ratio.height / framing_intent.aspect_ratio.width
            width = active_dimensions.width
            # This trick was mentioned in a ASC MITC FDL meeting by someone, but I can't recall by whom
            height = round((width * self.anamorphic_squeeze * aspect_quotient) / 2) * 2

        else:
            # Need to calculate width
            width = round((active_dimensions.height * intent_quotient) / 2) * 2
            height = active_dimensions.height

        decision_id = f'{self.id}-{framing_intent.id}'
        protection_dimensions = DimensionsFloat(width=width, height=height)
        protection_anchor_point = Point(
            x=(active_dimensions.width - protection_dimensions.width) / 2,
            y=(active_dimensions.height - protection_dimensions.height) / 2
        )
        dimensions = DimensionsFloat(
            width=round(protection_dimensions.width * (1 - framing_intent.protection) / 2) * 2,
            height=round(protection_dimensions.height * (1 - framing_intent.protection) / 2) * 2
        )
        anchor_point = Point(
            x=protection_anchor_point.x + (protection_dimensions.width - dimensions.width) / 2,
            y=protection_anchor_point.y + (protection_dimensions.height - dimensions.height) / 2
        )
        framing_decision = FramingDecision(
            _id=decision_id,
            label=framing_intent.label,
            framing_intent_id=framing_intent.id,
            dimensions=dimensions,
            anchor_point=anchor_point,
            protection_dimensions=protection_dimensions,
            protection_anchor_point=protection_anchor_point
        )
        self.framing_decisions.add_item(framing_decision)

        return decision_id

    def get_dimensions(self) -> Tuple[DimensionsInt, Point]:
        """ Get the most relevant dimensions and anchor point for the canvas.
        `effective_dimensions` and `effective_anchor_point` win over `dimensions`

        Returns:
            (dimensions, anchor_point):

        """
        if self.effective_dimensions:
            return self.effective_dimensions, self.effective_anchor_point

        return self.dimensions, Point(x=0, y=0)

    @property
    def parent(self) -> Union[TypedCollection, None]:
        return self._parent

    @parent.setter
    def parent(self, parent: TypedCollection):
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

from typing import Tuple, Type, Union, List

from pyfdl import Base, DimensionsInt, Point, DimensionsFloat, FramingDecision, TypedCollection, FramingIntent
from pyfdl.base import round_to_even
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
            framing_decisions: TypedCollection = None
    ):
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
        framing_decision = FramingDecision.from_framing_intent(self, framing_intent)
        self.framing_decisions.add_item(framing_decision)

        return framing_decision.id

    def get_dimensions(self) -> Tuple[DimensionsInt, Point]:
        """ Get the most relevant dimensions and anchor point for the canvas.
        `effective_dimensions` and `effective_anchor_point` win over `dimensions`

        Returns:
            (dimensions, anchor_point):

        """
        if self.effective_dimensions is not None:
            return self.effective_dimensions, self.effective_anchor_point

        return self.dimensions, Point(x=0, y=0)

    @classmethod
    def from_canvas_template(
            cls,
            canvas_template: 'CanvasTemplate',
            source_canvas: 'Canvas',
            source_framing_decision: Union[FramingDecision, int] = 0,
            framing_intent: FramingIntent = None
    ) -> 'Canvas':

        if type(source_framing_decision) is int:
            source_framing_decision = source_canvas.framing_decisions[source_framing_decision]

        steps = {
            "framing_decision.dimensions": source_framing_decision.dimensions,
            "framing_decision.protection_dimensions": source_framing_decision.protection_dimensions,
            "canvas.effective_dimensions": source_canvas.effective_dimensions,
            "canvas.dimensions": source_canvas.dimensions,
        }

        def get_steps(beg: str, end: str) -> List:
            keys = list(steps.keys())
            first = keys.index(beg) + 1
            last = keys.index(end)
            return keys[first:last]

        canvas = Canvas(
            label=canvas_template.label,
            _id=Base.generate_uuid().strip('-'),
            source_canvas_id=source_canvas.id,
            anamorphic_squeeze=canvas_template.target_anamorphic_squeeze
        )

        source_map = {
            'framing_decision': source_framing_decision,
            'canvas': source_canvas
        }

        # Figure out what dimensions to use
        fit_source = canvas_template.fit_source
        source_type, source_attribute = fit_source.split('.')

        # Map fit_source into target dimensions
        source_dimensions = getattr(source_map[source_type], source_attribute)
        scaled_size, scale_factor = canvas_template.fit_source_to_target(
            source_dimensions,
            source_canvas.anamorphic_squeeze
        )

        # If preserve_from_source_canvas contains "canvas", scale canvas dimensions first and apply to
        preserve = canvas_template.preserve_from_source_canvas
        if preserve is None or preserve == 'none':
            canvas_dimensions = canvas_template.target_dimensions.copy()

        else:
            preserve_source_type, preserve_source_attribute = preserve.split('.')
            source_canvas_dimensions = getattr(source_map[preserve_source_type], preserve_source_attribute).copy()

            canvas_dimensions = source_canvas_dimensions.copy()
            canvas_dimensions.width *= source_canvas.anamorphic_squeeze
            canvas_dimensions.scale_by(scale_factor)

        canvas.dimensions = canvas_dimensions
        framing_decision_id = canvas.place_framing_intent(framing_intent)
        framing_decision = canvas.framing_decisions.get_item(framing_decision_id)

        dest_map = {
            'framing_decision': framing_decision,
            'canvas': canvas
        }

        # Add remaining dimensions
        keys = get_steps(fit_source, preserve)
        for step in keys:
            source_type, source_attribute = step.split('.')
            value = getattr(source_map[source_type], source_attribute).copy()
            value.width = canvas_template.get_desqueezed_width(value.width, source_canvas.anamorphic_squeeze)
            value.scale_by(scale_factor)
            setattr(dest_map[source_type], source_attribute, value)

        # TODO: implement align horizonatal/vertical
        # TODO implement maximum_dimensions
        # TODO implement pad_to_maximum
        # TODO implement round
        canvas.adjust_effective_anchor_point()
        framing_decision.adjust_protection_anchor_point(canvas)
        framing_decision.adjust_anchor_point(canvas)

        print(canvas.to_dict())

        return canvas

    def adjust_effective_anchor_point(self) -> None:
        if self.effective_dimensions is None:
            return

        self.effective_anchor_point = Point(
            x=(self.dimensions.width - self.effective_dimensions.width) / 2,
            y=(self.dimensions.height - self.effective_dimensions.height) / 2
        )

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id}")'

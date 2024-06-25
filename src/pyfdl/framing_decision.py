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
    kwarg_map = {'id': 'id_'}
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
            id_: str = None,
            framing_intent_id: str = None,
            dimensions: DimensionsFloat = None,
            anchor_point: Point = None,
            protection_dimensions: DimensionsFloat = None,
            protection_anchor_point: Point = None
    ):
        self.label = label
        self.id = id_
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point

        # Make sure we have a rounding strategy
        if Base.rounding_strategy is None:
            Base.set_rounding_strategy()

    @classmethod
    def from_framing_intent(cls, canvas: 'Canvas', framing_intent: 'FramingIntent') -> 'FramingDecision':
        """
        Create a new [FramingDecision](framing_decision.md#Framing Decision) based on the provided
        [Canvas](canvas.md#Canvas) and [FramingIntent](framing_intent.md#Framing Intent)

        The framing decision's properties are calculated for you.
        If the canvas has effective dimensions set, these will be used for the calculations.
        Otherwise, we use the dimensions

        Args:
            canvas: canvas to base framing decision on
            framing_intent: framing intent to place in canvas

        Returns:
            framing_decision:

        """
        framing_decision = FramingDecision(
            id_=f'{canvas.id}-{framing_intent.id}',
            label=framing_intent.label,
            framing_intent_id=framing_intent.id
        )

        active_dimensions, active_anchor_point = canvas.get_dimensions()

        # Compare aspect ratios of framing intent and canvas
        intent_aspect = framing_intent.aspect_ratio.width / framing_intent.aspect_ratio.height
        canvas_aspect = active_dimensions.width / active_dimensions.height
        if intent_aspect >= canvas_aspect:
            width = active_dimensions.width
            height = (width * canvas.anamorphic_squeeze) / intent_aspect

        else:
            width = active_dimensions.height * intent_aspect
            height = active_dimensions.height

        if framing_intent.protection > 0:
            protection_dimensions = DimensionsFloat(width=width, height=height)
            framing_decision.protection_dimensions = cls.rounding_strategy.round_dimensions(
                protection_dimensions
            )
            framing_decision.adjust_protection_anchor_point(canvas)

        # We use the protection dimensions as base for dimensions if they're set
        if framing_decision.protection_dimensions is not None:
            width = framing_decision.protection_dimensions.width
            height = framing_decision.protection_dimensions.height

        dimensions = DimensionsFloat(
            width=width * (1 - framing_intent.protection),
            height=height * (1 - framing_intent.protection)
        )
        framing_decision.dimensions = cls.rounding_strategy.round_dimensions(dimensions)
        framing_decision.adjust_anchor_point(canvas)

        return framing_decision

    def adjust_anchor_point(
            self, canvas: 'Canvas',
            h_method: str = 'center',
            v_method: str = 'center'
    ) -> None:
        """
        Adjust this object's `anchor_point` either relative to `protection_anchor_point`
        or `canvas.effective_anchor_point`
        Please note that the `h_method` and `v_method` arguments only apply if no
        `protection_anchor_point` is present.

        Args:
            canvas: to fetch anchor point from in case protection_anchor_point is not set
            h_method: horizontal alignment ('left', 'center', 'right')
            v_method: vertical alignment ('top', 'center', 'bottom')
        """

        # TODO check if anchor point is shifted before centering
        _, active_anchor_point = canvas.get_dimensions()

        offset_point = self.protection_anchor_point or active_anchor_point
        offset_dimensions = self.protection_dimensions or self.dimensions

        x = offset_point.x
        y = offset_point.y

        if self.protection_anchor_point:
            x += (offset_dimensions.width - self.dimensions.width) / 2
            y += (offset_dimensions.height - self.dimensions.height) / 2

        else:
            if h_method == 'center':
                x += (offset_dimensions.width - self.dimensions.width) / 2

            elif h_method == 'right':
                x += (offset_dimensions.width - self.dimensions.width)

            if v_method == 'center':
                y += (offset_dimensions.height - self.dimensions.height) / 2

            elif v_method == 'bottom':
                y += (offset_dimensions.height - self.dimensions.height)

        self.anchor_point = Point(x=x, y=y)

    def adjust_protection_anchor_point(
            self,
            canvas: 'Canvas',
            h_method: str = 'center',
            v_method: str = 'center'
    ) -> None:
        """
        Adjust this object's `protection_anchor_point` if `protection_dimensions` are set.
        Please note that the `h_method` and `v_method` are primarily used when creating a canvas based on
        a [canvas template](canvas.md#from_canvas_template)

        Args:
            canvas: to fetch anchor point from in case protection_anchor_point is not set
            h_method: horizontal alignment ('left', 'center', 'right')
            v_method: vertical alignment ('top', 'center', 'bottom')
        """

        if self.protection_dimensions is None:
            return

        active_dimensions, active_anchor_point = canvas.get_dimensions()
        x = active_anchor_point.x
        y = active_anchor_point.y

        if h_method == 'center':
            x += (active_dimensions.width - self.protection_dimensions.width) / 2

        elif h_method == 'right':
            x += (active_dimensions.width - self.protection_dimensions.width)

        if v_method == 'center':
            y += (active_dimensions.height - self.protection_dimensions.height) / 2

        elif v_method == 'bottom':
            y += (active_dimensions.height - self.protection_dimensions.height)

        self.protection_anchor_point = Point(x=x, y=y)

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

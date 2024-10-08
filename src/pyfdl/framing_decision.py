from typing import Optional, TypeVar, Union

from .common import Base, Dimensions, Point, rounding_strategy

Canvas = TypeVar("Canvas")
FramingIntent = TypeVar("FramingIntent")


class FramingDecision(Base):
    def __init__(
        self,
        label: Optional[str] = None,
        id_: Optional[str] = None,
        framing_intent_id: Optional[str] = None,
        dimensions: Optional[Dimensions] = None,
        anchor_point: Optional[Point] = None,
        protection_dimensions: Optional[Dimensions] = None,
        protection_anchor_point: Optional[Point] = None,
    ):
        super().__init__()
        self.attributes = [
            "label",
            "id",
            "framing_intent_id",
            "dimensions",
            "anchor_point",
            "protection_dimensions",
            "protection_anchor_point",
        ]
        self.kwarg_map = {"id": "id_"}
        self.object_map = {
            "dimensions": Dimensions,
            "anchor_point": Point,
            "protection_dimensions": Dimensions,
            "protection_anchor_point": Point,
        }
        self.required = ["id", "framing_intent_id", "dimensions", "anchor_point"]

        self.label = label
        self.id = id_
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point

    @property
    def dimensions(self) -> Union[Dimensions, None]:
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dim: Union[Dimensions, None]):
        self._dimensions = dim

    @property
    def protection_dimensions(self) -> Union[Dimensions, None]:
        return self._protection_dimensions

    @protection_dimensions.setter
    def protection_dimensions(self, dim: Union[Dimensions, None]):
        self._protection_dimensions = dim

    @classmethod
    def from_framing_intent(cls, canvas: Canvas, framing_intent: FramingIntent) -> "FramingDecision":
        """
        Create a new [FramingDecision](framing_decision.md#pyfdl.FramingDecision) based on the provided
        [Canvas](canvas.md#pyfdl.Canvas) and [FramingIntent](framing_intent.md#pyfdl.FramingIntent)

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
            id_=f"{canvas.id}-{framing_intent.id}", label=framing_intent.label, framing_intent_id=framing_intent.id
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
            protection_dimensions = Dimensions(width=width, height=height)
            framing_decision.protection_dimensions = rounding_strategy().round_dimensions(protection_dimensions)
            framing_decision.adjust_protection_anchor_point(canvas)

        # We use the protection dimensions as base for dimensions if they're set
        if framing_decision.protection_dimensions is not None:
            width = framing_decision.protection_dimensions.width
            height = framing_decision.protection_dimensions.height

        dimensions = Dimensions(
            width=width * (1 - framing_intent.protection), height=height * (1 - framing_intent.protection)
        )
        framing_decision.dimensions = rounding_strategy().round_dimensions(dimensions)
        framing_decision.adjust_anchor_point(canvas)

        return framing_decision

    def adjust_anchor_point(self, canvas: Canvas, h_method: str = "center", v_method: str = "center") -> None:
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

        # TODO: check if anchor point is shifted before centering
        active_dimensions, active_anchor_point = canvas.get_dimensions()

        offset_point = self.protection_anchor_point or active_anchor_point
        offset_dimensions = self.protection_dimensions or active_dimensions

        x = offset_point.x
        y = offset_point.y

        if self.protection_anchor_point:
            x += (offset_dimensions.width - self.dimensions.width) / 2
            y += (offset_dimensions.height - self.dimensions.height) / 2

        else:
            if h_method == "center":
                x += (offset_dimensions.width - self.dimensions.width) / 2

            elif h_method == "right":
                x += offset_dimensions.width - self.dimensions.width

            if v_method == "center":
                y += (offset_dimensions.height - self.dimensions.height) / 2

            elif v_method == "bottom":
                y += offset_dimensions.height - self.dimensions.height

        self.anchor_point = Point(x=x, y=y)

    def adjust_protection_anchor_point(
        self, canvas: Canvas, h_method: str = "center", v_method: str = "center"
    ) -> None:
        """
        Adjust this object's `protection_anchor_point` if `protection_dimensions` are set.
        Please note that the `h_method` and `v_method` are primarily used when creating a canvas based on
        a [canvas template](canvas.md#pyfdl.Canvas.from_canvas_template)

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

        if h_method == "center":
            x += (active_dimensions.width - self.protection_dimensions.width) / 2

        elif h_method == "right":
            x += active_dimensions.width - self.protection_dimensions.width

        if v_method == "center":
            y += (active_dimensions.height - self.protection_dimensions.height) / 2

        elif v_method == "bottom":
            y += active_dimensions.height - self.protection_dimensions.height

        self.protection_anchor_point = Point(x=x, y=y)

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.dimensions == other.dimensions
            and self.anchor_point == other.anchor_point
            and self.protection_dimensions == other.protection_dimensions
            and self.protection_anchor_point == other.protection_anchor_point
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f'label="{self.label}", id="{self.id}", framing_intent_id="{self.framing_intent_id}"'
            f")"
        )

import uuid
from typing import Union, Annotated, Self, TypeVar

from pydantic import BaseModel, Field, field_validator, field_serializer

from pyfdl.common import Dimensions, Point, TypedCollection
from pyfdl.framingdecision import FramingDecision
from pyfdl.framingintent import FramingIntent


CanvasTemplate = TypeVar("CanvasTemplate")


class Canvas(BaseModel):
    label: Union[str, None] = None
    id: str
    source_canvas_id: str   # TODO: make sure it exists
    dimensions: Annotated[Dimensions[int], Field(default=Dimensions[int](), exclude_if=lambda dim: not dim)]
    effective_dimensions: Union[Dimensions[int]] = None
    effective_anchor_point: Union[Point[float]] = None
    photosite_dimensions: Union[Dimensions[int]] = None
    physical_dimensions: Union[Dimensions[float]] = None
    anamorphic_squeeze: Annotated[float, Field(default=1)]
    framing_decisions: TypedCollection[FramingDecision] = TypedCollection[FramingDecision]()

    def place_framing_intent(self, framing_intent: FramingIntent) -> str:
        """Create a new [FramingDecision](framing_decision.md#pyfdl.FramingDecision) based on the provided
        [FramingIntent](framing_intent.md#pyfdl.FramingIntent) and add it to the
        collection of framing decisions.

        The framing decision's properties are calculated for you.
        If the canvas has effective dimensions set, these will be used for the calculations.
        Otherwise, we use the dimensions

        Args:
            framing_intent: framing intent to place in canvas

        Returns:
            framing_decision_id: id of the newly created framing decision

        """
        framing_decision = FramingDecision.from_framing_intent(self, framing_intent)
        self.framing_decisions.append(framing_decision)

        return framing_decision.id

    @classmethod
    def from_canvas_template(
            cls,
            canvas_template: CanvasTemplate,
            source_canvas: Self,
            source_framing_decision: Union[FramingDecision, int] = 0,
    ) -> Self:
        """
        Create a new `Canvas` from the provided `source_canvas` and `framing_decision`
        based on a [CanvasTemplate](canvas_template.md#pyfdl.CanvasTemplate)

        Args:
            canvas_template: describing how to handle incoming `Canvas` and `FramingDecision`
            source_canvas: to use as base for new canvas
            source_framing_decision: either a `FramingDecision` from the source canvas or the index (`int`) of one.

        Returns:
            canvas: based on the provided canvas template and sources

        """
        if isinstance(source_framing_decision, int):
            source_framing_decision = source_canvas.framing_decisions[source_framing_decision]

        canvas = Canvas(
            label=canvas_template.label,
            id=str(uuid.uuid4()).replace("-", ""),
            source_canvas_id=source_canvas.id,
            anamorphic_squeeze=canvas_template.target_anamorphic_squeeze,
        )

        framing_decision = FramingDecision(
            label=source_framing_decision.label,
            id=f"{canvas.id}-{source_framing_decision.framing_intent_id}",
            framing_intent_id=source_framing_decision.framing_intent_id,
        )
        canvas.framing_decisions.append(framing_decision)

        source_map = {"framing_decision": source_framing_decision, "canvas": source_canvas}

        dest_map = {"framing_decision": framing_decision, "canvas": canvas}

        # Figure out what dimensions to use
        fit_source = canvas_template.fit_source
        source_type, source_attribute = fit_source.split(".")
        preserve = canvas_template.preserve_from_source_canvas or fit_source
        if preserve in [None, "none"]:
            preserve = fit_source

        # Get the scale factor
        source_dimensions = getattr(source_map[source_type], source_attribute)
        scale_factor = canvas_template.get_scale_factor(source_dimensions, source_canvas.anamorphic_squeeze)

        # Dummy dimensions to test against if we received a proper value
        dummy_dimensions = Dimensions[int](width=0, height=0)

        # Copy and scale dimensions from source to target
        for transfer_key in canvas_template.get_transfer_keys():
            if transfer_key == fit_source:
                target_size = canvas_template.fit_source_to_target(source_dimensions, source_canvas.anamorphic_squeeze)
                setattr(dest_map[source_type], source_attribute, target_size)
                continue

            source_type, dimension_source_attribute = transfer_key.split(".")
            dimensions = getattr(source_map[source_type], dimension_source_attribute, dummy_dimensions).duplicate()

            if dimensions == dummy_dimensions:
                # Source canvas/framing decision is missing this dimension. Let's move on
                continue

            dimensions.width = canvas_template.get_desqueezed_width(dimensions.width, source_canvas.anamorphic_squeeze)
            dimensions.scale_by(scale_factor)
            setattr(dest_map[source_type], dimension_source_attribute, dimensions)

        # Make sure the canvas has dimensions
        if not canvas.dimensions:
            preserve_source_type, preserve_source_attribute = preserve.split(".")
            canvas.dimensions = getattr(dest_map[preserve_source_type], preserve_source_attribute).duplicate()

        # Round values according to rules defined in the template
        if canvas_template.round is not None:
            canvas.dimensions = canvas_template.round.round_dimensions(canvas.dimensions)

        # Override canvas dimensions to maximum defined in template
        if canvas_template.maximum_dimensions is not None:
            canvas.dimensions = min(canvas_template.maximum_dimensions, canvas.dimensions)
            if canvas_template.pad_to_maximum:
                canvas.dimensions = canvas_template.maximum_dimensions

        # Make sure all anchor points are correct according to new sizes
        canvas.adjust_effective_anchor_point()
        framing_decision.adjust_protection_anchor_point(
            canvas, canvas_template.alignment_method_horizontal, canvas_template.alignment_method_vertical
        )
        framing_decision.adjust_anchor_point(
            canvas, canvas_template.alignment_method_horizontal, canvas_template.alignment_method_vertical
        )

        return canvas

    def adjust_effective_anchor_point(self) -> None:
        """
        Adjust the `effective_anchor_point` of this `Canvas` if `effective_dimensions` are set
        """

        if self.effective_dimensions is None:
            return

        self.effective_anchor_point = Point(
            x=(self.dimensions.width - self.effective_dimensions.width) / 2,
            y=(self.dimensions.height - self.effective_dimensions.height) / 2,
        )

    @field_validator("effective_anchor_point", mode="after")
    @classmethod
    def _check_effective_dimensions(cls, value, info) -> Point[float]:
        if info.data.get("effective_dimensions") is not None:
            if value is None:
                raise ValueError(
                    "effective_anchor_point must be provided when effective_dimensions is present"
                )

        return value

    @field_serializer("effective_anchor_point")
    def _check_effective_anchor_point(self, point: Point[float]) -> Union[Point[float], None]:
        if self.effective_dimensions is None:
            return None

        if point is None:
            raise ValueError("Effective anchor point is required when effective dimensions are provided")

        return point

    def __eq__(self, other) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __hash__(self):
        return hash((self.id,))

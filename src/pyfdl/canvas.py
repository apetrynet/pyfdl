from typing import Optional, TypeVar, Union

from .common import Base, Dimensions, Point, TypedCollection
from .framing_decision import FramingDecision
from .framing_intent import FramingIntent

CanvasTemplate = TypeVar("CanvasTemplate")


class Canvas(Base):
    def __init__(
        self,
        label: Optional[str] = None,
        id_: Optional[str] = None,
        source_canvas_id: Optional[str] = None,
        dimensions: Optional[Dimensions] = None,
        effective_dimensions: Optional[Dimensions] = None,
        effective_anchor_point: Optional[Point] = None,
        photosite_dimensions: Optional[Dimensions] = None,
        physical_dimensions: Optional[Dimensions] = None,
        anamorphic_squeeze: Optional[float] = None,
        framing_decisions: Optional[TypedCollection] = None,
    ):
        super().__init__()
        self.attributes = [
            "label",
            "id",
            "source_canvas_id",
            "dimensions",
            "effective_dimensions",
            "effective_anchor_point",
            "photosite_dimensions",
            "physical_dimensions",
            "anamorphic_squeeze",
            "framing_decisions",
        ]
        self.kwarg_map = {"id": "id_"}
        self.object_map = {
            "dimensions": Dimensions,
            "effective_dimensions": Dimensions,
            "effective_anchor_point": Point,
            "photosite_dimensions": Dimensions,
            "physical_dimensions": Dimensions,
            "framing_decisions": FramingDecision,
        }
        self.required = ["id", "source_canvas_id", "dimensions", "effective_dimensions.effective_anchor_point"]
        self.defaults = {"source_canvas_id": "self.id", "anamorphic_squeeze": 1}

        self.label = label
        self.id = id_
        self.source_canvas_id = source_canvas_id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze
        self.framing_decisions = framing_decisions or TypedCollection(FramingDecision)

    @property
    def dimensions(self) -> Union[Dimensions, None]:
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dim: Union[Dimensions, None]):
        self._dimensions = dim
        if dim is not None:
            self._dimensions.dtype = int

    @property
    def effective_dimensions(self) -> Union[Dimensions, None]:
        return self._effective_dimensions

    @effective_dimensions.setter
    def effective_dimensions(self, dim: Union[Dimensions, None]):
        self._effective_dimensions = dim
        if dim is not None:
            self._effective_dimensions.dtype = int

    @property
    def photosite_dimensions(self) -> Union[Dimensions, None]:
        return self._photosite_dimensions

    @photosite_dimensions.setter
    def photosite_dimensions(self, dim: Union[Dimensions, None]):
        self._photosite_dimensions = dim
        if dim is not None:
            self._photosite_dimensions.dtype = int

    @property
    def physical_dimensions(self) -> Union[Dimensions, None]:
        return self._physical_dimensions

    @physical_dimensions.setter
    def physical_dimensions(self, dim: Union[Dimensions, None]):
        self._physical_dimensions = dim

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
        self.framing_decisions.add(framing_decision)

        return framing_decision.id

    def get_dimensions(self) -> tuple[Dimensions, Point]:
        """Get the most relevant dimensions and anchor point for the canvas.
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
        canvas_template: CanvasTemplate,
        source_canvas: "Canvas",
        source_framing_decision: Union[FramingDecision, int] = 0,
    ) -> "Canvas":
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
            id_=Base.generate_uuid().replace("-", ""),
            source_canvas_id=source_canvas.id,
            anamorphic_squeeze=canvas_template.target_anamorphic_squeeze,
        )

        framing_decision = FramingDecision(
            label=source_framing_decision.label,
            id_=f"{canvas.id}-{source_framing_decision.framing_intent_id}",
            framing_intent_id=source_framing_decision.framing_intent_id,
        )
        canvas.framing_decisions.add(framing_decision)

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
        dummy_dimensions = Dimensions(width=0, height=0)

        # Copy and scale dimensions from source to target
        for transfer_key in canvas_template.get_transfer_keys():
            if transfer_key == fit_source:
                target_size = canvas_template.fit_source_to_target(source_dimensions, source_canvas.anamorphic_squeeze)
                setattr(dest_map[source_type], source_attribute, target_size)
                continue

            source_type, dimension_source_attribute = transfer_key.split(".")
            dimensions = getattr(source_map[source_type], dimension_source_attribute, dummy_dimensions).copy()

            if dimensions == dummy_dimensions:
                # Source canvas/framing decision is missing this dimension. Let's move on
                continue

            dimensions.width = canvas_template.get_desqueezed_width(dimensions.width, source_canvas.anamorphic_squeeze)
            dimensions.scale_by(scale_factor)
            setattr(dest_map[source_type], dimension_source_attribute, dimensions)

        # Make sure the canvas has dimensions
        if canvas.dimensions is None:
            preserve_source_type, preserve_source_attribute = preserve.split(".")
            canvas.dimensions = getattr(dest_map[preserve_source_type], preserve_source_attribute).copy()

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

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id}")'

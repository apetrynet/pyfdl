from typing import Literal, Union, Annotated

from pydantic import BaseModel, Field

from pyfdl.common import Dimensions
from pyfdl.rounding import RoundStrategy


FitSource = Literal[
    "framing_decision.dimensions",
    "framing_decision.protection_dimensions",
    "canvas.dimensions",
    "canvas.effective_dimensions"
]
FitMethod = Literal["width", "height", "fit_all", "fill"]
AlignmentMethodVertical = Literal["top", "center", "bottom"]
AlignmentMethodHorizontal = Literal["left", "center", "right"]
PreserveFromSource = Literal[
    "none",
    "framing_decision.dimensions",
    "framing_decision.protection_dimensions",
    "canvas.dimensions",
    "canvas.effective_dimensions"
]


class CanvasTemplate(BaseModel):
    label: Union[str, None] = None
    id: str
    target_dimensions: Dimensions[int]
    target_anamorphic_squeeze: Annotated[float, Field(ge=0, default=1)]
    fit_source: Annotated[FitSource, Field(default="framing_decision.dimensions")]
    fit_method: Annotated[FitMethod, Field(default="width")]
    alignment_method_vertical: Annotated[AlignmentMethodVertical, Field(default="center")]
    alignment_method_horizontal: Annotated[AlignmentMethodHorizontal, Field(default="center")]
    preserve_from_source_canvas: Annotated[PreserveFromSource, Field(default="none")]
    maximum_dimensions: Annotated[Dimensions[int], Field(default=None, exclude_if=lambda v: not v)]
    pad_to_maximum: Annotated[bool, Field(default=False, exclude_if=lambda v: v is None)]
    round: Annotated[RoundStrategy, Field(default=RoundStrategy())]

    def get_desqueezed_width(self, source_width: float, squeeze_factor: float) -> float:
        """
        Get the de-squeezed width also considering the `target_anamorphic_squeeze`.
        Used to calculate scaling of canvases and framing decisions.
        If `target_anamorphic_squeeze` is 0, it's considered "same as source" and no de-squeeze
        is applied.

        Args:
            source_width: from source `Canvas` or `FramingDecision`
            squeeze_factor: source `Canvas.anamorphic_squeeze`

        Returns:
            width: scaled to size
        """

        width = source_width

        # target_anamorphic_squeeze of 0 is considered "same as source"
        if self.target_anamorphic_squeeze > 0:
            width = width * squeeze_factor / self.target_anamorphic_squeeze

        return width

    def get_scale_factor(self, source_dimensions: Dimensions, source_anamorphic_squeeze: float) -> float:
        """
        Calculate the scale factor used when creating a new `Canvas` and `FramingDecision`

        Args:
            source_dimensions:
            source_anamorphic_squeeze:

        Returns:
            scale_factor:
        """

        # We default to fit_method "width"
        source_width = self.get_desqueezed_width(source_dimensions.width, source_anamorphic_squeeze)
        scale_factor = self.target_dimensions.width / source_width

        target_aspect = self.target_dimensions.width / self.target_dimensions.height
        source_aspect = source_width / source_dimensions.height

        if self.fit_method == "height":
            scale_factor = self.target_dimensions.height / source_dimensions.height

        elif self.fit_method == "fit_all":
            if target_aspect > source_aspect:
                # Target wider than source
                scale_factor = self.target_dimensions.height / source_dimensions.height

        elif self.fit_method == "fill" and target_aspect < source_aspect:
            # What's left outside the target dimensions due to fill?
            # Source wider than target
            scale_factor = self.target_dimensions.height / source_dimensions.height

        return scale_factor

    def fit_source_to_target(self, source_dimensions: Dimensions, source_anamorphic_squeeze: float) -> Dimensions:
        """
        Calculate the dimensions of `fit_source` inside `target_dimensions` based on `fit_mode`

        Args:
            source_dimensions:
            source_anamorphic_squeeze:

        Returns:
            size:
        """

        scale_factor = self.get_scale_factor(source_dimensions, source_anamorphic_squeeze)
        source_width = self.get_desqueezed_width(source_dimensions.width, source_anamorphic_squeeze)

        # In case of fit_mode == fill
        width = self.target_dimensions.width
        height = self.target_dimensions.height

        if self.fit_method == "width":
            width = self.target_dimensions.width
            # If scaled height exceeds target height, we crop the excess
            height = min(
                # round_to_even(source_dimensions.height * scale_factor),
                source_dimensions.height * scale_factor,
                self.target_dimensions.height,
            )

        elif self.fit_method == "height":
            height = self.target_dimensions.height
            scale_factor = height / source_dimensions.height
            # If scaled width exceeds target width, we crop the excess
            width = min(
                # round_to_even(source_width * scale_factor),
                source_width * scale_factor,
                self.target_dimensions.width,
            )

        elif self.fit_method == "fit_all":
            width = source_width * scale_factor
            height = source_dimensions.height * scale_factor
            if source_dimensions > self.target_dimensions:
                if width > self.target_dimensions.width:
                    adjustment_scale = self.target_dimensions.width / width

                else:
                    adjustment_scale = self.target_dimensions.height / height

                width *= adjustment_scale
                height *= adjustment_scale

        size = Dimensions(width=width, height=height)
        # TODO: consider returning crop True/False
        #  or at least coordinates outside of frame like data window vs display window in EXR

        return size

    def get_transfer_keys(self) -> list[str]:
        """
        Get a list of attributes to transfer from source to destination in the order that
        preserves all attributes between `fit_source` and `preserve_from_canvas`

        Returns:
            keys:
        """

        dimension_routing_map = {
            "framing_decision.dimensions": [
                "framing_decision.dimensions",
                "framing_decision.protection_dimensions",
                "canvas.effective_dimensions",
                "canvas.dimensions",
            ],
            "framing_decision.protection_dimensions": [
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.effective_dimensions",
                "canvas.dimensions",
            ],
            "canvas.effective_dimensions": [
                "canvas.effective_dimensions",
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.dimensions",
            ],
            "canvas.dimensions": [
                "canvas.dimensions",
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.effective_dimensions",
            ],
        }
        keys = dimension_routing_map[self.fit_source]
        preserve = self.preserve_from_source_canvas

        if preserve in [None, "none"]:
            preserve = self.fit_source

        first = keys.index(self.fit_source)
        last = keys.index(preserve) + 1
        if first == last:
            return [keys[first]]

        return keys[first:last]

    def __eq__(self, other) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __hash__(self):
        return hash((self.id,))

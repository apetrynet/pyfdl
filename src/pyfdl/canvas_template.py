from typing import Optional, Union

from .common import Base, Dimensions, RoundStrategy
from .errors import FDLError


class CanvasTemplate(Base):
    def __init__(
        self,
        label: Optional[str] = None,
        id_: Optional[str] = None,
        target_dimensions: Optional[Dimensions] = None,
        target_anamorphic_squeeze: Optional[float] = None,
        fit_source: Optional[str] = None,
        fit_method: Optional[str] = None,
        alignment_method_vertical: Optional[str] = None,
        alignment_method_horizontal: Optional[str] = None,
        preserve_from_source_canvas: Optional[str] = None,
        maximum_dimensions: Optional[Dimensions] = None,
        pad_to_maximum: Optional[bool] = None,
        round_: Optional[RoundStrategy] = None,
    ):
        super().__init__()
        self.attributes = [
            "label",
            "id",
            "target_dimensions",
            "target_anamorphic_squeeze",
            "fit_source",
            "fit_method",
            "alignment_method_vertical",
            "alignment_method_horizontal",
            "preserve_from_source_canvas",
            "maximum_dimensions",
            "pad_to_maximum",
            "round",
        ]

        self.kwarg_map = {"id": "id_", "round": "round_"}
        self.object_map = {"target_dimensions": Dimensions, "maximum_dimensions": Dimensions, "round": RoundStrategy}
        self.required = [
            "id",
            "target_dimensions",
            "target_anamorphic_squeeze",
            "fit_source",
            "fit_method",
            "pad_to_maximum.maximum_dimensions",
        ]
        self.defaults = {
            "target_anamorphic_squeeze": 1,
            "fit_source": "framing_decision.dimensions",
            "alignment_method_vertical": "center",
            "alignment_method_horizontal": "center",
            "preserve_from_source_canvas": "none",
            "pad_to_maximum": False,
        }

        self.label = label
        self.id = id_
        self.target_dimensions = target_dimensions
        self.target_anamorphic_squeeze = target_anamorphic_squeeze
        self.fit_source = fit_source
        self.fit_method = fit_method
        self.alignment_method_vertical = alignment_method_vertical
        self.alignment_method_horizontal = alignment_method_horizontal
        self.preserve_from_source_canvas = preserve_from_source_canvas
        self.maximum_dimensions = maximum_dimensions
        self.pad_to_maximum = pad_to_maximum
        self.round = round_

    @property
    def target_dimensions(self) -> Union[Dimensions, None]:
        return self._target_dimensions

    @target_dimensions.setter
    def target_dimensions(self, dim: Union[Dimensions, None]):
        self._target_dimensions = dim
        if dim is not None:
            self._target_dimensions.dtype = int

    @property
    def maximum_dimensions(self) -> Union[Dimensions, None]:
        return self._maximum_dimensions

    @maximum_dimensions.setter
    def maximum_dimensions(self, dim: Union[Dimensions, None]):
        self._maximum_dimensions = dim
        if dim is not None:
            self._maximum_dimensions.dtype = int

    @property
    def fit_source(self) -> str:
        return self._fit_source

    @fit_source.setter
    def fit_source(self, value: str):
        valid_options = (
            "framing_decision.dimensions",
            "framing_decision.protection_dimensions",
            "canvas.dimensions",
            "canvas.effective_dimensions",
        )
        if value is not None and value not in valid_options:
            msg = (
                f'"{value}" is not a valid option for "fit_source".\n'
                f"Please use one of the following: {valid_options}"
            )
            raise FDLError(msg)

        self._fit_source = value

    @property
    def fit_method(self) -> str:
        return self._fit_method

    @fit_method.setter
    def fit_method(self, value: str):
        valid_options = ("width", "height", "fit_all", "fill")
        if value is not None and value not in valid_options:
            msg = (
                f'"{value}" is not a valid option for "fit_method".\n'
                f"Please use one of the following: {valid_options}"
            )
            raise FDLError(msg)

        self._fit_method = value

    @property
    def alignment_method_vertical(self) -> str:
        return self._alignment_method_vertical

    @alignment_method_vertical.setter
    def alignment_method_vertical(self, value):
        valid_options = ("center", "top", "bottom")
        if value is not None and value not in valid_options:
            msg = (
                f'"{value}" is not a valid option for "alignment_method_vertical".\n'
                f"Please use one of the following: {valid_options}"
            )
            raise FDLError(msg)

        self._alignment_method_vertical = value

    @property
    def alignment_method_horizontal(self) -> str:
        return self._alignment_method_horizontal

    @alignment_method_horizontal.setter
    def alignment_method_horizontal(self, value):
        valid_options = ("center", "left", "right")
        if value is not None and value not in valid_options:
            msg = (
                f'"{value}" is not a valid option for "alignment_method_horizontal".\n'
                f"Please use one of the following: {valid_options}"
            )
            raise FDLError(msg)

        self._alignment_method_horizontal = value

    @property
    def preserve_from_source_canvas(self) -> str:
        return self._preserve_from_source_canvas

    @preserve_from_source_canvas.setter
    def preserve_from_source_canvas(self, value):
        valid_options = (
            "none",
            "framing_decision.dimensions",
            "framing_decision.protection_dimensions",
            "canvas.dimensions",
            "canvas.effective_dimensions",
        )
        if value is not None and value not in valid_options:
            msg = (
                f'"{value}" is not a valid option for "preserve_from_source_canvas".\n'
                f"Please use one of the following: {valid_options}"
            )
            raise FDLError(msg)

        self._preserve_from_source_canvas = value

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

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id})"'

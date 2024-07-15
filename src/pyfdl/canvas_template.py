from typing import Union, List

from pyfdl import Base, Dimensions, RoundStrategy
from pyfdl.errors import FDLError


class CanvasTemplate(Base):
    attributes = [
        'label',
        'id',
        'target_dimensions',
        'target_anamorphic_squeeze',
        'fit_source',
        'fit_method',
        'alignment_method_vertical',
        'alignment_method_horizontal',
        'preserve_from_source_canvas',
        'maximum_dimensions',
        'pad_to_maximum',
        'round'
    ]

    kwarg_map = {'id': 'id_', 'round': 'round_'}
    object_map = {
        'target_dimensions': Dimensions,
        'maximum_dimensions': Dimensions,
        'round': RoundStrategy
    }
    required = [
        'id',
        'target_dimensions',
        'target_anamorphic_squeeze',
        'fit_source',
        'fit_method',
        'pad_to_maximum.maximum_dimensions'
    ]
    defaults = {
        'target_anamorphic_squeeze': 1,
        'fit_source': 'framing_decision.dimensions',
        'alignment_method_vertical': 'center',
        'alignment_method_horizontal': 'center',
        'preserve_from_source_canvas': 'none',
        'pad_to_maximum': False
    }

    def __init__(
            self,
            label: str = None,
            id_: str = None,
            target_dimensions: Dimensions = None,
            target_anamorphic_squeeze: float = None,
            fit_source: str = None,
            fit_method: str = None,
            alignment_method_vertical: str = None,
            alignment_method_horizontal: str = None,
            preserve_from_source_canvas: str = None,
            maximum_dimensions: Dimensions = None,
            pad_to_maximum: bool = None,
            round_: RoundStrategy = None
    ):
        super().__init__()
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
    def dimensions(self) -> Union[Dimensions, None]:
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dim: Union[Dimensions, dict, None]):
        if isinstance(dim, dict):
            dim = Dimensions.from_dict(dim)

        self._dimensions = dim
        if dim is not None:
            self._dimensions.dtype = int

    @property
    def maximum_dimensions(self) -> Union[Dimensions, None]:
        return self._maximum_dimensions

    @maximum_dimensions.setter
    def maximum_dimensions(self, dim: Union[Dimensions, None]):
        if isinstance(dim, dict):
            dim = Dimensions.from_dict(dim)

        self._maximum_dimensions = dim
        if dim is not None:
            self._maximum_dimensions.dtype = int

    @property
    def fit_source(self) -> str:
        return self._fit_source

    @fit_source.setter
    def fit_source(self, value: str):
        valid_options = (
            'framing_decision.dimensions',
            'framing_decision.protection_dimensions',
            'canvas.dimensions',
            'canvas.effective_dimensions'
        )
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "fit_source".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._fit_source = value

    @property
    def fit_method(self) -> str:
        return self._fit_method

    @fit_method.setter
    def fit_method(self, value: str):
        valid_options = ('width', 'height', 'fit_all', 'fill')
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "fit_method".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._fit_method = value

    @property
    def alignment_method_vertical(self) -> str:
        return self._alignment_method_vertical

    @alignment_method_vertical.setter
    def alignment_method_vertical(self, value):
        valid_options = ('center', 'top', 'bottom')
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "alignment_method_vertical".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._alignment_method_vertical = value

    @property
    def alignment_method_horizontal(self) -> str:
        return self._alignment_method_horizontal

    @alignment_method_horizontal.setter
    def alignment_method_horizontal(self, value):
        valid_options = ('center', 'left', 'right')
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "alignment_method_horizontal".\n'
                f'Please use one of the following: {valid_options}'
            )

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
            "canvas.effective_dimensions"
        )
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "preserve_from_source_canvas".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._preserve_from_source_canvas = value

    def get_desqueezed_width(
            self,
            source_width: Union[float, int],
            squeeze_factor: float
    ) -> Union[float, int]:
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

    def get_scale_factor(
            self,
            source_dimensions: Dimensions,
            source_anamorphic_squeeze: float
    ) -> float:
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

        if self.fit_method == 'height':
            scale_factor = self.target_dimensions.height / source_dimensions.height

        elif self.fit_method == 'fit_all':
            if target_aspect > source_aspect:
                # Target wider than source
                scale_factor = self.target_dimensions.height / source_dimensions.height

        elif self.fit_method == 'fill':
            # What's left outside the target dimensions due to fill?
            if target_aspect < source_aspect:
                # Source wider than target
                scale_factor = self.target_dimensions.height / source_dimensions.height

        return scale_factor

    def fit_source_to_target(
            self,
            source_dimensions: Dimensions,
            source_anamorphic_squeeze: float
    ) -> Dimensions:
        """
        Calculate the dimensions of `fit_source` inside `target_dimensions` based on `fit_mode`

        Args:
            source_dimensions:
            source_anamorphic_squeeze:

        Returns:
            size:
        """
        # TODO: Add tests to see if this method actually does the right thing

        scale_factor = self.get_scale_factor(source_dimensions, source_anamorphic_squeeze)
        source_width = self.get_desqueezed_width(source_dimensions.width, source_anamorphic_squeeze)

        # In case of fit_mode == fill
        width = self.target_dimensions.width
        height = self.target_dimensions.height

        if self.fit_method == 'width':
            width = self.target_dimensions.width
            # If scaled height exceeds target height, we crop the excess
            height = min(
                # round_to_even(source_dimensions.height * scale_factor),
                source_dimensions.height * scale_factor,
                self.target_dimensions.height
            )

        elif self.fit_method == 'height':
            height = self.target_dimensions.height
            scale_factor = height / source_dimensions.height
            # If scaled width exceeds target width, we crop the excess
            width = min(
                # round_to_even(source_width * scale_factor),
                source_width * scale_factor,
                self.target_dimensions.width
            )

        elif self.fit_method == 'fit_all':
            height = self.target_dimensions.height
            width = source_width * scale_factor
            if width > self.target_dimensions.width:
                adjustment_scale = self.target_dimensions.width / width
                height *= adjustment_scale
                width *= adjustment_scale

        size = type(self.target_dimensions)(width=width, height=height)
        # TODO consider returning crop True/False
        #  or at least coordinates outside of frame like data window vs display window

        return size

    def get_transfer_keys(self) -> List[str]:
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
                "canvas.dimensions"
            ],
            "framing_decision.protection_dimensions": [
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.effective_dimensions",
                "canvas.dimensions"
            ],
            "canvas.effective_dimensions": [
                "canvas.effective_dimensions",
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.dimensions"
            ],
            "canvas.dimensions": [
                "canvas.dimensions",
                "framing_decision.protection_dimensions",
                "framing_decision.dimensions",
                "canvas.effective_dimensions"
            ]
        }
        keys = dimension_routing_map[self.fit_source]
        preserve = self.preserve_from_source_canvas

        if preserve in [None, 'none']:
            preserve = self.fit_source

        first = keys.index(self.fit_source)
        last = keys.index(preserve) + 1
        if first == last:
            return [keys[first]]

        return keys[first:last]

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id})"'

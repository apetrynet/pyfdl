import math
from collections import namedtuple
from typing import Union, NamedTuple, Tuple

from pyfdl import Base, DimensionsInt, RoundStrategy, TypedCollection
from pyfdl.base import round_to_even, DimensionsFloat
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

    kwarg_map = {'id': '_id', 'round': '_round'}
    object_map = {
        'target_dimensions': DimensionsInt,
        'maximum_dimensions': DimensionsInt,
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
            _id: str = None,
            target_dimensions: DimensionsInt = None,
            target_anamorphic_squeeze: float = None,
            fit_source: str = None,
            fit_method: str = None,
            alignment_method_vertical: str = None,
            alignment_method_horizontal: str = None,
            preserve_from_source_canvas: str = None,
            maximum_dimensions: DimensionsInt = None,
            pad_to_maximum: bool = None,
            _round: RoundStrategy = None
    ):
        self.label = label
        self.id = _id
        self.target_dimensions = target_dimensions
        self.target_anamorphic_squeeze = target_anamorphic_squeeze
        self.fit_source = fit_source
        self.fit_method = fit_method
        self.alignment_method_vertical = alignment_method_vertical
        self.alignment_method_horizontal = alignment_method_horizontal
        self.preserve_from_source_canvas = preserve_from_source_canvas
        self.maximum_dimensions = maximum_dimensions
        self.pad_to_maximum = pad_to_maximum
        self.round = _round

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

    def get_desqueezed_width(self, source_width: Union[float, int], squeeze_factor: float) -> Union[float, int]:
        width = source_width

        # target_anamorphic_squeeze of 0 is considered "same as source"
        if self.target_anamorphic_squeeze > 0:
            width = width * squeeze_factor / self.target_anamorphic_squeeze

        return width

    def fit_source_to_target(
            self,
            source_dimensions: Union[DimensionsInt, DimensionsFloat],
            source_anamorphic_squeeze: float
    ) -> Tuple[Union[DimensionsInt, DimensionsFloat], float]:

        source_width = self.get_desqueezed_width(source_dimensions.width, source_anamorphic_squeeze)
        scale_factor = self.target_dimensions.width / source_width

        # In case of fit_mode == fill
        width = self.target_dimensions.width
        height = self.target_dimensions.height

        if self.fit_method == 'width':
            width = self.target_dimensions.width
            # If scaled height exceeds target height, we crop the excess
            height = min(
                source_dimensions.height * scale_factor,
                # round_to_even(source_dimensions.height * scale_factor),
                self.target_dimensions.height
            )
            height = source_dimensions.height * scale_factor
            if height > self.target_dimensions.height:
                print("CROPPING HEIGHT", height)

        elif self.fit_method == 'height':
            height = self.target_dimensions.height
            # If scaled width exceeds target width, we crop the excess
            width = min(
                # round_to_even(source_width * scale_factor),
                source_width * scale_factor,
                self.target_dimensions.width
            )
            width = source_width * scale_factor
            if width > self.target_dimensions.width:
                print("CROPPING WIDTH", width)

        elif self.fit_method == 'fit_all':
            height = self.target_dimensions.height
            width = source_width * scale_factor
            if width > self.target_dimensions.width:
                adjustment_scale = self.target_dimensions.width / width
                height *= adjustment_scale
                width *= adjustment_scale

        size = type(self.target_dimensions)(width=width, height=height)
        # TODO consider returning crop True/False
        return size, scale_factor

    def round_canvas_dimensions(self, dimensions: DimensionsInt) -> DimensionsInt:
        print(type(self.round))
        even = self.round.even
        mode = self.round.mode

        mode_map = {
            'up': math.ceil,
            'down': math.floor,
            'round': round
        }

        width = mode_map[mode](dimensions.width)
        height = mode_map[mode](dimensions.height)

        if even == 'even':
            width = round_to_even(width)
            height = round_to_even(height)

        return DimensionsInt(width=width, height=height)

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id})"'

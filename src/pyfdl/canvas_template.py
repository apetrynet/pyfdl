from pyfdl import Base, DimensionsInt, RoundStrategy
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
        'rounding': RoundStrategy
    }
    required = ['id', 'target_dimensions', 'target_anamorphic_squeeze', 'fit_source', 'fit_method']
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
            pad_to_maximum: bool = False,
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

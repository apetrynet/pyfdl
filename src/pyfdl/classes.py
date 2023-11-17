import uuid
from abc import ABC, abstractmethod

from pyfdl.errors import FDLError

FDL_SCHEMA_MAJOR = 1
FDL_SCHEMA_MINOR = 0
FDL_SCHEMA_VERSION = {'major': FDL_SCHEMA_MAJOR, 'minor': FDL_SCHEMA_MINOR}


class Base(ABC):
    attributes = []
    kwarg_map = {}
    object_map = {}
    required = []
    defaults = {}

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def apply_defaults(self):
        """Applies default values, if any, to attributes that are `None`"""
        for key, value in self.defaults.items():
            if getattr(self, key) is None:
                if callable(value):
                    setattr(self, key, value())

                elif isinstance(value, Base):
                    setattr(self, key, value.apply_defaults())

                else:
                    setattr(self, key, value)

    def check_required(self) -> list:
        missing = []
        for required_key in self.required:
            # Check for dependant attributes.
            # Like "effective_anchor_point" required if "effective_dimensions" is provided
            if '.' in required_key:
                attr1, attr2 = required_key.split('.')
                if getattr(self, attr1) is not None and getattr(self, attr2) is None:
                    missing.append(attr2)

            elif getattr(self, required_key) is None:
                missing.append(required_key)

        return missing

    def to_dict(self) -> dict:
        data = {}
        for key in self.attributes:
            value = getattr(self, key)

            # check if empty value should be omitted
            if key not in self.required and not value:
                continue

            # Arrays (aka lists) contain other objects
            if isinstance(value, list):
                value = [item.to_dict() for item in value]

            # This should cover all known objects
            elif isinstance(value, Base):
                value = value.to_dict()

            data[key] = value

        missing = self.check_required()
        if missing:
            raise FDLError(f'{repr(self)} is missing some required attributes: {missing}')

        return data

    @classmethod
    def from_dict(cls, raw: dict):
        kwargs = {}
        for key in cls.attributes:
            # We get the value before we convert the key to a valid name
            value = raw.get(key)
            if value is None:
                continue

            # Check for keyword override
            keyword = cls.kwarg_map.get(key, key)

            if key in cls.object_map:
                if isinstance(value, list):
                    value = [cls.object_map[key].from_dict(item) for item in value]

                else:
                    value = cls.object_map[key].from_dict(value)

            kwargs[keyword] = value

        return cls(**kwargs)

    def __repr__(self) -> str:
        return f'"{self.__class__.__name__}"'

    def __str__(self) -> str:
        return str(self.to_dict())


class DimensionsFloat(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


class DimensionsInt(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height


class PointFloat(Base):
    attributes = ['x', 'y']
    required = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class RoundStrategy(Base):
    attributes = ['even', 'mode']

    VALID_EVEN = ('even', 'whole')
    VALID_MODES = ('up', 'down', 'round')
    defaults = {'even': 'even', 'mode': 'up'}

    def __init__(self, even: str = None, mode: str = None):
        self.even = even
        self.mode = mode


class Header(Base):
    attributes = ['uuid', 'version', 'fdl_creator', 'default_framing_intent']
    kwarg_map = {'uuid': '_uuid'}
    required = ['uuid', 'version']
    defaults = {'uuid': uuid.uuid4, 'fdl_creator': 'PyFDL', 'version': FDL_SCHEMA_VERSION}

    def __init__(
            self,
            _uuid: str = None,
            version: dict = None,
            fdl_creator: str = None,
            default_framing_intent: str = None
    ):
        self.uuid = _uuid
        self.version = version
        self.fdl_creator = fdl_creator
        self.default_framing_intent = default_framing_intent


class FramingIntent(Base):

    attributes = ['id', 'label', 'aspect_ratio', 'protection']
    kwarg_map = {'id': '_id'}
    object_map = {'aspect_ratio': DimensionsFloat}
    required = ['id', 'aspect_ratio']
    defaults = {'protection': 0}

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            aspect_ratio: DimensionsFloat = None,
            protection: float = None
    ):
        self.id = _id
        self.label = label
        self.aspect_ratio = aspect_ratio
        self.protection = protection


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
    kwarg_map = {'id': '_id'}
    object_map = {
        'dimensions': DimensionsFloat,
        'anchor_point': PointFloat,
        'protection_dimensions': DimensionsFloat,
        'protection_anchor_point': PointFloat
    }
    required = ['id', 'framing_intent_id', 'dimensions', 'anchor_point']

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            framing_intent_id: str = None,
            dimensions: DimensionsFloat = None,
            anchor_point: PointFloat = None,
            protection_dimensions: DimensionsFloat = None,
            protection_anchor_point: PointFloat = None
    ):
        self.label = label or ''
        self.id = _id
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point


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
        'effective_anchor_point': PointFloat,
        'photosite_dimensions': DimensionsInt,
        'physical_dimensions': DimensionsFloat,
        'framing_decisions': FramingDecision
    }
    required = ['id', 'source_canvas_id', 'dimensions', 'effective_dimensions.effective_anchor_point']
    defaults = {'anamorphic_squeeze': 1}

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            source_canvas_id: str = None,
            dimensions: DimensionsInt = None,
            effective_dimensions: DimensionsInt = None,
            effective_anchor_point: PointFloat = None,
            photosite_dimensions: DimensionsInt = None,
            physical_dimensions: DimensionsFloat = None,
            anamorphic_squeeze: float = None,
            framing_decisions: list = None
    ):
        self.label = label
        self.id = _id
        self.source_canvas_id = source_canvas_id or self.id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze
        self.framing_decisions = framing_decisions or []


class Context(Base):
    attributes = ['label', 'context_creator', 'canvases']
    object_map = {'canvases': Canvas}

    def __init__(self, label: str = None, context_creator: str = None, canvases: list = None):
        self.label = label or ''
        self.context_creator = context_creator or ''
        self.canvases = canvases or []


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


class FDL:
    def __init__(self, header: Header = None):
        if not header:
            header = Header()

        self.header = header
        self.framing_intents = []
        self.contexts = []
        self.canvas_templates = []

    def to_dict(self) -> dict:
        data = self.header.to_dict()
        data['framing_intents'] = [fi.to_dict() for fi in self.framing_intents]
        data['contexts'] = [ctx.to_dict() for ctx in self.contexts]
        data['canvas_templates'] = [template.to_dict() for template in self.canvas_templates]

        return data

    def __str__(self) -> str:
        return str(self.to_dict())

    @staticmethod
    def from_object(raw: dict):
        fdl = FDL()
        fdl.header = Header.from_dict(raw)
        fdl.framing_intents = [FramingIntent.from_dict(item) for item in raw.get('framing_intents', [])]
        fdl.contexts = [Context.from_dict(item) for item in raw.get('contexts', [])]
        fdl.canvas_templates = [CanvasTemplate.from_dict(item) for item in raw.get('canvas_templates', [])]

        return fdl

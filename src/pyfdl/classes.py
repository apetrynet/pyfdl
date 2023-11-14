import uuid
from abc import ABC, abstractmethod

from pyfdl.errors import FDLError

FDL_VERSION = {'major': 1, 'minor': 0}


class Base(ABC):
    __slots__ = []
    kwarg_map = {}
    object_map = {}
    required = []

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    def to_json(self) -> dict:
        data = {}
        for key in self.__slots__:
            value = getattr(self, key)
            if isinstance(value, list):
                value = [item.to_json() for item in value]

            elif isinstance(value, Base):
                value = value.to_json()

            data[key] = value

        return data

    @classmethod
    def from_object(cls, raw: dict):
        kwargs = {}
        for key in cls.__slots__:
            # We get the value before we convert the key to a valid name
            value = raw.get(key)
            if value is None:
                continue

            # Check for keyword override
            keyword = cls.kwarg_map.get(key, key)

            if key in cls.object_map:
                if isinstance(value, list):
                    value = [cls.object_map[key].from_object(item) for item in value]

                else:
                    value = cls.object_map[key].from_object(value)

            kwargs[keyword] = value

        return cls(**kwargs)

    def __str__(self) -> str:
        return str(self.to_json())


class Dimensions(Base):
    __slots__ = ['width', 'height']

    def __init__(self, width: [int, float], height: [int, float]):
        self.width = width
        self.height = height


class Point(Base):
    __slots__ = ['x', 'y']

    def __init__(self, x: [int, float], y: [int, float]):
        self.x = x
        self.y = y


class Header(Base):
    __slots__ = ['uuid', 'version', 'fdl_creator', 'default_framing_intent']
    kwarg_map = {'uuid': '_uuid'}
    required = ['uuid', 'version']

    def __init__(
            self,
            _uuid: str = str(uuid.uuid4()),
            version: dict = None,
            fdl_creator: str = 'pyfdl',
            default_framing_intent: str = ''
    ):
        self.uuid = _uuid
        self.version = version or FDL_VERSION
        self.fdl_creator = fdl_creator
        self.default_framing_intent = default_framing_intent


class FramingIntent(Base):

    __slots__ = ['id', 'label', 'aspect_ratio', 'protection']
    kwarg_map = {'id': '_id'}
    object_map = {'aspect_ratio': Dimensions}

    def __init__(self, label: str = None, _id: str = None, aspect_ratio: Dimensions = None,
                 protection: float = None):

        if not _id:
            raise FDLError('Please provide a required "_id"')

        self.id = _id
        self.label = label or ''
        self.aspect_ratio = aspect_ratio or Dimensions(1, 1)
        self.protection = protection or 0.0


class FramingDecision(Base):
    __slots__ = [
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
        'dimensions': Dimensions,
        'anchor_point': Point,
        'protection_dimensions': Dimensions,
        'protection_anchor_point': Point
    }

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            framing_intent_id: str = None,
            dimensions: Dimensions = None,
            anchor_point: Point = None,
            protection_dimensions: Dimensions = None,
            protection_anchor_point: Point = None
    ):
        if not _id:
            raise FDLError('Please provide a required "_id"')

        if not dimensions:
            raise FDLError('Please provide a required "dimensions"')

        if not anchor_point:
            raise FDLError('Please provide a required "anchor_point"')

        self.label = label or ''
        self.id = _id
        self.framing_intent_id = framing_intent_id
        self.dimensions = dimensions
        self.anchor_point = anchor_point
        self.protection_dimensions = protection_dimensions
        self.protection_anchor_point = protection_anchor_point


class Canvas(Base):
    __slots__ = [
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
        'dimensions': Dimensions,
        'effective_dimensions': Dimensions,
        'effective_anchor_point': Point,
        'photosite_dimensions': Dimensions,
        'physical_dimensions': Dimensions,
        'framing_decisions': FramingDecision
    }

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            source_canvas_id: str = None,
            dimensions: Dimensions = None,
            effective_dimensions: Dimensions = None,
            effective_anchor_point: Point = None,
            photosite_dimensions: Dimensions = None,
            physical_dimensions: Dimensions = None,
            anamorphic_squeeze: float = None,
            framing_decisions: list = None
    ):
        if not _id:
            raise FDLError('Please provide a required "_id"')

        if not dimensions:
            raise FDLError('Please provide a required "dimensions"')

        if effective_dimensions and not effective_anchor_point:
            raise FDLError('Please provide a required "effective_anchor_point"')

        self.label = label or ''
        self.id = _id
        self.source_canvas_id = source_canvas_id or self.id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze or 1.0
        self.framing_decisions = framing_decisions or []


class Context(Base):
    __slots__ = ['label', 'context_creator', 'canvases']
    object_map = {'canvases': Canvas}

    def __init__(self, label: str = None, context_creator: str = None, canvases: list = None):
        self.label = label or ''
        self.context_creator = context_creator or ''
        self.canvases = canvases or []


class Rounding(Base):
    __slots__ = ['even', 'mode']

    VALID_EVEN = ('even', 'whole')
    VALID_MODES = ('up', 'down', 'round')

    def __init__(self, even: str = 'even', mode: str = 'up'):
        if even not in self.VALID_EVEN:
            raise FDLError(f'"even" must be one of the following: {self.VALID_EVEN}')

        if mode not in self.VALID_MODES:
            raise FDLError(f'"mode" must be one of the following: {self.VALID_MODES}')

        self.even = even
        self.mode = mode


class CanvasTemplate(Base):
    FIT_SOURCE = (
        'framing_decision.dimensions',
        'framing_decision.protection_dimensions',
        'canvas.dimensions',
        'canvas.effective_dimensions'
    )
    FIT_METHOD = ('width', 'height', 'fit_all', 'fill')
    ALIGNMENT_VERTICAL = ('center', 'top', 'bottom')
    ALIGNMENT_HORIZONTAL = ('center', 'left', 'right')
    PRESERVE_FROM_SOURCE_CANVAS = (
        'none',
        'framing_decision.dimensions',
        'framing_decision.protection_dimensions',
        'canvas.dimensions',
        'canvas.effective_dimensions'
    )
    __slots__ = [
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
        'target_dimensions': Dimensions,
        'maximum_dimensions': Dimensions,
        'rounding': Rounding
    }

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            target_dimensions: Dimensions = None,
            target_anamorphic_squeeze: float = None,
            fit_source: str = None,
            fit_method: str = None,
            alignment_method_vertical: str = None,
            alignment_method_horizontal: str = None,
            preserve_from_source_canvas: str = None,
            maximum_dimensions: Dimensions = None,
            pad_to_maximum: bool = False,
            _round: Rounding = None
    ):
        if not _id:
            raise FDLError('Please provide a required "_id"')

        if not target_dimensions:
            raise FDLError('Please provide a required "target_dimensions"')

        if fit_source and fit_source not in self.FIT_SOURCE:
            raise FDLError(f'"fit_source" must be one of the following: {self.FIT_SOURCE}')

        if fit_method and fit_method not in self.FIT_METHOD:
            raise FDLError(f'"fit_method" must be one of the following: {self.FIT_METHOD}')

        if alignment_method_vertical and alignment_method_vertical not in self.ALIGNMENT_VERTICAL:
            raise FDLError(f'"alignment_method_vertical" must be one of the following: {self.ALIGNMENT_VERTICAL}')

        if alignment_method_horizontal and alignment_method_horizontal not in self.ALIGNMENT_HORIZONTAL:
            raise FDLError(f'"alignment_method_horizontal" must be one of the following: {self.ALIGNMENT_HORIZONTAL}')

        if preserve_from_source_canvas and preserve_from_source_canvas not in self.PRESERVE_FROM_SOURCE_CANVAS:
            raise FDLError(
                f'"preserve_from_source_canvas" must be one of the following: {self.PRESERVE_FROM_SOURCE_CANVAS}'
            )

        self.label = label or ''
        self.id = _id
        self.target_dimensions = target_dimensions
        self.target_anamorphic_squeeze = target_anamorphic_squeeze or 1.0
        self.fit_source = fit_source or self.FIT_SOURCE[0]
        self.fit_method = fit_method or self.FIT_METHOD[0]
        self.alignment_method_vertical = alignment_method_vertical or self.ALIGNMENT_VERTICAL[0]
        self.alignment_method_horizontal = alignment_method_horizontal or self.ALIGNMENT_HORIZONTAL[0]
        self.preserve_from_source_canvas = preserve_from_source_canvas or self.PRESERVE_FROM_SOURCE_CANVAS[0]
        self.maximum_dimensions = maximum_dimensions
        self.pad_to_maximum = pad_to_maximum or False
        self.round = _round


class FDL:
    def __init__(self, header: Header = None):
        if not header:
            header = Header()

        self.header = header
        self.framing_intents = []
        self.contexts = []
        self.canvas_templates = []

    def to_json(self) -> dict:
        data = self.header.to_json()
        data['framing_intents'] = [fi.to_json() for fi in self.framing_intents]
        data['contexts'] = [ctx.to_json() for ctx in self.contexts]
        data['canvas_templates'] = [template.to_json() for template in self.canvas_templates]

        return data

    def __str__(self) -> str:
        return str(self.to_json())

    @staticmethod
    def from_object(raw: dict):
        header = Header.from_object(raw)
        fdl = FDL(header=header)

        fdl.framing_intents = [FramingIntent.from_object(item) for item in raw.get('framing_intents', [])]
        fdl.contexts = [Context.from_object(item) for item in raw.get('contexts', [])]
        fdl.canvas_templates = [CanvasTemplate.from_object(item) for item in raw.get('canvas_templates', [])]

        return fdl

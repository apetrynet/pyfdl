import uuid
import json

from pyfdl.errors import FDLError

FDL_VERSION = {'major': 1, 'minor': 0}


class Dimensions:
    def __init__(self, width: [int, float], height: [int, float]):
        self.width = width
        self.height = height

    def to_json(self) -> str:
        return json.dumps({'width': self.width, 'height': self.height})

    @staticmethod
    def from_object(raw: dict):
        return Dimensions(raw.get('width'), raw.get('height'))

    def __str__(self) -> str:
        return str(self.to_json())


class Point:
    def __init__(self, x: [int, float], y: [int, float]):
        self.x = x
        self.y = y

    def to_json(self) -> str:
        return json.dumps({'x': self.x, 'y': self.y})

    @staticmethod
    def from_object(raw: dict):
        return Point(raw.get('x'), raw.get('y'))

    def __str__(self) -> str:
        return str(self.to_json())


class Header:
    def __init__(
            self,
            header_uuid: str = str(uuid.uuid4()),
            version: dict = FDL_VERSION,
            fdl_creator: str = 'pyfdl',
            default_framing_intent: str = ''
    ):
        self.uuid = header_uuid
        self.version = version
        self.fdl_creator = fdl_creator
        self.default_framing_intent = default_framing_intent

    def to_json(self) -> str:
        data = {
            'uuid': self.uuid,
            'version': self.version,
            'fdl_creator': self.fdl_creator,
            'default_framing_intent': self.default_framing_intent
        }

        return json.dumps(data)

    def __str__(self) -> str:
        return str(self.to_json())


class FramingIntent:
    def __init__(
            self,
            label: str = None,
            intent_id: str = None,
            aspect_ratio: Dimensions = None,
            protection: float = None
    ):
        if not intent_id:
            raise FDLError('Please provide a required "intent_id"')

        self.id = intent_id
        self.label = label or ''
        self.aspect_ratio = aspect_ratio or Dimensions(1, 1)
        self.protection = protection or 0.0

    def to_json(self) -> str:
        data = {
            'label': self.label,
            'id': self.id,
            'aspect_ratio': self.aspect_ratio.to_json(),
            'protection': self.protection
        }

        return json.dumps(data)

    @staticmethod
    def from_object(raw: dict):
        framing_intent = FramingIntent(
            label=raw.get('label'),
            intent_id=raw.get('id'),
            aspect_ratio=Dimensions.from_object(raw.get('aspect_ratio')),
            protection=raw.get('protection')
        )

        return framing_intent

    def __str__(self) -> str:
        return str(self.to_json())


class Context:
    def __init__(self, label: str = None, context_creator: str = None, canvases: list = None):
        self.label = label or ''
        self.context_creator = context_creator or ''
        self.canvases = canvases or []

    def to_json(self) -> str:
        data = {
            'label': self.label,
            'context_creator': self.context_creator,
            'canvases': [canvas.to_json() for canvas in self.canvases]
        }

        return json.dumps(data)

    @staticmethod
    def from_object(raw: dict):
        context = Context(
            label=raw.get('label'),
            context_creator=raw.get('context_creator'),
            canvases=[Canvas.from_object(canvas) for canvas in raw.get('canvases', [])]
        )

        return context

    def __str__(self) -> str:
        return str(self.to_json())


class Canvas:
    def __init__(
            self,
            label: str = None,
            canvas_id: str = None,
            source_canvas_id: str = None,
            dimensions: Dimensions = None,
            effective_dimensions: Dimensions = None,
            effective_anchor_point: Point = None,
            photosite_dimensions: Dimensions = None,
            physical_dimensions: Dimensions = None,
            anamorphic_squeeze: float = None
    ):
        if not canvas_id:
            raise FDLError('Please provide a required "canvas_id"')

        if not Dimensions:
            raise FDLError('Please provide a required "dimensions"')

        if not effective_anchor_point:
            raise FDLError('Please provide a required "effective_anchor_point"')

        self.label = label or ''
        self.id = canvas_id
        self.source_canvas_id = source_canvas_id or self.id
        self.dimensions = dimensions
        self.effective_dimensions = effective_dimensions
        self.effective_anchor_point = effective_anchor_point
        self.photosite_dimensions = photosite_dimensions
        self.physical_dimensions = physical_dimensions
        self.anamorphic_squeeze = anamorphic_squeeze or 1.0

    @staticmethod
    def from_object(raw: dict):
        canvas = Canvas(
            label=raw.get('label'),
            canvas_id=raw.get('id'),
            source_canvas_id=raw.get('source_canvas_id'),
            dimensions=Dimensions.from_object(raw.get('dimensions')),
            effective_dimensions=Dimensions.from_object(raw.get('effective_dimensions', {})),
            effective_anchor_point=Point.from_object(raw.get('effective_anchor_point', {})),
            photosite_dimensions=Dimensions.from_object(raw.get('photosite_dimensions', {})),
            physical_dimensions=Dimensions.from_object(raw.get('physical_dimensions', {})),
            anamorphic_squeeze=raw.get('anamorphic_squeeze')
        )

        return canvas

    def to_json(self) -> str:
        data = {
            'label': self.label,
            'id': self.id,
            'source_canvas_id': self.source_canvas_id,
            'dimensions': self.dimensions.to_json(),
            'effective_dimensions': self.effective_dimensions.to_json(),
            'effective_anchor_point': self.effective_anchor_point.to_json(),
            'photosite_dimensions': self.photosite_dimensions.to_json(),
            'physical_dimensions': self.physical_dimensions.to_json(),
            'anamorphic_squeeze': self.anamorphic_squeeze
        }

        return json.dumps(data)

    def __str__(self) -> str:
        return str(self.to_json())


class Rounding:
    VALID_EVEN = ('even', 'whole')
    VALID_MODES = ('up', 'down', 'round')

    def __init__(self, even: str = 'even', mode: str = 'up'):
        if even not in self.VALID_EVEN:
            raise FDLError(f'"even" must be one of the following: {self.VALID_EVEN}')

        if mode not in self.VALID_MODES:
            raise FDLError(f'"mode" must be one of the following: {self.VALID_MODES}')

        self.data = {'even': even, 'mode': mode}

    def to_json(self) -> str:
        return json.dumps(self.data)

    @staticmethod
    def from_object(raw: dict):
        return Rounding(even=raw.get('even'), mode=raw.get('mode'))


class CanvasTemplate:
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

    def __init__(
            self,
            label: str = None,
            template_id: str = None,
            target_dimensions: Dimensions = None,
            target_anamorphic_squeeze: float = None,
            fit_source: str = None,
            fit_method: str = None,
            alignment_method_vertical: str = None,
            alignment_method_horizontal: str = None,
            preserve_from_source_canvas: str = None,
            maximum_dimensions: Dimensions = None,
            pad_to_maximum: bool = False,
            rounding: Rounding = None
    ):
        if not template_id:
            raise FDLError('Please provide a required "template_id"')

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
        self.id = template_id
        self.target_dimensions = target_dimensions
        self.target_anamorphic_squeeze = target_anamorphic_squeeze or 1.0
        self.fit_source = fit_source or self.FIT_SOURCE[0]
        self.fit_method = fit_method or self.FIT_METHOD[0]
        self.alignment_method_vertical = alignment_method_vertical or self.ALIGNMENT_VERTICAL[0]
        self.alignment_method_horizontal = alignment_method_horizontal or self.ALIGNMENT_HORIZONTAL[0]
        self.preserve_from_source_canvas = preserve_from_source_canvas or self.PRESERVE_FROM_SOURCE_CANVAS[0]
        self.maximum_dimensions = maximum_dimensions
        self.pad_to_maximum = pad_to_maximum or False
        self.round = rounding.to_json()

    def to_json(self) -> str:
        data = {
            'label': self.label,
            'id': self.id,
            'target_dimensions': self.target_dimensions.to_json(),
            'target_anamorphic_squeeze': self.target_anamorphic_squeeze,
            'fit_source': self.fit_source,
            'fit_method': self.fit_method,
            'alignment_method_vertical': self.alignment_method_vertical,
            'alignment_method_horizontal': self.alignment_method_horizontal,
            'preserve_from_source_canvas': self.preserve_from_source_canvas,
            'maximum_dimensions': self.maximum_dimensions.to_json(),
            'pad_to_maximum': self.pad_to_maximum,
            'round': self.round
        }

        return json.dumps(data)

    @staticmethod
    def from_object(raw: dict):
        canvas_template = CanvasTemplate(
            label=raw.get('label'),
            template_id=raw.get('id'),
            target_dimensions=Dimensions.from_object(raw.get('target_dimensions')),
            target_anamorphic_squeeze=raw.get('target_anamorphic_squeeze'),
            fit_source=raw.get('fir_source'),
            fit_method=raw.get('fir_method'),
            alignment_method_vertical=raw.get('alignment_method_vertical'),
            alignment_method_horizontal=raw.get('alignment_method_horizontal'),
            preserve_from_source_canvas=raw.get('preserve_from_source_canvas'),
            maximum_dimensions=Dimensions.from_object(raw.get('maximum_dimensions', {})),
            pad_to_maximum=raw.get('pad_to_maximum'),
            rounding=Rounding.from_object(raw.get('round'))
        )

        return canvas_template

    def __str__(self) -> str:
        return str(self.to_json())


class FDL:
    def __init__(self, header: Header = None):
        if not header:
            header = Header()

        self.header = header
        self.framing_intents = []
        self.contexts = []
        self.canvas_templates = []

    def to_json(self) -> str:
        data = self.header.to_json()
        data['framing_intents'] = [fi.to_json() for fi in self.framing_intents]
        data['contexts'] = [ctx.to_json() for ctx in self.contexts]
        data['canvas_templates'] = [template.to_json() for template in self.canvas_templates]

        return json.dumps(data)

    def __str__(self) -> str:
        return str(self.to_json())

    @staticmethod
    def from_object(raw: dict):
        header = Header(
            header_uuid=raw.get('uuid'),
            version=raw.get('version'),
            fdl_creator=raw.get('fdl_creator'),
            default_framing_intent=raw.get('default_framing_intent')
        )
        fdl = FDL(header=header)

        for intent in raw.get('framing_intents', []):
            fdl.framing_intents.append(FramingIntent.from_object(intent))

        for context in raw.get('contexts', []):
            fdl.contexts.append(Context.from_object(context))

        for canvas_template in raw.get('canvas_templates', []):
            fdl.canvas_templates.append(CanvasTemplate.from_object(canvas_template))

        return fdl

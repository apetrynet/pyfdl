import json
import uuid
import jsonschema

from pathlib import Path

from pyfdl import (
    Base,
    Header,
    FramingIntent,
    Context,
    CanvasTemplate,
    TypedList,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION
)


class FDL(Base):
    attributes = [
        'uuid',
        'version',
        'fdl_creator',
        'default_framing_intent',
        'framing_intents',
        'contexts',
        'canvas_templates'
    ]
    kwarg_map = {'uuid': '_uuid'}
    required = ['uuid', 'version']
    defaults = {'uuid': uuid.uuid4, 'fdl_creator': 'PyFDL', 'version': FDL_SCHEMA_VERSION}
    object_map = {
        'framing_intents': FramingIntent,
        'contexts': Context,
        'canvas_templates': CanvasTemplate
    }

    def __init__(
            self,
            _uuid: str = None,
            version: dict = None,
            fdl_creator: str = None,
            default_framing_intent: str = None,
            framing_intents: TypedList[FramingIntent] = None,
            contexts: TypedList[Context] = None,
            canvas_templates: TypedList[CanvasTemplate] = None
    ):
        self.uuid = _uuid
        self.version = version
        self.fdl_creator = fdl_creator
        self.default_framing_intent = default_framing_intent
        self.framing_intents = framing_intents or TypedList(FramingIntent)
        self.contexts = contexts or TypedList(Context)
        self.canvas_templates = canvas_templates or TypedList(CanvasTemplate)
        self._schema = None

    def validate(self):
        if not self._schema:
            self._schema = FDL.load_schema()

        jsonschema.validate(self.to_dict(), self._schema)

    @property
    def header(self) -> Header:
        header = Header.from_dict(self.to_dict())

        return header

    @header.setter
    def header(self, header: Header):
        # Future proof setting of attributes in case Header expands its attributes
        for attr in header.attributes:
            setattr(self, attr, getattr(header, attr))

    @staticmethod
    def load_schema() -> dict:
        schema_path = Path(__file__).parent.joinpath(
            f'schema',
            f'v{FDL_SCHEMA_MAJOR}.{FDL_SCHEMA_MINOR}',
            f'Python_FDL_Checker'
        )
        with schema_path.open('rb') as fp:
            schema = json.load(fp)

        return schema

    def __repr__(self):
        return repr(self.header)

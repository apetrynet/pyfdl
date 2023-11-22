import json
import jsonschema
from pathlib import Path

from pyfdl import Base, Header, FramingIntent, Context, CanvasTemplate, FDL_SCHEMA_MAJOR, FDL_SCHEMA_MINOR


class FDL(Base):
    attributes = ['header', 'framing_intents', 'contexts', 'canvas_templates']
    required = ['header']
    object_map = {
        'header': Header,
        'framing_intents': FramingIntent,
        'contexts': Context,
        'canvas_templates': CanvasTemplate
    }

    def __init__(
            self,
            header: Header = None,
            framing_intents: list[FramingIntent] = None,
            contexts: list[Context] = None,
            canvas_templates: list[CanvasTemplate] = None
    ):
        self.header = header
        self.framing_intents = framing_intents or []
        self.contexts = contexts or []
        self.canvas_templates = canvas_templates or []
        self._schema = None

    def validate(self):
        if not self._schema:
            self._schema = FDL.load_schema()

        jsonschema.validate(self.to_dict(), self._schema)

    def to_dict(self) -> dict:
        data = self.header.to_dict()
        data['framing_intents'] = [fi.to_dict() for fi in self.framing_intents]
        data['contexts'] = [ctx.to_dict() for ctx in self.contexts]
        data['canvas_templates'] = [template.to_dict() for template in self.canvas_templates]

        return data

    @classmethod
    def from_dict(cls, raw: dict):
        fdl = FDL()
        fdl.header = Header.from_dict(raw)
        fdl.framing_intents = [FramingIntent.from_dict(item) for item in raw.get('framing_intents', [])]
        fdl.contexts = [Context.from_dict(item) for item in raw.get('contexts', [])]
        fdl.canvas_templates = [CanvasTemplate.from_dict(item) for item in raw.get('canvas_templates', [])]

        return fdl

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

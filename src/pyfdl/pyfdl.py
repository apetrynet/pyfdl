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
    TypedCollection,
    FDL_SCHEMA_MAJOR,
    FDL_SCHEMA_MINOR,
    FDL_SCHEMA_VERSION
)
from pyfdl.errors import FDLError, FDLValidationError


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
        self.framing_intents = framing_intents or TypedCollection(FramingIntent)
        self.default_framing_intent = default_framing_intent
        self.contexts = contexts or TypedList(Context)
        self.canvas_templates = canvas_templates or TypedCollection(CanvasTemplate)
        self._schema = None

    def validate(self):
        """Validate the current state of the FDL against the json schema.

        Raises:
            FDLValidationError: if any errors are found
        """
        if not self._schema:
            self._schema = self.load_schema()

        errors = []

        # Check internal relations
        for context in self.contexts:
            for canvas in context.canvases:
                if canvas.source_canvas_id not in context.canvases:
                    errors.append(
                        f'{canvas}.source_canvas_id (canvas.source_canvas_id) not found in '
                        f'registered canvases'
                    )

                for framing_decision in canvas.framing_decisions:
                    if framing_decision.framing_intent_id not in self.framing_intents:
                        errors.append(
                            f'{framing_decision}.framing_intent_id ({framing_decision.framing_intent_id}) '
                            f'not found in registered framing intents'
                        )

        # Check structure and values against json schema
        v = jsonschema.validators.validator_for(self._schema)
        validator = v(schema=self._schema, format_checker=v.FORMAT_CHECKER)
        for error in validator.iter_errors(self.to_dict()):
            errors.append(str(error))

        if errors:
            nl = '\n'
            FDLValidationError(
                f"Validation failed!\n"
                f"{f'{nl}'.join(errors)}"
            )

    @property
    def header(self) -> Header:
        """

        Returns:
            Header: based on attributes
        """
        header = Header.from_dict(self.to_dict())

        return header

    @header.setter
    def header(self, header: Header):
        """

        Args:
            header: Header instance
        """
        # "Future-proof" setting of attributes in case Header expands its attributes
        for attr in header.attributes:
            setattr(self, attr, getattr(header, attr))

    @property
    def default_framing_intent(self) -> str:
        return self._default_framing_intent

    @default_framing_intent.setter
    def default_framing_intent(self, framing_intent_id: str):
        if framing_intent_id and framing_intent_id not in self.framing_intents:
            raise FDLError(
                f"Default framing intent: \"{framing_intent_id}\" not found in "
                f"registered framing intents."
            )

        self._default_framing_intent = framing_intent_id

    def load_schema(self) -> dict:
        """Load a jsonschema based on the version in `Header` or default to current version
        set in [base](common.md)

        Returns:
            schema:
        """
        major = self.version.get('major') if self.version else FDL_SCHEMA_MAJOR
        minor = self.version.get('minor') if self.version else FDL_SCHEMA_MINOR

        schema_path = Path(__file__).parent.joinpath(
            f'schema',
            f'v{major}.{minor}',
            f'ascfdl.schema.json'
        )
        with schema_path.open('rb') as fp:
            schema = json.load(fp)

        return schema

    def __repr__(self):
        return repr(self.header)

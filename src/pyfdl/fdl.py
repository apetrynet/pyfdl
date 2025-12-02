import json

import jsonschema
from pathlib import Path
from typing import Union, Any

from pydantic import field_serializer, PrivateAttr

from pyfdl import FDLValidationError
from pyfdl.common import FDL_SCHEMA_VERSION, FDL_SCHEMA_MINOR, TypedCollection
from pyfdl.canvastemplate import CanvasTemplate
from pyfdl.framingintent import FramingIntent
from pyfdl.canvas import Canvas
from pyfdl.context import Context
from pyfdl.header import Header


class FDL(Header):
    # uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # version: dict[str, int] = Field(default=FDL_SCHEMA_VERSION)
    # fdl_creator: str = Field(default="PyFDL")
    # default_framing_intent: Union[str, None] = None
    framing_intents: TypedCollection[FramingIntent] = TypedCollection[FramingIntent]()
    contexts: TypedCollection[Context] = TypedCollection[Context]()
    canvas_templates: TypedCollection[CanvasTemplate] = TypedCollection[
        CanvasTemplate
    ]()

    _schema: dict[str, Any] = PrivateAttr(default=None)

    def load_schema(self) -> dict:
        """Load a jsonschema based on the version in `Header` or default to current version
        set in [base](common.md)

        Returns:
            schema:
        """
        major = self.version.get("major", FDL_SCHEMA_VERSION)
        minor = self.version.get("minor", FDL_SCHEMA_MINOR)

        schema_path = Path(__file__).parent.joinpath(
            "schema", f"v{major}.{minor}", "ascfdl.schema.json"
        )
        with schema_path.open("rb") as fp:
            schema = json.load(fp)

        return schema

    def place_canvas_in_context(self, context_label: str, canvas: Canvas):
        """Place a canvas in a context. If no context with the provided label exist,
        a new context will be created for you.

        Args:
            context_label: name of existing or to be created context
            canvas: to be placed in context
        """

        context = self.contexts.get_by_id(context_label)
        if context is None:
            context = Context(label=context_label)
            self.contexts.append(context)

        context.canvases.append(canvas)

    @field_serializer("default_framing_intent")
    def _check_default_framing_intent(
        self, framing_intent_id: Union[str, None]
    ) -> Union[str, None]:
        if framing_intent_id is None:
            return None

        if self.framing_intents.get_by_id(framing_intent_id) is None:
            raise ValueError(
                f'Default framing intent: "{framing_intent_id}" '
                "is not found among registered framing intents"
            )

        return framing_intent_id

    # @model_serializer()
    def _validate(self):
        """Validate the current state of the FDL.
         ID's and relationships between items are checked and values are
         validated against the json schema.

        Raises:
            FDLValidationError: if any errors are found
        """
        if not self._schema:
            self._schema = self.load_schema()

        errors = []

        # Check if default framing intent is present
        if (
            self.default_framing_intent
            and self.default_framing_intent not in self.framing_intents
        ):
            errors.append(
                f'Default framing intent: "{self.default_framing_intent}" '
                "not found in registered framing intents."
            )

        # Check internal relations
        canvases = TypedCollection[Canvas]()
        canvas_collections = [context.canvases for context in self.contexts]

        for canvas_collection in canvas_collections:
            for canvas in canvas_collection:
                canvases.append(canvas)

        for canvas in canvases:
            if canvases.get_by_id(canvas.source_canvas_id) is None:
                errors.append(
                    f'canvas.source_canvas_id: "{canvas.source_canvas_id}" not found among registered canvases'
                )
                # raise ValueError(
                #     f'canvas.source_canvas_id: "{canvas.source_canvas_id}" not found among registered canvases'
                # )

            for framing_decision in canvas.framing_decisions:
                if framing_decision.framing_intent_id not in self.framing_intents:
                    errors.append(
                        f'framing_decision.framing_intent_id: "{framing_decision.framing_intent_id}" '
                        "not found among registered framing intents"
                    )
                    # raise ValueError(
                    #     f'framing_decision.framing_intent_id: "{framing_decision.framing_intent_id}" '
                    #     "not found among registered framing intents"
                    # )

        # Check structure and values against json schema
        json_v = jsonschema.validators.validator_for(self._schema)
        validator = json_v(schema=self._schema, format_checker=json_v.FORMAT_CHECKER)
        for error in validator.iter_errors(
            self.model_dump(by_alias=True, exclude_none=True)
        ):
            errors.append(str(error))
            # raise ValueError(str(error))

        if errors:
            nl = "\n"
            msg = f"Validation failed!\n{f'{nl}'.join(errors)}"
            raise FDLValidationError(msg)

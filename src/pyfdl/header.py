import uuid

from pyfdl import FDL_SCHEMA_VERSION, Base


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

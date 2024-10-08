from typing import Optional

from pyfdl import FDL_SCHEMA_VERSION, Base


class Header(Base):
    def __init__(
        self,
        uuid_: Optional[str] = None,
        version: Optional[dict] = None,
        fdl_creator: Optional[str] = None,
        default_framing_intent: Optional[str] = None,
    ):
        super().__init__()
        self.attributes = ["uuid", "version", "fdl_creator", "default_framing_intent"]
        self.kwarg_map = {"uuid": "uuid_"}
        self.required = ["uuid", "version"]
        self.defaults = {"uuid": Base.generate_uuid, "fdl_creator": "PyFDL", "version": FDL_SCHEMA_VERSION}

        self.uuid = uuid_
        self.version = version
        self.fdl_creator = fdl_creator
        self.default_framing_intent = default_framing_intent

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f'uuid="{self.uuid}", '
            f"version={self.version}, "
            f'fdl_creator="{self.fdl_creator}", '
            f'default_framing_intent="{self.default_framing_intent}"'
            f")"
        )

import uuid
from typing import Union

from pydantic import BaseModel, Field

from fdl.common import FDL_SCHEMA_MAJOR, FDL_SCHEMA_MINOR


class Version(BaseModel):
    major: int = FDL_SCHEMA_MAJOR
    minor: int = FDL_SCHEMA_MINOR


class Header(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: Version = Field(default_factory=Version)
    fdl_creator: str = Field(default="PyFDL")
    default_framing_intent: Union[str, None] = None

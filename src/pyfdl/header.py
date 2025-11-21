import uuid
from typing import Union

from pydantic import BaseModel, Field

from pyfdl import FDL_SCHEMA_VERSION


class Header(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: dict[str, int] = Field(default=FDL_SCHEMA_VERSION)
    fdl_creator: str = Field(default="PyFDL")
    default_framing_intent: Union[str, None] = None

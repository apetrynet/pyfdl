from typing import Union, Annotated

from pydantic import BaseModel, Field

from pyfdl.common import Dimensions


class FramingIntent(BaseModel):
    label: Union[str, None] = None
    id: str
    aspect_ratio: Dimensions[int]
    protection: Annotated[float, Field(default=0)]

    def __eq__(self, other) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __hash__(self):
        return hash((self.id,))

    def __str__(self) -> str:
        return self.__repr__()

from typing import Union, Annotated

from pydantic import BaseModel, Field

from fdl.types import DimensionsInt


class FramingIntent(BaseModel):
    label: Union[str, None] = None
    id: Annotated[str, Field(min_length=1, max_length=32)]
    aspect_ratio: DimensionsInt
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

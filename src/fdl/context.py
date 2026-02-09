from typing import Union

from pydantic import BaseModel

from fdl import ClipID, TypedCollection, Canvas


class Context(BaseModel):
    label: Union[str, None] = None
    context_creator: Union[str, None] = None
    clip_id: Union[ClipID, None] = None
    canvases: TypedCollection[Canvas] = TypedCollection[Canvas]()

    def __eq__(self, other) -> bool:
        try:
            return self.label == other.label
        except AttributeError:
            return self.label == other

    def __hash__(self):
        return hash((self.label,))

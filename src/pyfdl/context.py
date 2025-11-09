from typing import Optional

from pyfdl import Base, Canvas, TypedCollection
from pyfdl.clipid import ClipID


class Context(Base):
    def __init__(
        self,
        label: Optional[str] = None,
        context_creator: Optional[str] = None,
        canvases: Optional[TypedCollection] = None,
        clip_id: Optional[ClipID] = None,
    ):
        super().__init__()
        self.attributes = ["label", "context_creator", "clip_id", "canvases"]
        self.defaults = {"context_creator": "PyFDL"}
        self.object_map = {"clip_id": ClipID, "canvases": Canvas}
        self.id_attribute = "label"

        self.label = label
        self.context_creator = context_creator
        self.clip_id = clip_id
        self.canvases = canvases or TypedCollection(Canvas)

    def __eq__(self, other):
        return self.label == other.label

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}")'

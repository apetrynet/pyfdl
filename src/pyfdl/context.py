from typing import Optional

from pyfdl import Base, Canvas, TypedCollection


class Context(Base):
    attributes = ["label", "context_creator", "canvases"]
    defaults = {"context_creator": "PyFDL"}
    object_map = {"canvases": Canvas}
    id_attribute = "label"

    def __init__(
        self,
        label: Optional[str] = None,
        context_creator: Optional[str] = None,
        canvases: Optional[TypedCollection] = None,
    ):
        super().__init__()
        self.label = label
        self.context_creator = context_creator
        self.canvases = canvases or TypedCollection(Canvas)

    def __eq__(self, other):
        return self.label == other.label

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}")'

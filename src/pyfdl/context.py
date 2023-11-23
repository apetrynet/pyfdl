from pyfdl import Canvas
from pyfdl.base import Base


class Context(Base):
    attributes = ['label', 'context_creator', 'canvases']
    object_map = {'canvases': Canvas}

    def __init__(self, label: str = None, context_creator: str = None, canvases: list = None):
        self.label = label
        self.context_creator = context_creator
        self.canvases = canvases or []

    # TODO verify appending canvases

    def __repr__(self):
        return f"{self.__class__.__name__}(label={self.label})"

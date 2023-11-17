from pyfdl import Canvas
from pyfdl.base import Base


class Context(Base):
    attributes = ['label', 'context_creator', 'canvases']
    object_map = {'canvases': Canvas}

    def __init__(self, label: str = None, context_creator: str = None, canvases: list = None):
        self.label = label or ''
        self.context_creator = context_creator or ''
        self.canvases = canvases or []

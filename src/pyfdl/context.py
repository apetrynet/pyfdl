from pyfdl import Base, Canvas, TypedContainer


class Context(Base):
    attributes = ['label', 'context_creator', 'canvases']
    object_map = {'canvases': Canvas}

    def __init__(self, label: str = None, context_creator: str = None, canvases: TypedContainer = None):
        self.label = label
        self.context_creator = context_creator
        self.canvases = canvases or TypedContainer(Canvas)

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}")'

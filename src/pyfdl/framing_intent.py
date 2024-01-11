from typing import Union

from pyfdl import Base, DimensionsInt, TypedContainer


class FramingIntent(Base):

    attributes = ['id', 'label', 'aspect_ratio', 'protection']
    kwarg_map = {'id': '_id'}
    object_map = {'aspect_ratio': DimensionsInt}
    required = ['id', 'aspect_ratio']
    defaults = {'protection': 0}

    def __init__(
            self,
            label: str = None,
            _id: str = None,
            aspect_ratio: DimensionsInt = None,
            protection: float = None,
            parent: TypedContainer = None
    ):
        self.parent = parent
        self.id = _id
        self.label = label
        self.aspect_ratio = aspect_ratio
        self.protection = protection

    @property
    def parent(self) -> Union[TypedContainer, None]:
        return self._parent

    @parent.setter
    def parent(self, parent: TypedContainer):
        self._parent = parent

    def __repr__(self):
        return f'{self.__class__.__name__}(label="{self.label}", id="{self.id}")'

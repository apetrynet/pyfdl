from typing import Union

from pyfdl import Base, DimensionsInt, TypedCollection


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
            protection: float = None
    ):
        self.id = _id
        self.label = label
        self.aspect_ratio = aspect_ratio
        self.protection = protection

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'label="{self.label}", '
                f'id="{self.id}", '
                f'aspect_ratio={self.aspect_ratio}, '
                f'protection={self.protection}'
                f')'
                )

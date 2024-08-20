from typing import Union

from pyfdl import Base, Dimensions


class FramingIntent(Base):
    attributes = ["id", "label", "aspect_ratio", "protection"]
    kwarg_map = {"id": "id_"}
    object_map = {"aspect_ratio": Dimensions}
    required = ["id", "aspect_ratio"]
    defaults = {"protection": 0}

    def __init__(self, label: str = None, id_: str = None, aspect_ratio: Dimensions = None, protection: float = None):
        super().__init__()
        self.id = id_
        self.label = label
        self.aspect_ratio = aspect_ratio
        self.protection = protection

    @property
    def aspect_ratio(self) -> Union[Dimensions, None]:
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, dim: Union[Dimensions, None]):
        self._aspect_ratio = dim
        if dim is not None:
            self._aspect_ratio.dtype = int

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f'label="{self.label}", '
            f'id="{self.id}", '
            f"aspect_ratio={self.aspect_ratio}, "
            f"protection={self.protection}"
            f")"
        )

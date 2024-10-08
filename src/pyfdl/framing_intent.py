from typing import Optional, Union

from .common import Base, Dimensions


class FramingIntent(Base):
    def __init__(
        self,
        label: Optional[str] = None,
        id_: Optional[str] = None,
        aspect_ratio: Optional[Dimensions] = None,
        protection: Optional[float] = None,
    ):
        super().__init__()
        self.attributes = ["id", "label", "aspect_ratio", "protection"]
        self.kwarg_map = {"id": "id_"}
        self.object_map = {"aspect_ratio": Dimensions}
        self.required = ["id", "aspect_ratio"]
        self.defaults = {"protection": 0}

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

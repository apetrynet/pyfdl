from pyfdl import Base, DimensionsInt


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

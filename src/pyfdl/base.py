from abc import ABC, abstractmethod

from pyfdl.errors import FDLError

FDL_SCHEMA_MAJOR = 1
FDL_SCHEMA_MINOR = 0
FDL_SCHEMA_VERSION = {'major': FDL_SCHEMA_MAJOR, 'minor': FDL_SCHEMA_MINOR}


class Base(ABC):
    attributes = []
    kwarg_map = {}
    object_map = {}
    required = []
    defaults = {}

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def apply_defaults(self):
        """Applies default values, if any, to attributes that are `None`"""
        for key, value in self.defaults.items():
            if getattr(self, key) is None:
                if callable(value):
                    setattr(self, key, value())

                elif isinstance(value, Base):
                    setattr(self, key, value.apply_defaults())

                else:
                    setattr(self, key, value)

    def check_required(self) -> list:
        missing = []
        for required_key in self.required:
            # Check for dependant attributes.
            # Like "effective_anchor_point" required if "effective_dimensions" is provided
            if '.' in required_key:
                attr1, attr2 = required_key.split('.')
                if getattr(self, attr1) is not None and getattr(self, attr2) is None:
                    missing.append(attr2)

            elif getattr(self, required_key) is None:
                missing.append(required_key)

        return missing

    def to_dict(self) -> dict:
        data = {}
        for key in self.attributes:
            value = getattr(self, key)

            # check if empty value should be omitted
            if key not in self.required and not value:
                continue

            # Arrays (aka lists) contain other objects
            if isinstance(value, list):
                value = [item.to_dict() for item in value]

            # This should cover all known objects
            elif isinstance(value, Base):
                value = value.to_dict()

            data[key] = value

        missing = self.check_required()
        if missing:
            raise FDLError(f'{repr(self)} is missing some required attributes: {missing}')

        return data

    @classmethod
    def from_dict(cls, raw: dict):
        kwargs = {}
        for key in cls.attributes:
            # We get the value before we convert the key to a valid name
            value = raw.get(key)
            if value is None:
                continue

            # Check for keyword override
            keyword = cls.kwarg_map.get(key, key)

            if key in cls.object_map:
                if isinstance(value, list):
                    value = [cls.object_map[key].from_dict(item) for item in value]

                else:
                    value = cls.object_map[key].from_dict(value)

            kwargs[keyword] = value

        return cls(**kwargs)

    def __repr__(self) -> str:
        return f'"{self.__class__.__name__}"'

    def __str__(self) -> str:
        return str(self.to_dict())


class DimensionsFloat(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


class DimensionsInt(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height


class PointFloat(Base):
    attributes = ['x', 'y']
    required = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class RoundStrategy(Base):
    attributes = ['even', 'mode']

    VALID_EVEN = ('even', 'whole')
    VALID_MODES = ('up', 'down', 'round')
    defaults = {'even': 'even', 'mode': 'up'}

    def __init__(self, even: str = None, mode: str = None):
        self.even = even
        self.mode = mode

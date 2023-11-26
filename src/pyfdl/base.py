from abc import ABC, abstractmethod
from collections import UserList
from collections.abc import MutableSequence
from typing import Type

from pyfdl.errors import FDLError

FDL_SCHEMA_MAJOR = 1
FDL_SCHEMA_MINOR = 0
FDL_SCHEMA_VERSION = {'major': FDL_SCHEMA_MAJOR, 'minor': FDL_SCHEMA_MINOR}


class Base(ABC):
    # Holds a list of known attributes
    attributes = []
    # Maps attribute names that clash with reserved builtin functions to safe alternatives (id -> _id)
    kwarg_map = {}
    # Map keys to custom classes
    object_map = {}
    # List of required attributes
    required = []
    # Default values for attributes
    defaults = {}

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def apply_defaults(self):
        """Applies default values, if any, to attributes that are `None`"""
        for key, value in self.defaults.items():
            if getattr(self, key) is None:
                # value is a function
                if callable(value):
                    setattr(self, key, value())
                # value is an instance of PyFDL a class
                elif isinstance(value, Base):
                    setattr(self, key, value.apply_defaults())
                # Value is an attribute of this instance
                elif 'self.' in value:
                    setattr(self, key, getattr(self, value.strip('self.')))
                # Value is whatever
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
                # Keys with arrays as values should pass (for now?)
                if not isinstance(value, VerifiedList):
                    continue

            # Arrays (aka lists) contain other objects
            if isinstance(value, VerifiedList):
                value = [item.to_dict() for item in value]

            # This should cover all known objects
            elif isinstance(value, (Base, VerifiedList)):
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
                    _cls = cls.object_map[key]
                    value = VerifiedList(_cls, [_cls.from_dict(item) for item in value])

                else:
                    value = cls.object_map[key].from_dict(value)

            kwargs[keyword] = value

        return cls(**kwargs)

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        return str(self.to_dict())


class VerifiedList(UserList):
    def __init__(self, cls: Type[Base], items: list = None):
        super().__init__()
        self._cls = cls
        if items:
            self.extend(items)

    def append(self, item):
        self.insert(self.__len__(), item)

    def extend(self, other):
        for item in other:
            self.append(item)

    def insert(self, i, item):
        if not isinstance(item, self._cls):
            raise TypeError(
                f"This list does not accept items of type: \"{type(item)}\". "
                f"Please provide items of type: \"{self._cls}\""
            )

        super().insert(i, item)


class DimensionsFloat(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, height={self.height})"


class DimensionsInt(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: int, height: int):
        self.width = width.__int__()
        self.height = height.__int__()

    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, height={self.height})"


class Point(Base):
    attributes = ['x', 'y']
    required = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"


class RoundStrategy(Base):
    attributes = ['even', 'mode']
    required = ['even', 'mode']
    defaults = {'even': 'even', 'mode': 'up'}

    def __init__(self, even: str = None, mode: str = None):
        self.even = even
        self.mode = mode

    @property
    def even(self):
        return self._even

    @even.setter
    def even(self, value):
        valid_options = ('even', 'whole')
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "even".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._even = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        valid_options = ('up', 'down', 'round')
        if value is not None and value not in valid_options:
            raise FDLError(
                f'"{value}" is not a valid option for "mode".\n'
                f'Please use one of the following: {valid_options}'
            )

        self._mode = value

    def __repr__(self):
        return f'{self.__class__.__name__}(even="{self.even}", mode="{self.mode}")'

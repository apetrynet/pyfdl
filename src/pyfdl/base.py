from abc import ABC, abstractmethod
from collections import UserList
from typing import Type, Any, Union

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
    def __init__(self, *args: Any, **kwargs: Any):
        """Base class not to be instanced directly.

            Args:
                *args:
                **kwargs:

            Attributes:
                attributes: list of attributes described in FDL spec
                kwarg_map: map attribute names that clash with reserved builtin python functions to safe alternatives
                    like: (id -> _id) and (uuid -> _uuid)
                object_map: map attributes to custom classes
                required: list of required attributes.
                    Supports linked attributes like: "effective_dimensions.effective_anchor_point" where
                    "effective_anchor_point" is required if "effective_dimensions" is set
                defaults: map default values to attributes. In addition to primitive values supports: callable,
                    subclasses of [Base](#Base)

            """
        pass

    def apply_defaults(self) -> None:
        """Applies default values defined in the `defaults` attribute to attributes that are `None`"""

        for key, value in self.defaults.items():
            if getattr(self, key) is None:
                # value is a function
                if callable(value):
                    setattr(self, key, value())
                # value is an instance of PyFDL a class
                elif isinstance(value, Base):
                    setattr(self, key, value.apply_defaults())
                # Value is an attribute of this instance
                elif isinstance(value, str) and 'self.' in value:
                    setattr(self, key, getattr(self, value.strip('self.')))
                # Value is whatever
                else:
                    setattr(self, key, value)

    def check_required(self) -> list:
        """Check that required attributes contain values.
        Checks linked attributes like: "effective_dimensions.effective_anchor_point" where
        "effective_anchor_point" is required if "effective_dimensions" is set

        Returns:
            a list of missing attributes
        """

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
        """
        Produce a dictionary representation of the current object along with all sub objects.

        Raises:
           FDLError: if required keys are missing

        Returns:
            representation of object
        """
        data = {}
        for key in self.attributes:
            value = getattr(self, key)

            # check if empty value should be omitted
            if key not in self.required and not value:
                # Keys with arrays as values should pass (for now?)
                if not isinstance(value, (TypedList, TypedCollection)):
                    continue

            # Arrays (aka lists) contain other objects
            if isinstance(value, (TypedList, TypedCollection)):
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
    def from_dict(cls, raw: dict, parent: Any = None) -> Any:
        """Create instances of classes from a provided dict.

        Args:
            parent: is used in collections of items
            raw: dictionary to convert to supported classes

        Returns:
            cls: and instance of the current class
        """
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
                    # TODO consider using TypedContainer for all and put the id stuff in there
                    if 'id' in _cls.attributes:
                        tc = TypedCollection(_cls)
                        for item in value:
                            tc.add_item(_cls.from_dict(item, parent=tc))
                        value = tc
                    else:
                        value = TypedList(_cls, [_cls.from_dict(item) for item in value])
                else:
                    value = cls.object_map[key].from_dict(value)

            kwargs[keyword] = value

        if parent:
            kwargs['parent'] = parent

        return cls(**kwargs)

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        return str(self.to_dict())


class TypedCollection:
    def __init__(self, cls: Any):
        """Collection only accepting items of a given class.
        In addition, a strict control of unique id's is enforced.

        Args:
            cls: type of class to be accepted
        """
        self._cls = cls
        self._data = {}

    def add_item(self, item: Any):
        """Add an item to the collection.
         All items added to a collection get associated to the collection by passing itself
         as parent

        Args:
            item: of type passed at instancing of the collection.

        Raises:
            FDLError: for missing id or if a duplicate id is detected
        """
        if not isinstance(item, self._cls):
            raise TypeError(
                f"This container does not accept items of type: \"{type(item)}\". "
                f"Please provide items of type: \"{self._cls}\""
            )

        if item.id:
            _item = self._data.setdefault(item.id, item)
            if _item != item:
                raise FDLError(
                    f"{item.__class__.__name__}.id ({item.id}) already exists. ID's must be unique."
                )

        else:
            raise FDLError(f"Item must have a valid ID (not None or empty string)")

        item.parent = self

    def get_item(self, item_id: str) -> Union[Any, None]:
        """Get an item in the collection

        Args:
            item_id: id of item you'd like to get

        Returns:
            item: in collection or `None` if not found
        """
        return self._data.get(item_id)

    def remove_item(self, item_id: str):
        """Remove an item in the collection if found

        Args:
            item_id: id of item to be removed
        """
        if item_id in self._data:
            del self._data[item_id]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for item in self._data.values():
            yield item

    def __contains__(self, item: Any) -> bool:
        # We support both looking for an item by item.id and "string" for future use of collection
        try:
            return item.id in self._data

        except AttributeError:
            return item in self._data


class TypedList(UserList):
    def __init__(self, cls: Type[Base], items: list = None):
        """A list that only accepts items of a given type

        Args:
            cls: accepted class for this instance. Example [FramingDecision](framing_decision.md)
            items: an initial list of items
        """
        super().__init__()
        self._cls = cls
        if items:
            self.extend(items)

    def append(self, item: Type[Base]) -> None:
        """Append an item to the list.

        Args:
            item: of same class as defined when instanced

        Raises:
            TypeError: if wrong type of item is provided
        """
        self.insert(self.__len__(), item)

    def extend(self, other: list[Type[Base]]) -> None:
        """Extend list with a list of same type of items

        Args:
            other: items to merge with this list

        Raises:
            TypeError: if other list contains items of a different class than this one
        """
        for item in other:
            self.append(item)

    def insert(self, i: int, item: Type[Base]) -> None:
        """Insert an item at the given position of the list

        Args:
            i: index a.k.a position of the item
            item: an item of the given class to insert in this list

        Raises:
            TypeError: if wrong type of item is provided
        """
        if not isinstance(item, self._cls):
            raise TypeError(
                f"This list does not accept items of type: \"{type(item)}\". "
                f"Please provide items of type: \"{self._cls}\""
            )

        self.data.insert(i, item)


class DimensionsFloat(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: float, height: float):
        """Dimensions properly formatted and stored as floats

        Args:
            width:
            height:
        """
        self.width = width
        self.height = height

    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, height={self.height})"


class DimensionsInt(Base):
    attributes = ['width', 'height']
    required = ['width', 'height']

    def __init__(self, width: int, height: int):
        """Dimensions properly formatted and stored as ints

        Args:
            width:
            height:
        """
        self.width = width.__int__()
        self.height = height.__int__()

    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, height={self.height})"


class Point(Base):
    attributes = ['x', 'y']
    required = ['x', 'y']

    def __init__(self, x: float, y: float):
        """Point properly formatted

        Args:
            x:
            y:
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"


class RoundStrategy(Base):
    attributes = ['even', 'mode']
    required = ['even', 'mode']
    defaults = {'even': 'even', 'mode': 'up'}

    def __init__(self, even: str = None, mode: str = None):
        """Describes how to handle rounding of values.

        Args:
            even:
                "whole" = to nearest integer,
                "even" = to nearest even-numbered integer

            mode:
                "up" = always round up,
                "down" = always round down

        Raises:
            FDLError: if you provide a value other than the ones listed above
        """
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

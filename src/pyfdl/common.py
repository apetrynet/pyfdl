import math
import uuid
from typing import Any, Optional, Union

from pyfdl.errors import FDLError

FDL_SCHEMA_MAJOR = 1
FDL_SCHEMA_MINOR = 0
FDL_SCHEMA_VERSION = {"major": FDL_SCHEMA_MAJOR, "minor": FDL_SCHEMA_MINOR}

_ROUNDING = None
NO_ROUNDING = {}
DEFAULT_ROUNDING_STRATEGY = NO_ROUNDING


def set_rounding_strategy(rules: Union[dict, None]):
    global _ROUNDING  # noqa

    if rules is None:
        rules = NO_ROUNDING

    _ROUNDING = RoundStrategy(**rules)


def rounding_strategy() -> "RoundStrategy":
    if _ROUNDING is None:
        set_rounding_strategy(DEFAULT_ROUNDING_STRATEGY)

    return _ROUNDING


class Base:
    def __init__(self):
        """Base class not to be instanced directly.

        Attributes:
            attributes: list of attributes described in FDL spec
            kwarg_map: map attribute names that clash with reserved builtin python functions to safe alternatives
                like: (id -> id_) and (uuid -> uuid_)
            object_map: map attributes to custom classes
            required: list of required attributes.
                Supports linked attributes like: "effective_dimensions.effective_anchor_point" where
                "effective_anchor_point" is required if "effective_dimensions" is set
            defaults: map default values to attributes. In addition to primitive values supports: callable,
                subclasses of [Base](common.md#pyfdl.Base)

        """
        # Holds a list of known attributes
        self.attributes = []
        # Maps attribute names that clash with reserved builtin functions to safe alternatives (id -> id_)
        self.kwarg_map = {}
        # Map keys to custom classes
        self.object_map = {}
        # List of required attributes
        self.required = []
        # Default values for attributes
        self.defaults = {}
        # Attribute used as a unique identifier
        self.id_attribute = "id"

    @property
    def rounding_strategy(self) -> "RoundStrategy":
        return rounding_strategy()

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
                elif isinstance(value, str) and "self." in value:
                    setattr(self, key, getattr(self, value.strip("self.")))
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
            if "." in required_key:
                attr1, attr2 = required_key.split(".")
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
            if key not in self.required and not value and not isinstance(value, TypedCollection):
                # Keys with arrays as values should pass (for now?)
                continue

            # Arrays (aka lists) contain other objects
            if isinstance(value, TypedCollection):
                value = value.to_list()

            # This should cover all known objects
            elif isinstance(value, Base):
                value = value.to_dict()

            data[key] = value

        missing = self.check_required()
        if missing:
            msg = f"{self!r} is missing some required attributes: {missing}"
            raise FDLError(msg)

        return data

    @classmethod
    def from_dict(cls, raw: dict) -> Any:
        """Create instances of classes from a provided dict.

        Args:
            raw: dictionary to convert to supported classes

        Returns:
            cls: and instance of the current class
        """
        kwargs = {}
        # We only use this to get access to attributes
        _tmp_instance = cls()

        for key in _tmp_instance.attributes:
            # We get the value before we convert the key to a valid name
            value = raw.get(key)
            if value is None:
                continue

            # Check for keyword override
            keyword = _tmp_instance.kwarg_map.get(key, key)

            if key in _tmp_instance.object_map:
                if isinstance(value, list):
                    _cls = _tmp_instance.object_map[key]

                    tc = TypedCollection(_cls)
                    for item in value:
                        tc.add(_cls.from_dict(item))
                    value = tc
                else:
                    value = _tmp_instance.object_map[key].from_dict(value)

            kwargs[keyword] = value

        return cls(**kwargs)

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

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

    @property
    def ids(self):
        return list(self._data.keys())

    def add(self, item: Any):
        """Add an item to the collection.
         All items added to a collection get associated to the collection by passing itself
         as parent

        Args:
            item: of type passed at instancing of the collection.

        Raises:
            FDLError: for missing id or if a duplicate id is detected
        """

        if not isinstance(item, self._cls):
            msg = (
                f'This container does not accept items of type: "{type(item)}". '
                f'Please provide items of type: "{self._cls}"'
            )
            raise TypeError(msg)

        item_id = self._get_item_id(item)

        if item_id:
            if item_id in self._data:
                msg = f'{item.__class__.__name__}.{item.id_attribute} ("{item_id}") already exists.'
                raise FDLError(msg)
            self._data[item_id] = item

        else:
            msg = f'Item must have a valid identifier ("{item.id_attribute}"), not None or empty string'
            raise FDLError(msg)

    def get(self, item_id: str) -> Union[Any, None]:
        """Get an item in the collection

        Args:
            item_id: id of item you'd like to get

        Returns:
            item: in collection or `None` if not found
        """
        return self._data.get(item_id)

    def remove(self, item_id: str):
        """Remove an item in the collection if found

        Args:
            item_id: id of item to be removed
        """
        if item_id in self._data:
            del self._data[item_id]

    def to_list(self) -> list[dict]:
        return [item.to_dict() for item in self]

    def _get_item_id(self, item: Any) -> str:
        """
        Get the "id" of the item based on the item's `id_attribute`

        Args:
            item:

        Returns:
            id:
        """
        return getattr(item, item.id_attribute)

    def __bool__(self):
        return bool(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        yield from self._data.values()

    def __getitem__(self, item):
        return self.get(self.ids[item])

    def __contains__(self, item: Any) -> bool:
        # We support both looking for an item by item.id and "string" for future use of collection
        try:
            item_id = self._get_item_id(item)
            return item_id in self._data  # noqa

        except AttributeError:
            return item in self._data


class Dimensions(Base):
    def __init__(
        self,
        width: Optional[Union[int, float]] = None,
        height: Optional[Union[int, float]] = None,
        dtype: Optional[Union[int, float]] = float,
    ):
        """
        Dimensions may be either `ints` or `floats`. You may pass the desired data type at instantiation.
        However, the objects using the dimensions will set the required type for you when they are passed
        to them

        Args:
            width:
            height:
            dtype: set data type of dimension values, mostly used behind the scenes.
        """

        super().__init__()
        self.attributes = ["width", "height"]
        self.required = ["width", "height"]

        self.dtype = dtype

        self.width = width
        self.height = height

    def scale_by(self, factor: float) -> None:
        """
        Scale the dimensions by the provider factor

        Args:
            factor:
        """
        self.width *= factor
        self.height *= factor

        if self.dtype == int:
            self.width, self.height = self.rounding_strategy.round_dimensions(self)

    def copy(self) -> "Dimensions":
        """
        Create a copy of these dimensions

        Returns:
            copy: of these dimensions
        """

        return Dimensions(width=self.width, height=self.height, dtype=self.dtype)

    def to_dict(self) -> dict:
        # TODO: do we round before casting to int?
        return {"width": self.dtype(self.width), "height": self.dtype(self.height)}

    def __iter__(self):
        return iter((self.width, self.height))

    def __lt__(self, other):
        return self.width < other.width or self.height < other.height

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height

    def __gt__(self, other):
        return self.width > other.width or self.height > other.height

    def __bool__(self):
        return self.width is not None and self.height is not None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(" f"width={self.dtype(self.width)}, " f"height={self.dtype(self.height)}" f")"
        )


class Point(Base):
    def __init__(self, x: Optional[float] = None, y: Optional[float] = None):
        """Point properly formatted

        Args:
            x:
            y:
        """
        super().__init__()
        self.attributes = ["x", "y"]
        self.required = ["x", "y"]

        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"


class RoundStrategy(Base):
    def __init__(self, even: Optional[str] = None, mode: Optional[str] = None):
        """Describes how to handle rounding canvas dimensions when applying a
        [CanvasTemplate](canvas_template.md#pyfdl.CanvasTemplate).

        Args:
            even:
                "whole" = to nearest integer,
                "even" = to nearest even-numbered integer

            mode:
                "up" = always round up,
                "down" = always round down
                "round" = standard rounding, >= +0.5 rounds up,< +0.5 rounds down

        Raises:
            FDLError: if you provide a value other than the ones listed above
        """
        super().__init__()
        self.attributes = ["even", "mode"]
        self.required = ["even", "mode"]
        self.defaults = {"even": "even", "mode": "up"}

        self.even = even
        self.mode = mode

    @property
    def rounding_strategy(self) -> "RoundStrategy":
        return self

    @property
    def even(self):
        return self._even

    @even.setter
    def even(self, value):
        valid_options = ("even", "whole")
        if value is not None and value not in valid_options:
            msg = f'"{value}" is not a valid option for "even".\n' f"Please use one of the following: {valid_options}"

            raise FDLError(msg)

        self._even = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        valid_options = ("up", "down", "round")
        if value is not None and value not in valid_options:
            msg = f'"{value}" is not a valid option for "mode".\n' f"Please use one of the following: {valid_options}"
            raise FDLError(msg)

        self._mode = value

    def round_dimensions(self, dimensions: Dimensions) -> Dimensions:
        """
        Round the provided dimensions based on the rules defined in this object

        Args:
            dimensions:

        Returns:
            dimensions: rounded based on rules

        """

        mode_map = {"up": math.ceil, "down": math.floor, "round": round}

        width = dimensions.width
        height = dimensions.height

        adjust = 1
        if self.even == "even":
            adjust = 2

        if self.mode is not None:
            width = mode_map[self.mode](width / adjust) * adjust
            height = mode_map[self.mode](height / adjust) * adjust

        return Dimensions(width=width, height=height, dtype=dimensions.dtype)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.even == other.get("even") and self.mode == other.get("mode")

        return self.even == other.even and self.mode == other.mode

    def __repr__(self):
        return f'{self.__class__.__name__}(even="{self.even}", mode="{self.mode}")'

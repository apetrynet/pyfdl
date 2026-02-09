import math
from collections.abc import Iterable
from typing import Generic, Any, get_args, Self, List, Union, Iterator, TypeVar

from pydantic import BaseModel, Field, PrivateAttr, RootModel, model_serializer

import fdl.config as config
from fdl.rounding import fdl_round


T = TypeVar("T")


FDL_SCHEMA_MAJOR = 2
FDL_SCHEMA_MINOR = 1
FDL_SCHEMA_VERSION = {"major": FDL_SCHEMA_MAJOR, "minor": FDL_SCHEMA_MINOR}


class Dimensions(BaseModel, Generic[T]):
    width: T = Field(ge=0, default=0)
    height: T = Field(ge=0, default=0)
    _dtype: T = PrivateAttr()

    def model_post_init(self, context: Any, /) -> None:
        self._dtype = self.__class__.model_fields["width"].annotation

    def scale_by(self, factor: float) -> None:
        """Scale the dimensions by the provided factor."""
        self.width *= factor
        self.height *= factor

        if self._dtype is int:
            self.width, self.height = config.get_rounding().round_dimensions(self)

    def duplicate(self) -> Self:
        """Create a duplicate of these dimensions."""
        return self.__class__(width=self.width, height=self.height)

    @classmethod
    def from_dimensions(cls, dims: "Dimensions") -> "Dimensions[float]":
        """Create float Dimensions from any Dimensions instance."""
        result = Dimensions[float]()
        result.width = float(dims.width)
        result.height = float(dims.height)
        return result

    def is_zero(self) -> bool:
        """Check if both width and height are zero."""
        return self.width == 0 and self.height == 0

    def normalize(self, squeeze: float) -> "Dimensions[float]":
        """Normalize dimensions by applying anamorphic squeeze to width.

        Per spec 7.4.5: All applications reading an ASC FDL will apply the squeeze factor
        before any scaling to ensure consistency.
        """
        result = Dimensions[float]()
        result.width = float(self.width) * squeeze
        result.height = float(self.height)
        return result

    def scale(self, scale_factor: float, target_squeeze: float) -> "Dimensions[float]":
        """Scale normalized dimensions and apply target squeeze.

        Per spec 7.4.5: Order is Desqueeze, then Scale, then apply target squeeze.
        """
        result = Dimensions[float]()
        result.width = (float(self.width) * scale_factor) / target_squeeze
        result.height = float(self.height) * scale_factor
        return result

    def normalize_and_scale(self, input_squeeze: float, scale_factor: float, target_squeeze: float) -> "Dimensions[float]":
        """Normalize and scale dimensions in a single operation."""
        return self.normalize(input_squeeze).scale(scale_factor, target_squeeze)

    def clamp_to_dims(self, clamp_dims: "Dimensions[int]") -> tuple["Dimensions[float]", "Point[float]"]:
        """Clamp dimensions to maximum bounds, returning (clamped_dims, delta_offset)."""
        delta_w = min(0.0, clamp_dims.width - self.width)
        delta_h = min(0.0, clamp_dims.height - self.height)
        new_w = min(float(self.width), float(clamp_dims.width))
        new_h = min(float(self.height), float(clamp_dims.height))

        result_dims = Dimensions[float]()
        result_dims.width = new_w
        result_dims.height = new_h

        result_point = Point[float]()
        result_point.x = delta_w
        result_point.y = delta_h

        return result_dims, result_point

    def to_int(self) -> "Dimensions[int]":
        """Convert to integer dimensions by truncating."""
        if self._dtype is int:
            return self
        result = Dimensions[int]()
        result.width = int(self.width)
        result.height = int(self.height)
        return result

    def round(self, even: str, mode: str) -> "Dimensions[float]":
        """Round dimensions according to FDL rounding rules."""
        result = Dimensions[float]()
        result.width = fdl_round(self.width, even, mode)
        result.height = fdl_round(self.height, even, mode)
        return result

    def __iter__(self):
        return iter((self.width, self.height))

    def __lt__(self, other):
        return self.width < other.width or self.height < other.height

    def __eq__(self, other):
        if not isinstance(other, Dimensions):
            return False
        return math.isclose(self.width, other.width, rel_tol=1e-9, abs_tol=1e-6) and math.isclose(
            self.height, other.height, rel_tol=1e-9, abs_tol=1e-6
        )

    def __hash__(self):
        return hash((self.width, self.height))

    def __gt__(self, other):
        return self.width > other.width or self.height > other.height

    def __sub__(self, other: "Dimensions") -> "Dimensions[float]":
        """Subtract dimensions."""
        result = Dimensions[float]()
        result.width = float(self.width - other.width)
        result.height = float(self.height - other.height)
        return result

    def __bool__(self):
        return bool(self.width) and bool(self.height)

    @model_serializer
    def _serialize(self) -> dict:
        """Ensure proper type serialization based on generic type parameter."""
        if self._dtype is float:
            return {"width": float(self.width), "height": float(self.height)}
        return {"width": self.width, "height": self.height}


class Point(BaseModel, Generic[T]):
    _dtype: T = PrivateAttr()
    x: T = Field(default=0)
    y: T = Field(default=0)

    def model_post_init(self, context: Any, /) -> None:
        self._dtype = self.__class__.model_fields["x"].annotation

    def is_zero(self) -> bool:
        """Check if both x and y are zero."""
        return self.x == 0 and self.y == 0

    def normalize(self, squeeze: float) -> "Point[float]":
        """Normalize point by applying anamorphic squeeze to x coordinate."""
        result = Point[float]()
        result.x = float(self.x) * squeeze
        result.y = float(self.y)
        return result

    def scale(self, scale_factor: float, target_squeeze: float) -> "Point[float]":
        """Scale a normalized point and apply target squeeze."""
        result = Point[float]()
        result.x = (float(self.x) * scale_factor) / target_squeeze
        result.y = float(self.y) * scale_factor
        return result

    def normalize_and_scale(self, input_squeeze: float, scale_factor: float, target_squeeze: float) -> "Point[float]":
        """Normalize and scale point in a single operation."""
        return self.normalize(input_squeeze).scale(scale_factor, target_squeeze)

    def clamp(self, min_val: float = None, max_val: float = None) -> "Point[float]":
        """Clamp point values to specified range."""
        x, y = float(self.x), float(self.y)
        if min_val is not None:
            x, y = max(x, min_val), max(y, min_val)
        if max_val is not None:
            x, y = min(x, max_val), min(y, max_val)
        result = Point[float]()
        result.x = x
        result.y = y
        return result

    def round(self, even: str, mode: str) -> "Point[float]":
        """Round point according to FDL rounding rules."""
        result = Point[float]()
        result.x = fdl_round(self.x, even, mode)
        result.y = fdl_round(self.y, even, mode)
        return result

    @classmethod
    def from_alignment(
        cls,
        container: "Dimensions",
        content: "Dimensions",
        align_h: str,
        align_v: str,
    ) -> "Point[float]":
        """Calculate alignment offset for placing content within a container."""
        align_h = (align_h or "center").lower()
        align_v = (align_v or "center").lower()

        if align_h == "left":
            x = 0.0
        elif align_h == "right":
            x = container.width - content.width
        else:
            x = (container.width - content.width) * 0.5

        if align_v == "top":
            y = 0.0
        elif align_v == "bottom":
            y = container.height - content.height
        else:
            y = (container.height - content.height) * 0.5

        result = Point[float]()
        result.x = x
        result.y = y
        return result

    @classmethod
    def from_content_translation(
        cls,
        container: "Dimensions",
        content: "Dimensions",
        align_h: str,
        align_v: str,
    ) -> "Point[float]":
        """Calculate content translation offset for fill method alignment.

        Used when content is larger than container and needs to be positioned
        within the container bounds.
        """
        align_h = (align_h or "center").lower()
        align_v = (align_v or "center").lower()

        if align_h == "left":
            x = content.width - container.width
        elif align_h == "right":
            x = container.width - content.width
        else:
            x = (content.width - container.width) * 0.5

        if align_v == "top":
            y = content.height - container.height
        elif align_v == "bottom":
            y = container.height - content.height
        else:
            y = (content.height - container.height) * 0.5

        result = Point[float]()
        result.x = x
        result.y = y
        return result

    def __add__(self, other: "Point") -> "Point[float]":
        result = Point[float]()
        result.x = float(self.x) + float(other.x)
        result.y = float(self.y) + float(other.y)
        return result

    def __iadd__(self, other: "Point") -> "Point":
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Point") -> "Point[float]":
        result = Point[float]()
        result.x = float(self.x) - float(other.x)
        result.y = float(self.y) - float(other.y)
        return result

    def __mul__(self, other: Union["Point", float]) -> "Point[float]":
        result = Point[float]()
        if isinstance(other, Point):
            result.x = float(self.x) * float(other.x)
            result.y = float(self.y) * float(other.y)
        elif isinstance(other, (int, float)):
            result.x = float(self.x) * float(other)
            result.y = float(self.y) * float(other)
        else:
            raise TypeError(f"Cannot multiply Point with {type(other)}")
        return result

    def __lt__(self, other: "Point") -> bool:
        return self.x < other.x or self.y < other.y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        return math.isclose(self.x, other.x, rel_tol=1e-9, abs_tol=1e-6) and math.isclose(
            self.y, other.y, rel_tol=1e-9, abs_tol=1e-6
        )

    def __hash__(self):
        return hash((self.x, self.y))

    @model_serializer
    def _serialize(self) -> dict:
        """Ensure proper type serialization based on generic type parameter."""
        if self._dtype is float:
            return {"x": float(self.x), "y": float(self.y)}
        return {"x": self.x, "y": self.y}


class TypedCollection(RootModel[List[T]]):
    root: list[T] = Field(default=list())
    _cls: T = PrivateAttr(default=T)

    def model_post_init(self, context: Any, /) -> None:
        self._cls: T = get_args(self.__class__.model_fields["root"].annotation)[0]

    def get_by_id(self, item_id: str) -> Union[T, None]:
        try:
            return self.root[self.root.index(item_id)]
        except ValueError:
            return None

    def append(self, item: T):
        """Append an item to the collection.

        Args:
            item:

        Raises:
            ValueError: if a duplicate id is detected
        """
        if type(item) is not self._cls:
            raise ValueError(
                f'This collection only accepts items of type: "{self._cls.__name__}", not "{item.__class__.__name__}"'
            )

        if item in self.root:
            raise ValueError(f"{repr(item)} already exists in collection")

        self.root.append(item)

    def remove(self, item_id: str):
        """Remove an item in the collection if found

        Args:
            item_id: id of item to be removed
        """
        if item_id in self.root:
            del self.root[self.root.index(item_id)]

    def __len__(self) -> int:
        return self.root.__len__()

    def __iter__(self) -> Iterator[T]:
        return self.root.__iter__()

    def __bool__(self) -> bool:
        return bool(self.root)

    def __getitem__(self, item) -> T:
        return self.root[item]

    def __contains__(self, item: T) -> bool:
        return item in self.root


# Type aliases for convenience
DimensionsInt = Dimensions[int]
DimensionsFloat = Dimensions[float]
PointFloat = Point[float]

def find_by_attr(sequence: "Iterable[T]", attr: str, value: object) -> "T | None":
    """Return first item in *sequence* whose attribute *attr* equals *value*."""
    for item in sequence:
        if getattr(item, attr, None) == value:
            return item
    return None


def find_by_id(sequence: "Iterable[T]", id_value: str) -> "T | None":
    """Return first item in *sequence* whose ``id`` equals *id_value*."""
    return find_by_attr(sequence, "id", id_value)


def find_by_label(sequence: "Iterable[T]", label: str) -> "T | None":
    """Return first item in *sequence* whose ``label`` equals *label*."""
    return find_by_attr(sequence, "label", label)


# Hierarchy from outermost to innermost for geometry population
PATH_HIERARCHY = [
    "canvas.dimensions",
    "canvas.effective_dimensions",
    "framing_decision.protection_dimensions",
    "framing_decision.dimensions",
]

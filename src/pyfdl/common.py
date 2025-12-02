from typing import Generic, Any, get_args, Self, List, Union, Iterator, TypeVar

from pydantic import BaseModel, Field, PrivateAttr, RootModel

import pyfdl.config as config


T = TypeVar("T")


FDL_SCHEMA_MAJOR = 2
FDL_SCHEMA_MINOR = 0
FDL_SCHEMA_VERSION = {"major": FDL_SCHEMA_MAJOR, "minor": FDL_SCHEMA_MINOR}


class Dimensions(BaseModel, Generic[T]):
    width: T = Field(ge=0, default=0)
    height: T = Field(ge=0, default=0)
    _dtype: T = PrivateAttr()

    def model_post_init(self, context: Any, /) -> None:
        self._dtype = self.__class__.model_fields["width"].annotation

    def scale_by(self, factor: float) -> None:
        """
        Scale the dimensions by the provider factor

        Args:
            factor:
        """
        self.width *= factor
        self.height *= factor

        if self._dtype is int:
            self.width, self.height = config.get_rounding().round_dimensions(self)

    def duplicate(self) -> Self:
        """
        Create a duplicate of these dimensions

        Returns:
            duplicate: of these dimensions
        """

        dup = Dimensions[self._dtype]()
        dup.width = self.width
        dup.height = self.height
        return dup

    def __iter__(self):
        return iter((self.width, self.height))

    def __lt__(self, other):
        return self.width < other.width or self.height < other.height

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height

    def __gt__(self, other):
        return self.width > other.width or self.height > other.height

    def __bool__(self):
        return bool(self.width) and bool(self.height)


class Point(BaseModel, Generic[T]):
    x: T = Field(ge=0, default=0)
    y: T = Field(ge=0, default=0)


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
        if not isinstance(item, self._cls):
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

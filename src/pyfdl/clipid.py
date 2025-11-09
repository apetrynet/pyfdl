from typing import Optional, Union

from pyfdl import Base
from pyfdl.errors import FDLError


class FileSequence(Base):
    def __init__(self, value: str, idx: str, min_: int, max_: str):
        super().__init__()
        self._min = 0
        self._max = 0

        self.attributes = ["value", "idx", "min", "max"]
        self.required = ["value", "idx", "min", "max"]
        self.kwarg_map = {"min": "min_", "max": "max_"}

        self.value = value
        self.idx = idx
        self.min = min_
        self.max = max_

    @property
    def min(self) -> int:
        return self._min

    @min.setter
    def min(self, value: int):
        if value < 0:
            raise FDLError("Sequences do not allow negative values")

        self._min = value

    @property
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, value: int):
        if value < 0:
            raise FDLError("Sequences do not allow negative values")

        self._max = value

    def __repr__(self):
        return self.to_dict()


class ClipID(Base):
    def __init__(self, clip_name: str, *, file: Optional[str] = None, sequence: Optional[FileSequence] = None):
        super().__init__()
        self._file = None
        self._sequence = None

        self.attributes = ["clip_name", "file", "sequence"]
        self.object_map = {"sequence": FileSequence}
        self.required = ["clip_name"]

        self.clip_name = clip_name
        self.file = file
        self.sequence = sequence

    @property
    def file(self) -> Union[str, None]:
        return self._file

    @file.setter
    def file(self, file: Union[str, None]):
        if file is not None and self.sequence is not None:
            raise FDLError("A sequence is already provided. You may only have file OR sequence as an identifier")

        self._file = file

    @property
    def sequence(self) -> Union[FileSequence, None]:
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: Union[FileSequence, None]):
        if sequence is not None and self.file is not None:
            raise FDLError("A file is already provided. You may only have file OR sequence as an identifier")

        self._sequence = sequence

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f'clip_name="{self.clip_name}"'
            f', file="{self.file}"' if self._file is not None else ""
            f', sequence={self.sequence}' if self.sequence is not None else ""
            f")"
        )

from typing import Annotated, Union

from pydantic import BaseModel, Field, field_validator, model_serializer


class FileSequence(BaseModel):
    value: str
    idx: Annotated[str, Field(max_length=1)]
    min_: Annotated[int, Field(alias="min")]
    max_: Annotated[int, Field(alias="max")]


class ClipID(BaseModel):
    clip_name: str
    file: Union[str, None] = None
    sequence: Union[FileSequence, None] = None

    @field_validator("file", mode="after")
    @classmethod
    def check_for_sequence(cls, value, info):
        if info.data.get("sequence") is not None:
            raise ValueError(
                "A sequence is already provided. You may only have file OR sequence as an identifier"
            )

        return value

    @field_validator("sequence", mode="after")
    @classmethod
    def check_for_file(cls, value, info):
        if info.data.get("file") is not None:
            raise ValueError(
                "A file is already provided. You may only have file OR sequence as an identifier"
            )

        return value

    @model_serializer
    def _validate(self) -> dict:
        result = {
            "clip_name": self.clip_name
        }
        if self.file is not None:
            result["file"] = self.file

        if self.sequence is not None:
            result["sequence"] = self.sequence.model_dump()

        if self.file and self.sequence:
            raise ValueError(
                "Both file and sequence attributes are provided, you may only use one"
            )

        return result

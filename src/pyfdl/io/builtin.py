import json
from typing import IO, Union

from pyfdl import FDL


def load(fp: IO, validate: bool = True) -> FDL:
    """
    Load an FDL from a file.

    Args:
        fp: file pointer
        validate: validate incoming json with jsonschema

    Raises:
        jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec

    Returns:
        FDL:
    """

    raw = fp.read()
    return loads(raw, validate=validate)


def loads(s: str, validate: bool = True) -> FDL:
    """Load an FDL from string.

    Args:
        s: string representation of an FDL
        validate: validate incoming json with jsonschema

    Returns:
        FDL:

    """
    fdl = FDL.from_dict(json.loads(s))

    if validate:
        fdl.validate()

    return fdl


def dump(obj: FDL, fp: IO, validate: bool = True, indent: Union[int, None] = 2):
    """Dump an FDL to a file.

    Args:
        obj: object to serialize
        fp: file pointer
        validate: validate outgoing json with jsonschema
        indent: amount of spaces
    """
    fp.write(dumps(obj, validate=validate, indent=indent))


def dumps(obj: FDL, validate: bool = True, indent: Union[int, None] = 2) -> str:
    """Dump an FDL to string

    Args:
        obj: object to serialize
        validate: validate outgoing json with jsonschema
        indent: amount of spaces

    Returns:
        string: representation of the resulting json
    """
    if validate:
        obj.validate()

    return json.dumps(obj.to_dict(), indent=indent, sort_keys=False)

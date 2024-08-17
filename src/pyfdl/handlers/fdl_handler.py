import json
from pathlib import Path
from typing import IO, Union

from pyfdl import FDL


class FDLHandler:
    def __init__(self):
        """
        The default built-in FDL handler. Takes care of reading and writing FDL files
        """
        self.name = 'fdl'
        self.suffixes = ['.fdl']

    def read_from_file(self, path: Path, validate: bool = True) -> FDL:
        """
        Read an FDL from a file.

        Args:
            path: to fdl file
            validate: validate incoming json with jsonschema

        Raises:
            jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec

        Returns:
            FDL:
        """

        with path.open('r') as fp:
            raw = fp.read()
            return self.read_from_string(raw, validate=validate)

    def read_from_string(self, s: str, validate: bool = True) -> FDL:
        """Read an FDL from a string.

        Args:
            s: string representation of an FDL
            validate: validate incoming json with jsonschema

        Raises:
            jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec

        Returns:
            FDL:

        """
        fdl = FDL.from_dict(json.loads(s))

        if validate:
            fdl.validate()

        return fdl

    def write_to_file(self, fdl: FDL,  path: Path, validate: bool = True, indent: Union[int, None] = 2):
        """Dump an FDL to a file.

        Args:
            fdl: object to serialize
            path: path to store fdl file
            validate: validate outgoing json with jsonschema
            indent: amount of spaces

        Raises:
            jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec
        """
        with path.open('w') as fp:
            fp.write(self.write_to_string(fdl, validate=validate, indent=indent))

    def write_to_string(self, fdl: FDL, validate: bool = True, indent: Union[int, None] = 2) -> str:
        """Dump an FDL to string

        Args:
            fdl: object to serialize
            validate: validate outgoing json with jsonschema
            indent: amount of spaces

        Raises:
            jsonschema.exceptions.ValidationError: if the contents doesn't follow the spec

        Returns:
            string: representation of the resulting json
        """
        if validate:
            fdl.validate()

        return json.dumps(fdl.to_dict(), indent=indent, sort_keys=False)

    def load(self, fp: IO, validate: bool = True) -> FDL:
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
        return self.loads(raw, validate=validate)

    def loads(self, s: str, validate: bool = True) -> FDL:
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

    def dump(self, obj: FDL, fp: IO, validate: bool = True, indent: Union[int, None] = 2):
        """Dump an FDL to a file.

        Args:
            obj: object to serialize
            fp: file pointer
            validate: validate outgoing json with jsonschema
            indent: amount of spaces
        """
        fp.write(self.dumps(obj, validate=validate, indent=indent))

    def dumps(self, obj: FDL, validate: bool = True, indent: Union[int, None] = 2) -> str:
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


def register_plugin(registry: 'PluginReistry'):
    """
    Mandatory function to register handler in the registry. Called by the PluginRegistry itself.

    Args:
        registry: The PluginRegistry passes itself to this function
    """
    registry.add_handler(FDLHandler())

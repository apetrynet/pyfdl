from pathlib import Path
from typing import Optional, Any, Union

from pyfdl.errors import UnsupportedHandlerError
from pyfdl import plugins


def get_handler(direction: str, func_name: str, path: Path = None, handler_name: str = None) -> Any:
    """
    Convenience function to get a matching handler matching the provided arguments.

    Args:
        direction: of handler, "input" or "output"
        func_name: desired function name in handler
        path: to file. Used to get handler based on suffix
        handler_name: ask for a specific handler by name

    Returns:

    """

    _manifest = plugins.get_registry()
    handler = None
    if handler_name is not None:
        handler = _manifest.get_handler_by_name(handler_name, direction=direction, func_name=func_name)
        if handler is None:
            raise AttributeError(
                f'No handler by name: "{handler_name}" registered. '
                f'Please consider using one of the following: {sorted(_manifest.handlers["inputs"])}'
            )

    elif path is not None:
        handler = _manifest.get_handler_by_suffix(path.suffix, direction=direction, func_name=func_name)
        if handler is None:
            raise AttributeError(f'No handler supporting suffix: "{path.suffix}" registered.')

    if handler is None:
        raise UnsupportedHandlerError(
            f'Unable to find an {direction} handler by name: "{handler_name}" or '
            f'suitable handler for suffix: "{path.suffix}"'
        )

    return handler


def read_from_file(path: Union[Path, str], handler_name: str = None, **handler_kwargs: Optional[Any]) -> 'FDL':
    """
    Handler agnostic function for producing an FDL from a file. A suitable handler will be
    chosen based on `path` or `handler_name`.

    Args:
        path: to the file in question
        handler_name: name of handler to use
        **handler_kwargs: arguments passed to handler

    Returns:
        FDL:
    """
    handler = get_handler(
        direction="input",
        func_name='read_from_file',
        path=path,
        handler_name=handler_name
    )

    return handler.read_from_file(Path(path), **handler_kwargs)


def read_from_string(s: str, handler_name: str = 'fdl', **handler_kwargs: Optional[Any]) -> 'FDL':
    """
    Handler agnostic function for producing an FDL based on a string. A suitable handler will be
    chosen based on `handler_name`. Defaults to "fdl".

    Args:
        s: string to convert into an FDL
        handler_name: name of handler to use
        **handler_kwargs: arguments passed to handler

    Returns:
        FDL:
    """
    handler = get_handler(
        direction="input",
        func_name='read_from_string',
        handler_name=handler_name
    )
    return handler.read_from_string(s, **handler_kwargs)


def write_to_file(fdl: 'FDL', path: Union[Path, str], handler_name: str = 'fdl', **handler_kwargs: Optional[Any]):
    """
    Handler agnostic function to write a file based on an FDL. A suitable handler will be chosen based
    on `path` or `handler_name`

    Args:
        fdl: to write
        path: to file
        handler_name: name of handler to use
        **handler_kwargs: arguments passed to handler
    """
    handler = get_handler(
        direction="output",
        func_name='write_to_file',
        path=path,
        handler_name=handler_name
    )
    handler.write_to_file(fdl, Path(path), **handler_kwargs)


def write_to_string(fdl: 'FDL', handler_name: str = 'fdl', **handler_kwargs: Optional[Any]):
    """
    Handler agnostic function for producing a string representation of an FDL. A suitable handler will
    be chosen based on `handler_name`.

    Args:
        fdl: to write
        handler_name: name of hanlder to use
        **handler_kwargs: arguments passed to handler

    Returns:

    """
    handler = get_handler(
        direction="output",
        func_name='write_to_string',
        handler_name=handler_name
    )
    return handler.write_to_string(fdl, **handler_kwargs)

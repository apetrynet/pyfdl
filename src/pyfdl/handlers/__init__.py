from pathlib import Path
from typing import Optional, Any, Union

from pyfdl.plugins import get_registry


def get_handler(func_name: str, path: Union[Path, str] = None, handler_name: str = None) -> Any:
    """
    Convenience function to get a handler matching the provided arguments.

    Args:
        func_name: desired function name in handler
        path: to file. Used to get handler based on suffix
        handler_name: ask for a specific handler by name

    Returns:
        handler:
    """

    if handler_name is None and path is None:
        raise RuntimeError(f'"handler_name" and "path" can\'t both be None. Please provide one or the other')

    _registry = get_registry()
    if handler_name is not None:
        handler = _registry.get_handler_by_name(handler_name, func_name=func_name)

    else:
        path = Path(path)
        handler = _registry.get_handler_by_suffix(path.suffix, func_name=func_name)

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
    path = Path(path)
    handler = get_handler(func_name='read_from_file', path=path, handler_name=handler_name)

    return handler.read_from_file(path, **handler_kwargs)


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
    handler = get_handler(func_name='read_from_string', handler_name=handler_name)
    return handler.read_from_string(s, **handler_kwargs)


def write_to_file(fdl: 'FDL', path: Union[Path, str], handler_name: str = None, **handler_kwargs: Optional[Any]):
    """
    Handler agnostic function to write a file based on an FDL. A suitable handler will be chosen based
    on `path` or `handler_name`

    Args:
        fdl: to write
        path: to file
        handler_name: name of handler to use
        **handler_kwargs: arguments passed to handler
    """
    path = Path(path)
    handler = get_handler(func_name='write_to_file', path=path, handler_name=handler_name)
    handler.write_to_file(fdl, path, **handler_kwargs)


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
    handler = get_handler(func_name='write_to_string', handler_name=handler_name)
    return handler.write_to_string(fdl, **handler_kwargs)

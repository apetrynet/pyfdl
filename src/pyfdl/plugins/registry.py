import sys
from importlib import import_module, resources
from importlib.metadata import entry_points
from typing import Any, Union

from pyfdl.errors import UnknownHandlerError

_REGISTRY = None


class PluginRegistry:
    def __init__(self):
        """
        The `PluginRegistry` loads and registers all plugins and built in handlers.
        """

        self.handlers = {}
        self.load_builtin()
        self.load_plugins()

    def load_builtin(self):
        """
        Load the built-in handlers
        """
        anchor = "pyfdl.handlers"
        for module in resources.files(anchor).iterdir():
            if module.name.startswith("_") or module.suffix != ".py":
                continue
            module_name = module.stem
            mod = import_module(f"{anchor}.{module_name}")
            if hasattr(mod, "register_plugin"):
                mod.register_plugin(self)

    def load_plugins(self):
        """
        Load plugins from the "pyfdl.plugins" namespace.
        """
        try:
            plugin_packages = entry_points(group="pyfdl.plugins")
        except TypeError:
            # Python < 3.10
            plugin_packages = entry_points().get("pyfdl.plugins", [])

        for plugin in plugin_packages:
            try:
                if plugin.attr is not None:
                    register_func = plugin.load()
                else:
                    mod = plugin.load()
                    register_func = getattr(mod, "register_plugin", None)

                if register_func is None:
                    print(
                        f'Unable to find a registration function in plugin: "{plugin.name}". '
                        f"Please consult documentation on plugins to solve this.",
                        file=sys.stderr,
                    )

                register_func(self)

            except (ModuleNotFoundError, TypeError) as err:
                print(f'Unable to load plugin: "{plugin.name}" due to: "{err}"', file=sys.stderr)

    def add_handler(self, handler: Any):
        """
        Add a handler to the collection of handlers
        Args:
            handler: plugin or built-in handler to add
        """
        self.handlers.setdefault(handler.name, handler)

    def get_handler_by_name(self, handler_name: str, func_name: str) -> Union["Handler", None]:
        """
        Get a registered handler by `handler_name`, and
        make sure it has a function (`func_name`) to call

        Args:
            handler_name: name handler to look for
            func_name: name of function in handler to call

        Returns:
            handler:

        Raises:
            error: if no handler by name and function is registered
        """
        handler = self.handlers.get(handler_name)
        if hasattr(handler, func_name):
            return handler

        raise UnknownHandlerError(
            f'No handler by name: "{handler_name}" with function: "{func_name}" seems to be registered. '
            f"Please check that a plugin containing this handler is properly installed"
            f"or use one of the following registered handlers: {sorted(self.handlers.keys())}"
        )

    def get_handler_by_suffix(self, suffix: str, func_name: str) -> Union["Handler", None]:
        """
        Get a registered handler by `suffix`, and
        make sure it has a function (`func_name`) to call


        Args:
            suffix: including the dot (".fdl")
            func_name: name of function in handler to call

        Returns:
            handler:

        Raises:
            error:
        """
        for handler in self.handlers.values():
            if not hasattr(handler, "suffixes"):
                continue

            if suffix in handler.suffixes and hasattr(handler, func_name):
                return handler

        raise UnknownHandlerError(
            f'No handler supporting suffix: "{suffix}" and function: "{func_name}" seems to be registered. '
            f"Please check that a plugin supporting this suffix is properly installed"
            f"or use one of the following registered handlers: {sorted(self.handlers.keys())}"
        )


def get_registry(reload: bool = False) -> PluginRegistry:
    """
    Get the active registry containing plugins and built-in handlers

    Returns:
        registry:
    """
    global _REGISTRY
    if _REGISTRY is None or reload:
        _REGISTRY = PluginRegistry()

    return _REGISTRY

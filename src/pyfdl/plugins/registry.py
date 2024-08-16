from importlib import import_module, resources
from importlib.metadata import entry_points
from typing import Union, Any

_REGISTRY = None


class PluginRegistry:
    def __init__(self):
        """
        The `PluginRegistry` loads and registers all plugins and built in handlers.
        """

        self.handlers = {
            "input": {},
            "output": {}
        }
        self.load_builtin()
        self.load_plugins()

    def load_builtin(self):
        """
        Load the built-in handlers
        """
        anchor = 'pyfdl.handlers'
        for module in resources.files(anchor).iterdir():
            if module.name.startswith('_') or module.suffix != '.py':
                continue
            module_name = module.stem
            mod = import_module(f'{anchor}.{module_name}')
            if hasattr(mod, 'register_plugin'):
                mod.register_plugin(self)

    def load_plugins(self):
        """
        Load plugins from the "pyfdl.plugins" namespace.
        """
        plugin_packages = entry_points(group='pyfdl.plugins')
        for plugin in plugin_packages:
            if plugin.attr is not None:
                mod = plugin.load()
                register_func = getattr(mod, 'register_plugin', None)
            else:
                register_func = plugin.load()

            if register_func is not None:
                register_func(self)

    def add_handler(self, handler: Any):
        """
        Add a handler to the collection of handlers
        Args:
            handler: plugin or built-in handler to add
        """
        for direction in handler.directions:
            self.handlers[direction].setdefault(handler.name, handler)

    def get_handler_by_name(self, handler_name: str, direction: str, func_name: str) -> Union['Handler', None]:
        """
        Get a registered handler by `handler_name`, `direction` and
        make sure it has a function (`func_name`) to call

        Args:
            handler_name: name handler to look for
            direction: to send data ("input" or "output")
            func_name: name of function in handler to call

        Returns:
            handler:
        """
        handler = self.handlers.get(direction, {}).get(handler_name)
        if hasattr(handler, func_name):
            return handler

    def get_handler_by_suffix(self, suffix: str, direction: str, func_name: str) -> Union['Handler', None]:
        """
        Get a registered handler by `suffix`, `direction` and
        make sure it has a function (`func_name`) to call


        Args:
            suffix: including the dot (".fdl")
            direction: to send data ("input" or "output")
            func_name: name of function in handler to call

        Returns:
            handler:
        """
        for handler in self.handlers.get(direction, {}).values():
            if suffix in handler.suffixes and hasattr(handler, func_name):
                return handler


def get_registry() -> PluginRegistry:
    """
    Get the active registry containing plugins and built-in handlers

    Returns:
        registry:
    """
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = PluginRegistry()

    return _REGISTRY

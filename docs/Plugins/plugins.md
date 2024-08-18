# Plugins

PyFDL supports plugins for expanding the toolkit.  
This may be useful to add support for converting frame line definitions in another formats to FDL or 
reading metadata from files to mention a few examples.

## Plugin types

### Handlers
Plugins that take care of reading/writing files to and/or from FDL are called `handlers`. 
PyFDL comes with a built-in [`FDLHandler`](../Handlers/handlers.md#fdlhandler) which takes care of reading and writing 
FDL files.

## Writing a handler plugin
There are only a couple of requirements for a handler.  
1. The handler needs to be a class with a `name` variable. If your handler deals with files you should 
 provide a `suffixes` variable containing a list of suffixes to support. Suffixes include the dot like. ".yml" 
2. The module needs to provide a function, example: `register_plugin(registry)` which accepts one argument for 
 the registry. This function will call `registry.add_handler(<HANDLER_INSTANCE>)` with an instance of your 
 handler.

Example of a YAML Handler:
```python
import yaml
from pathlib import Path
from typing import Optional, Any
from pyfdl import FDL

class YAMLHandler:
    def __init__(self):
        # Name is required
        self.name = 'yaml'
        # Suffixes may be used to automagically select this handler based on path
        self.suffixes = [".yml", ".yaml"]

    def write_to_string(self, fdl: FDL, validate: bool = True, **yaml_args: Optional[Any]) -> str:
        if validate:
            fdl.validate()
        
        return yaml.dump(fdl.to_dict(), **yaml_args)

    def write_to_file(self, fdl: FDL, path: Path, validate: bool = True, **yaml_args: Optional[Any]) -> str:
        if validate:
            fdl.validate()
        print('yoho')
        with path.open('w') as f:
            f.write(yaml.dump(fdl.to_dict(), **yaml_args))

    def custom_method(self, fdl: FDL, brand: str) -> FDL:
        fdl.fdl_creator = brand
        return fdl
            
    
def register_plugin(registry: 'PluginRegistry'):
    registry.add_handler(YAMLHandler())
``` 

## Installing a plugin
### Install via pip
Ideally you package your plugin according to best practices and share it via PyPi for other to use.
However, the only requirement from PyFDL's perspective is that you install the plugin to PyFDL's 
plugin namespace: `pyfdl.plugins`.

In your pyproject.toml or setup.py make sure to add your package/module like so:
``` toml

[project.entry-points."pyfdl.plugins"]
# If you choose to call your register function something else, make sure to adjust the entry below.
yaml_handler = "yaml_handler:register_plugin"
```

You are free to name your register function whatever you like, but make sure you add it after the module name
If you don't provide a function name PyFDL will assume the function is named `register_plugin` and will
ignore your plugin if that is not the case.

### Install at runtime
You may also add your handler directly in your code.
To do this, simply get a hold of the registry and add your handler.

```python
from pyfdl.plugins import get_registry

registry = get_registry()
registry.add_handler(YAMLHandler())
```

## Using your handler
If your handler provides one or more of the following methods: `read_from_file` `read_from_string`, 
`write_to_file` or `write_to_string`, PyFDL will choose your handler based on either path (suffix) or 
directly asking for this specific handler.

```python
import pyfdl
from pathlib import Path
from tempfile import NamedTemporaryFile

fdl = pyfdl.FDL()
fdl.apply_defaults()
pyfdl.write_to_string(fdl, handler_name='yaml', indent=4)
pyfdl.write_to_file(fdl, path=NamedTemporaryFile(suffix='.yml', delete=False).name)
```
If your handler doesn't provide one of the methods above or you have others exposed you can use them like so:
```python
from pyfdl.handlers import get_handler

my_handler = get_handler(func_name='custom_method', handler_name='yaml')
fdl = FDL()
fdl.apply_defaults()
assert fdl.fdl_creator == 'PyFDL'
my_handler.custom_method(fdl, "my brand")
assert fdl.fdl_creator == 'my brand'

```

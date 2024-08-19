# Handlers
PyFDL provides a set of functions to read and write files. These functions will pick the appropriate handler based
on path.suffix or handler name. 

----

::: pyfdl.read_from_file

::: pyfdl.read_from_string

::: pyfdl.write_to_file

::: pyfdl.write_to_string

## FDLHandler
This is the built-in handler for reading and writing fdl files. No need to call this directly. Use the functions above.

::: pyfdl.handlers.fdl_handler

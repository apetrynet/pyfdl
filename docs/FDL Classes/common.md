# Common

## Global Variables
Version numbers are used as default values in [Header](header.md) and to select a matching json schema file
if no version is set.

::: pyfdl.FDL_SCHEMA_MAJOR
::: pyfdl.FDL_SCHEMA_MINOR
::: pyfdl.FDL_SCHEMA_VERSION
---

Different workflows have different requirements for precision, so we are flexible in how to apply 
rounding of values

::: pyfdl.DEFAULT_ROUNDING_STRATEGY
This is the default behavior for rounding the values of dimensions. The rules are the same as for
`CanvasTemplate.round`.

::: pyfdl.NO_ROUNDING
This will disable rounding of values in dimensions. Exception being `Canvas.dimensions` when
created by a canvas templates

::: pyfdl.set_rounding_strategy

::: pyfdl.rounding_strategy


## Base Classes

Below is a collection of the common classes that are used by other classes.

::: pyfdl.Base
    options:
        inherited_members: false

::: pyfdl.TypedCollection
    options:
        inherited_members: false

::: pyfdl.Dimensions
    options:
        inherited_members: false

::: pyfdl.Point
    options:
        inherited_members: false

::: pyfdl.RoundStrategy
    options:
        inherited_members: false

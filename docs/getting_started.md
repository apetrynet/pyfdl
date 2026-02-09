# Getting Started

## About rounding
As different parts of a pipeline requires different levels of precision we have an option to 
round values of dimensions accordingly.  
A canvas+framing decision for a "raw" camera canvas should in theory keep more precision than a 
canvas+framing decision for a conformed VFX plate. 

The rules for rounding strategy are the same as for [CanvasTemplate.round](FDL Classes/common.md#fdl.RoundStrategy)


The [default](FDL Classes/common.md#fdl.DEFAULT_ROUNDING_STRATEGY) strategy is to not apply rounding and keep float values where applicable, but this may be 
overridden by setting the rounding strategy via the 
[`set_rounding_strategy()`](FDL Classes/common.md#fdl.set_rounding_strategy) function

> **NOTE!** The rounding strategy is set globally for where rounding applies except for `CanvasTemplate.round` 
> which follows its own rules.

### Setting the global rounding strategy
Here are a some examples of how to set the rounding strategy:

```python
import fdl.config
import fdl.rounding
import fdl

# No rounding (default behavior) is set by passing the NO_ROUNDING variable
fdl.config.set_rounding(fdl.config.NO_ROUNDING)

# For other requirements pass a RoundStrategy instance with the desired rules
fdl.config.set_rounding(fdl.rounding.RoundStrategy(even="whole", mode="up"))
```

## Usage Examples
### Create an FDL from scratch

```python
import fdl
from fdl import Canvas, FramingIntent, Dimensions, Point
from tempfile import NamedTemporaryFile

# A clean FDL instance populates the header with a valid staring point 
fdl = fdl.FDL()

# Let's create a framing intent
framing_intent = FramingIntent(
    label="1.78-1 Framing",
    id="FDLSMP03",
    aspect_ratio=Dimensions(width=16, height=9),
    protection=0.088
)

# Add the newly created framing intent to our FDL
fdl.framing_intents.append(framing_intent)

# Now let's create a canvas
canvas = Canvas(
    label="Open Gate RAW",
    id="20220310",
    source_canvas_id="20220310",
    dimensions=Dimensions(width=5184, height=4320),
    effective_dimensions=Dimensions(width=5184, height=4320),
    effective_anchor_point=Point(x=0, y=0),
    photosite_dimensions=Dimensions(width=5184, height=4320),
    physical_dimensions=Dimensions(width=25.92, height=21.60),
    anamorphic_squeeze=1.30
)

# Let's now add our canvas to the FDL within a context.
# If no such context exists, one will be created for you.
fdl.place_canvas_in_context(context_label="PanavisionDXL2", canvas=canvas)

# Finally, let's create a framing decision
canvas.place_framing_intent(framing_intent=framing_intent)

# Validate our FDL and save it
with NamedTemporaryFile(suffix='.fdl', delete=False) as f:
    fdl.write_to_file(fdl, f.name, validate=True)
```

### Apply a Canvas Template
```python
import fdl
from pathlib import Path
from tempfile import NamedTemporaryFile

fdl_file = Path('tests/sample_data/Scenario-9__OriginalFDL_UsedToMakePlate.fdl')
my_fdl = fdl.read_from_file(fdl_file)

# Select the first canvas in the first context
context = my_fdl.contexts[0]
source_canvas = context.canvases[0]
source_framing = source_canvas.framing_decisions[0]

# Select the first canvas template
canvas_template = my_fdl.canvas_templates[0]

# Apply the template to produce a new FDL with the transformed canvas
result = fdl.apply_fdl_template(
    source_canvas=source_canvas,
    source_framing=source_framing,
    template=canvas_template,
    new_fd_name="",
    source_context=context,
)

# result.fdl contains the new FDL, result.canvas the new canvas, etc.
with NamedTemporaryFile(suffix='.fdl', delete=False) as f:
    fdl.write_to_file(result.fdl, f.name, validate=True)
```

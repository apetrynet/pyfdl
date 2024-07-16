# Getting Started

## Install
> **NOTE!** Please note that at the time of writing this PyFDL is not released on PyPi. 
> Please refer to README.md for instructions. 
```
pip install pyfdl
```

## About rounding
As different parts of a pipeline requires different levels of precision we have an option to 
round values of dimensions accordingly.  
A canvas+framing decision for a "raw" camera canvas should in theory keep more precision than a 
canvas+framing decision for a conformed VFX plate. 

The rules for rounding strategy are the same as for [CanvasTemplate.round](Classes/common.md#pyfdl.RoundStrategy)


The [default](Classes/common.md#pyfdl.DEFAULT_ROUNDING_STRATEGY) strategy is to round dimensions to 
even numbers, but this may be overridden by setting the rounding strategy to 
[`NO_ROUNDING`](Classes/common.md#pyfdl.NO_ROUNDING)

Here are a couple examples of setting the rounding strategy:
```python
import pyfdl

fdl = pyfdl.FDL()

# No rounding may either be set by passing the NO_ROUNDING variable
fdl.set_rounding_strategy(pyfdl.NO_ROUNDING)

# Or by explicitly passing None
fdl.set_rounding_strategy(None)

# For other requirements pass a dictionary with the rules
fdl.set_rounding_strategy({'even': 'whole', 'mode': 'up'})
```

## Examples
### Create an FDL from scratch

```python
import pyfdl
from pyfdl import Canvas, FramingIntent, Dimensions, Point
from io import StringIO

fdl = pyfdl.FDL()

# Applying defaults will provide you with a valid staring point 
fdl.apply_defaults()

# Let's create a framing intent
framing_intent = FramingIntent(
    label="1.78-1 Framing",
    id_="FDLSMP03",
    aspect_ratio=Dimensions(width=16, height=9),
    protection=0.088
)

# Add the newly created framing intent to our FDL
fdl.framing_intents.add(framing_intent)

# Now let's create a canvas
canvas = Canvas(
    label="Open Gate RAW",
    id_="20220310",
    source_canvas_id="20220310",
    dimensions=Dimensions(width=5184, height=4320),
    effective_dimensions=Dimensions(width=5184, height=4320),
    effective_anchor_point=Point(x=0, y=0),
    photosite_dimensions=Dimensions(5184, height=4320),
    physical_dimensions=Dimensions(width=25.92, height=21.60),
    anamorphic_squeeze=1.30
)

# Let's now add our canvas to the FDL within a context.
# If no such context exists, one will be created for you.
fdl.place_canvas_in_context(context_label="PanavisionDXL2", canvas=canvas)

# Finally, let's create a framing decision
canvas.place_framing_intent(framing_intent=framing_intent)

# Validate our FDL and save it (using StringIO as example)
with StringIO() as f:
    pyfdl.dump(fdl, f, validate=True)
```

### Create a Canvas from a Canvas Template
```python
import pyfdl
from io import StringIO
from pathlib import Path

fdl_file = Path('tests/sample_data/Scenario-9__OriginalFDL_UsedToMakePlate.fdl')
with fdl_file.open('r') as f:
    fdl = pyfdl.load(f)

# Select the first canvas in the first context
context = fdl.contexts[0]
source_canvas = context.canvases[0]

# Select the first canvas template
canvas_template = fdl.canvas_templates[0]

# We know we want to use the first framing decision of the source canvas, so we pass index 0
# You may also pass the actual `FramingDecision` source_canvas.framing_decisions[0]
new_canvas = pyfdl.Canvas.from_canvas_template(
    canvas_template=canvas_template,
    source_canvas=source_canvas,
    source_framing_decision=0
)

# Place the new canvas along side the source 
fdl.place_canvas_in_context(context_label=context.label, canvas=new_canvas)

# Validate and "save"
with StringIO() as f:
    pyfdl.dump(fdl, f, validate=True)
```

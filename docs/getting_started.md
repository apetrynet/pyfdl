# Getting Started

## Install
> **NOTE!** Please note that at the time of writing this PyFDL is not released on PyPi. 
> Please refer to README.md for instructions. 
```
pip install pyfdl
```

## Create an FDL from scratch

```python
from io import StringIO
from pyfdl import FDL, Canvas, FramingIntent, DimensionsInt, DimensionsFloat, Point

fdl = FDL()

# Applying defaults will provide you with a valid staring point 
fdl.apply_defaults()

# Let's create a framing intent
framing_intent = FramingIntent(
    label="1.78-1 Framing",
    _id="FDLSMP03",
    aspect_ratio=DimensionsInt(width=16, height=9),
    protection=0.088
)

# Add the newly created framing intent to our FDL
fdl.framing_intents.add_item(framing_intent)

# Now let's create a canvas
canvas = Canvas(
    label="Open Gate RAW",
    _id="20220310",
    source_canvas_id="20220310",
    dimensions=DimensionsInt(width=5184, height=4320),
    effective_dimensions=DimensionsInt(width=5184, height=4320),
    effective_anchor_point=Point(x=0, y=0),
    photosite_dimensions=DimensionsInt(5184, height=4320),
    physical_dimensions=DimensionsFloat(width=25.92, height=21.60),
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

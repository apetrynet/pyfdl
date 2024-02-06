> **Note!**  PyFDL is under development and should not be used in production. 

# PyFDL
PyFDL is a toolkit to parse and produce [FDL](https://theasc.com/society/ascmitc/asc-framing-decision-list) files in python.  
In addition to parsing FDL files, PyFDL aims to provide sample applications/plugins to apply framing intents
described in the FDL.

# Features

| Feature                         | Read | Write | Notes                                                                    |
|:--------------------------------|:----:|:-----:|--------------------------------------------------------------------------|
| FDL files                       |  ✔   |   ✔   |                                                                          |
| Validate id's and relationships |  ✔   |   ✔   | Enforces unique ID's and makes sure relationship between items are valid |
| FDL wizard                      |  ✖   |   ✖   | Commandline tool to produce FDL files                                    |
| Reformat tool                   |  ✖   |   ✖   | Commandline tool based on OpenImageIO                                    |
| FDL as metadata                 |  ✖   |   ✖   | Only files supported by OpenImageIO                                      |
| GUI for reformat tool           |  ✖   |   ✖   | Visualize framing intents                                                |
| Nuke plugin                     |  ✖   |   ✖   |                                                                          |

✔ Implemented  
✖ Not implemented  
N/A Not applicable  

# Usage
```python
import pyfdl
from pathlib import Path

# Read from file
fdl_path = Path('/path/to/fdl/file.fdl')
with fdl_path.open('r') as fp:
    fdl = pyfdl.load(fp)

# Write to file
fdl_path = Path('/path/to/fdl/myfile.fdl')
with fdl_path.open('w') as fp:
    pyfdl.dump(fdl, fp)
```

# Documentation
You can build the documentation by installing and running `mkdocs build` in the 
root directory. A "site" folder should appear with an `index.html` file.  
The documentation is primarily based on docstrings at the moment. 
More examples and use cases will be added as the project evolves.

# Schema Files
PyFDL ships with JSON schema definition files kindly provided by [ASC MITC](https://github.com/ascmitc/fdl).  
The schema files are used to validate the incoming and outgoing FDL files.

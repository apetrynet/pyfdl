# Welcome to PyFDL
> **Warning!**  PyFDL is still under development and parts of the API may still change.
> Please consider this before using it production. 

PyFDL is a toolkit to parse and produce [Framing Decision List (FDL)](https://theasc.com/society/ascmitc/asc-framing-decision-list) files in python.  
In addition to parsing FDL files, PyFDL aims to provide an expandable command line tool and a set of plugins
to scratch that FDL itch.

PyFDL is modeled around the official FDL [spec](https://github.com/ascmitc/fdl/tree/main/Specification).

# Install
> **Note!** Until a package is available on PyPi, you'll need to install PyFDL manually.

It's recommended to install packages like this in a virtual environment.
```shell
pip install pyfdl
```

# Features

| Feature                         | Read | Write | Notes                                                                    |
|:--------------------------------|:----:|:-----:|--------------------------------------------------------------------------|
| FDL files                       |  ✔   |   ✔   |                                                                          |
| Validate ID's and relationships |  ✔   |   ✔   | Enforces unique ID's and makes sure relationship between items are valid |
| Expandable through plugins      |  ✔   |   ✔   |                                                                          |
| Verify FDL with JSON Schema     |  ✔   |   ✔   |                                                                          |
| Commandline tool                |  ✖   |   ✖   |                                                                          |

✔ Implemented  
✖ Not implemented  
N/A Not applicable  

# Welcome to PyFDL
> **NOTE!** PyFDL is under development and should not be used in production 

PyFDL is a toolkit to parse and produce [Framing Decision List (FDL)](https://theasc.com/society/ascmitc/asc-framing-decision-list) files in python.  
In addition to parsing FDL files, PyFDL aims to provide sample applications/plugins to apply framing intents
described in the FDL.

PyFDL is modeled around the official [spec](https://github.com/ascmitc/fdl/blob/main/Specification/ASCFDL_Specification_v1.0.pdf).

# Install
Until a package is available on PyPi, you'll need to install PyFDL manually.
It's recommended to install packages like this in a virtual environment.

## When you just want to use PyFDL
```shell
# Replace PROJECT_ROOT with the root of this project
cd [PROJECT_ROOT] 
pip install .
```

## When working on a contribution
If you're working a contribution to this package you can save some time
by installing the package like described below. This way you won't need to reinstall
the package for every change you do to the code.
```shell
# Replace PROJECT_ROOT with the root of this project
cd [PROJECT_ROOT] 
pip install -e .
```

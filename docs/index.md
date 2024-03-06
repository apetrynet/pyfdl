# Welcome to PyFDL
> **NOTE!** PyFDL is under development and should not be used in production 

PyFDL is a toolkit to parse and produce [Framing Decision List (FDL)](https://theasc.com/society/ascmitc/asc-framing-decision-list) files in python.  
In addition to parsing FDL files, PyFDL aims to provide sample applications/plugins to apply framing intents
described in the FDL.

PyFDL is modeled around the official [spec](https://github.com/ascmitc/fdl/tree/main/Specification).

# Install
Until a package is available on PyPi, you'll need to install PyFDL manually.
It's recommended to install packages like this in a virtual environment.

## Installing from PyPi
```shell
pip install pyfdl
```

## Installing directly from main branch on GitHub (At your own risk)
```shell
pip install git+https://github.com/apetrynet/pyfdl.git
```

## When working on a contribution
If you're working a contribution to this project you can save some time
by installing the package like described below. This way you won't need to reinstall
the package for every change you do to the code.
```shell
# Replace PROJECT_ROOT with the root of this project
cd [PROJECT_ROOT] 
pip install -e .
```

[![Tests](https://github.com/apetrynet/pyfdl/actions/workflows/test_pyfdl.yml/badge.svg)](https://github.com/apetrynet/pyfdl/actions/workflows/test_pyfdl.yml)
[![Deploy Docs](https://github.com/apetrynet/pyfdl/actions/workflows/deploy_docs.yml/badge.svg)](https://github.com/apetrynet/pyfdl/actions/workflows/deploy_docs.yml)

> **Warning!**  PyFDL is still under development and parts of the API may still change.
> Please consider this before using it production. 

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

# Documentation
You'll find the latest published documentation on PyFDL [here](https://apetrynet.github.io/pyfdl/)

# Package Management
PyFDL uses [Hatch](https://hatch.pypa.io) for package management. 
Please refer to their documentation for more info on usage.

There is an environment setup for unit testing.

``` commandline
hatch run test:test
```

To build and serve the documentation locally, you may use one of the following commands.
``` commandline
# Only build the docs. You'll find them in the "site" folder
hatch run docs:build

# Serve the docs on localhost:8000
hatch run docs:serve
```

# Schema Files
PyFDL ships with JSON schema definition files kindly provided by [ASC MITC](https://github.com/ascmitc/fdl).  
The schema files are used to validate the incoming and outgoing FDL files.

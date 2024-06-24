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
You'll find the latest published documentation [here](https://apetrynet.github.io/pyfdl/)

If You'd like a local copy of the documentation you may build it by installing mkdocs and running `mkdocs build` in the
root directory. A "site" folder should appear with an `index.html` file in it.

# Schema Files
PyFDL ships with JSON schema definition files kindly provided by [ASC MITC](https://github.com/ascmitc/fdl).  
The schema files are used to validate the incoming and outgoing FDL files.

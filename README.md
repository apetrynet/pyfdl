[![Tests](https://github.com/apetrynet/pyfdl/actions/workflows/test_pyfdl.yml/badge.svg)](https://github.com/apetrynet/pyfdl/actions/workflows/test_pyfdl.yml)
[![Deploy Docs](https://github.com/apetrynet/pyfdl/actions/workflows/deploy_docs.yml/badge.svg)](https://github.com/apetrynet/pyfdl/actions/workflows/deploy_docs.yml)
![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fapetrynet%2Fpyfdl%2Fmain%2F.github%2Fworkflows%2Ftest_pyfdl.yml&query=%24.jobs%5B%22test_pyfdl%22%5D.strategy.matrix%5B%22python-version%22%5D&label=Python)

> **Warning!**  PyFDL is still under development and parts of the API may still change.
> Please consider this before using it production. 

# PyFDL
PyFDL is a toolkit to parse and produce [Framing Decision List (FDL)](https://theasc.com/society/ascmitc/asc-framing-decision-list) files in python.  
In addition to parsing FDL files, PyFDL aims to provide an expandable command line tool and a set of plugins
to scratch that FDL itch.

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

# Documentation
You'll find the latest published documentation on PyFDL [here](https://apetrynet.github.io/pyfdl/)

# Contributions
Contributions are welcome. Please refer to the [contributing](https://apetrynet.github.io/pyfdl/contributing) page in the docs for more info. 

# Schema Files
PyFDL ships with JSON schema definition files kindly provided by [ASC MITC](https://github.com/ascmitc/fdl).  
The schema files are used to validate the incoming and outgoing FDL files.

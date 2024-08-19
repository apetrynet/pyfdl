# Contributions
Contributions come in many forms, be it reporting bugs, giving feedback or submitting code. It's all welcome 
as our goal is to provide a useful toolkit that suits the needs of its users.

## Response Time
At the time of writing this, PyFDL is developed primarily in my spare time. Please excuse any delays in answering 
questions or reviewing of code. I'll do my best to respond as quickly as I can.

## Package Management
PyFDL uses [Hatch](https://hatch.pypa.io) for package management. 
Please refer to their documentation for more info on usage.

There is an environment setup for unit testing.

```commandline
hatch run test:test
# or
hatch test
```
And a default shell for an interactive python session and so on.
```commandline
hatch shell
```

To build and serve the documentation locally, you may use one of the following commands.
```commandline
# Only build the docs. You'll find them in the "site" folder
hatch run docs:build

# Serve the docs on localhost:8000
hatch run docs:serve
```

## Checklist For Contributions
### Fork the repo
Please fork the repo on GitHub and clone your fork locally.  
`git clone git@github.com:<USERNAME>/pyfdl.git`

### Create a feature branch
Always work in a feature branch. ***Do not submit Pull Requests directly from "main"***  
Name your branch something relatable to the feature you're adding or a bug your fixing. 
Only address one feature/bug in a branch to the best of your judgement.  
`git checkout -b my_feature_branch`  

### Write code
Please try to follow the style of the project when writing code.  
Use type hints and provide docstrings in your code.

### Write unittests
All contributions should provide tests for new/updated behavior. We use [pytest](https://docs.pytest.org/en/stable/), please consult 
their documentation for info on usage.
New sample files may be added to the `tests/sample_data` folder if needed

### Documentation
Please add/update relevant documentation. We use [mkdocs](https://www.mkdocs.org/) and 
[mkdocstrings](https://mkdocstrings.github.io/)
>**NOTE!** All python code blocks will get tested, so make sure to write valid examples.

If you need to split your code blocks in the documentation, but would like to refer to each block, add your
markdown file to the `USE_MEM` list in the `tests/test_docs.py` file

### Submitting a Pull Request
Push your feature branch to your repo and open a Pull Request on GitHub.  
Branches on "apetrynet's" GitHub repo that get merged into "main" are deleted on GitHub to keep a clean repo.   
`git push origin my_feature_branch`

Continue to push to this branch until the Pull Request is merged

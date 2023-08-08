# Installation


## Install the prerequisites

You will need Python (version >= 3.9) and `poetry` (version >= 1.2) installed
on your computer. To install Python, it is recommended to use the `pyenv` tool.
Installation instructions are available [on
Github](https://github.com/pyenv/pyenv#installation).

The `poetry` tool handles dependency management and installation. Installation
instructions are available on [their
documentation](https://python-poetry.org/docs/#installation). 

If you already have `poetry` installed, you can check the version by running
the following from the command line:

```bash
poetry --version
```

If the version is less than 1.2, you can update it by following the
[instructions](https://python-poetry.org/docs/#installation) on their
documentation.


## Install the source code

First, clone the [Github
repository](https://github.com/PhilaController/five-year-plan-analysis):

```bash
git clone https://github.com/PhilaController/five-year-plan-analysis.git
```
and change to the new folder:


```bash
cd five-year-plan-analysis
```

Then use `poetry` to install the dependencies:


```bash
poetry install
```

This will create a new Python environment where all of the code's dependencies
are installed. If this finishes successfully, 

```bash
poetry run fyp-analysis-run --help
```

This should output the help message for the main analysis command.

!!! note

    The command name (`fyp-analysis-run`) must be prefixed with `poetry run`. 
    This ensures that `poetry` will run the command from within the installed 
    environment, so that the necessary dependencies are available when the code runs.

## Set up your API credentials

To download economic indicator data, you will need credentials to connect to
the API services of various sources. These credentials are stored on the FPD
Sharepoint site in the following file:

`Documents/Five Year Plan/Analysis/Indicator API Credentials.docx`

Create a local file in the `conf/local/` folder called `credentials.yml` and
copy the contents of the sharepoint file into this file. This will allow the
data processing pipeline to automatically download the necessary economic
indicators.



## Getting the latest code changes

You can pull in the latest changes from Github using the `git` command:

```bash
git pull origin main
```

If you have any local changes, this command could raise merge conflicts that
you will have to resolve manually. You check for local changes via:

```
git status
```

If you want to save your local changes, but get a clean git status, you can
"stash" them:

```
git stash
```

If you "stash" your changes before running `git pull origin main` you will
avoid any merge conflicts when syncing the code. 



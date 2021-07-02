# Local Development Setup


## Installation

### Step 1: Clone the Github repository

First, clone the [Github repository](https://github.com/PhiladelphiaController/five-year-plan-analysis):

```
git clone https://github.com/PhiladelphiaController/five-year-plan-analysis.git
```
and change to the new folder:

```
cd five-year-plan-analysis
```

### Step 2: Set up a conda environment

Next, we'll create a fresh conda environment called `fyp` for the project:

```
conda create -n fyp -y python=3.8
```

And then we can activate the new environment:

```
conda activate fyp
```

---
**NOTE**

Whenever you are trying to run code from the repository, you must activate the environment first. You can 
tell if the environment is currently activated because the command line should start with `(fyp)`.

---

### Step 3: Install the package and its dependencies


The analysis code is stored in the `src/` folder. With the environment activated, we can 
use the `pip` command to install the relevant dependencies and the package itself:

```
pip install -e src -r src/requirements.txt
```

### Step 4: Verify the installation worked

To verify the installation worked properly, run the 
following:

```
fyp-analysis --help
```

You should see the help message for the command printed to the terminal.


## Getting the Latest Changes

You can pull in the latest changes from Github using the `git` command:

```
git pull origin main
```

If you have any local changes, this command could raise merge conflicts that you will 
have to resolve manually.


## Updating the Installed Dependencies

If the `requirements.txt` file is updated, you can install the latest dependencies using 
the following command:

```
kedro install
```
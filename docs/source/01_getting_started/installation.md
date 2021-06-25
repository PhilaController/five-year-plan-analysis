# Installation

First, clone the [Github repository](https://github.com/PhiladelphiaController/five-year-plan-analysis):

```
git clone https://github.com/PhiladelphiaController/five-year-plan-analysis.git
```
and change to the new folder:

```
cd five-year-plan-analysis
```

Next, we'll create a fresh conda environment called `fyp` for the project:

```
conda create -n fyp python=3.8
```

And then we can activate the new environment:

```
conda activate fyp
```

Now we are ready to install the project's dependencies. First, we need to install the main dependency, [kedro](https://github.com/quantumblacklabs/kedro/).

```
conda install -c conda-forge kedro
```
And then we can use the `kedro` command  to install the rest of the dependencies:

```
kedro install
```

To verify the installation worked properly, run the 
following:

```
fyp-analysis --help
```

You should see the help message for the command printed to the terminal.
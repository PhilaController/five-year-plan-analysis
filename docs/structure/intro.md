# Overview

The analysis code is subdivided into four steps: 

1. **Data Processing**: a pipeline that prepares the relevant data indicators
   to be input into the modeling regressions.
1. **Forecast Preparation**: a pipeline that prepares for the forecasting step by trying to estimate the best features to use for each tax.
1. **Exploratory modeling**: an exploratory step that runs a grid search to find the best features for each tax.
1. **Forecasting**: a pipeline that runs the regressions for each tax and produces
   the final forecasts.

You can think of a pipeline as a series of functions where the inputs to one
function depend on the outputs from a previous function. 

The third step above is an interactive step performed using the Jupyter notebooks in
the `notebooks/` folder. There is a notebook file for each tax. These notebooks
are used to identify the best fitting parameters for each tax, e.g., which
endogenous and exogenous variables should be used in the vector
auto-regressions. Once these best-fit parameters are found, they can be fed
into the modeling pipeline.

To manage the pipelines and the data inputs/outputs, the project uses the
[kedro](https://github.com/quantumblacklabs/kedro) package. From the kedro
documentation:

> Kedro is an open-source Python framework for creating reproducible,
> maintainable and modular data science code. It borrows concepts from software
> engineering best-practice and applies them to machine-learning code; applied
> concepts include modularity, separation of concerns and versioning.

Kedro is useful for our purposes because it enables reproducible revenue
projections, manages the data inputs and outputs, and tracks any changes in the
data and results over time.

There are a few key concepts from kedro that are necessary to understand how
this project works. This section provides a brief introduction to this
concepts. To fully understand kedro, it is worth going through the
[spaceflights
tutorial](https://kedro.readthedocs.io/en/stable/03_tutorial/01_spaceflights_tutorial.html)
on the kedro documentation. The full documentation is available
[here](https://kedro.readthedocs.io/en/stable/index.html).

## The Data Catalog


This section introduces `catalog.yml`. The file is located in `conf/base` and
is a registry of all data sources available for use by the project. It manages
loading and saving of data. 

The Data Catalog provides instructions for how to load and save the various
data inputs and outputs used by the analysis pipelines. The Data Catalog for
this project is available
[here](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/catalog.yml).

The Data Catalog is composed of a series of named entries. Giving official
"names" to the data frames the analysis uses is helpful because then we can
refer to those data frames in our pipeline code. Because the Data Catalog
provides the saving/loading instructions, functions in our pipeline code will
automatically "know" about the data and how to load it. For example: 

```yaml
economic_indicators:
  type: pandas.CSVDataSet
  filepath: data/02_intermediate/economic_indicators_all.csv
  save_args:
    index: True
  load_args:
    index_col: 0
    parse_dates: True
```

We've created a named dataset called "economic_indicators" and specified that
it should be saved as a CSV file to the location
`data/02_intermediate/economic_indicators_all.csv` (more info on the `data/` folder [here](../data/overview)). The other
arguments are passed to the `read_csv()` and `DataFrame.to_csv()` functions
from `pandas`.


!!! note

        For more information, see the 
        [Kedro documentation](https://kedro.readthedocs.io/en/stable/05_data/01_data_catalog.html) on the Data Catalog.


## Configuration

The analysis depends on a set of input parameters that we can define in a
configuration file. These files are located in the `conf/base/` folder of the
repository. There are four relevant parameters files:

- [`conf/base/parameters.yml`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters.yml):
  This holds general parameters about the analysis, such as the start year for
  the plan being analyzed.
- [`conf/base/parameters/data_processing.yml`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters/data_processing.yml):
  This holds parameters specific to the data processing pipeline.
- [`conf/base/parameters/forecast_prep.yml`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters/forecast_prep.yml):
  This holds parameters specific to the forecast prep pipeline.
- [`conf/base/parameters/forecast.yml`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters/forecast.yml):
  This holds parameters specific to the forecasting pipeline.

When running a pipeline or working in one of the Jupyter notebooks, the
parameters will automatically be loaded by `kedro` and available as variables.
Magic!

!!! note
        For more information, see the [Kedro documentation](https://kedro.readthedocs.io/en/stable/04_kedro_project_setup/02_configuration.html#use-parameters) on configuration parameters.


## Nodes

From the kedro documentation:

> Nodes are the building blocks of pipelines and represent tasks. Pipelines are
> used to combine nodes to build workflows, which range from simple machine
> learning workflows to end-to-end production workflows.


Nodes are just Python functions that can be put together in sequential order to
form a pipeline. Nodes are useful because we can specify any named dataset from
the Data Catalog or configuration parameter as either the input or output of
the function. 

For example, the first step of the data processing pipeline uses the following
node:

```python
node(
    func=get_economic_indicators,
    inputs="params:fresh_indicators",
    outputs="economic_indicators",
    name="economic_indicators_node",
)
```

This function outputs the `economic_indicators` data frame that we defined
earlier in the Data Catalog. When running the pipeline, `kedro` will
automatically save the data frame as a CSV to file location we specified in the
data catalog. This node will call the function `get_economic_indicators()`. 

Note the syntax `params:fresh_indicators` — this is how you are able to
reference configuration parameters, by prefixing the name of the variable with
the "params:" tag. In this case, the function takes an input argument that
determines whether the function should download a fresh copy of the indicators
or not.


This is the second node in the data processing pipeline:

```python
node(
    func=get_quarterly_averages,
    inputs="economic_indicators",
    outputs="quarterly_features_raw",
    name="quarterly_features_raw_node",
)
```

This node will call the function
`get_quarterly_averages()`, which will take the quarterly average of the economic indicators. It takes the
raw `economic_indicators` data frame as input and outputs a
`quarterly_features_raw` dataset (that is also defined in the Data Catalog). 

!!! note
        For more information, see the 
        [Kedro documentation](https://kedro.readthedocs.io/en/stable/06_nodes_and_pipelines/01_nodes.html) 
        on Nodes.



## Pipelines

From the kedro documentation: 

> A pipeline organises the dependencies and execution order of your collection
> of nodes, and connects inputs and outputs while keeping your code modular.
> The pipeline determines the node execution order by resolving dependencies
> and does not necessarily run the nodes in the order in which they are passed
> in.

There are three pipelines in this project for data processing, forecast prep, and forecasting.
These are modular and completely separate from each other. The outputs of the
data processing pipeline are used as inputs to the forecast prep pipeline and then
the forecast pipeline.

In the repository, the source code for these pipelines are broken out
separately in to different folders (see
[here](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines)).

More information is provided for each of these pipelines: [data processing](./steps/1-processing.md), 
[forecast prep](./steps/2-forecast-prep.md), and [forecasting](./steps/4-forecast.md).
sections of the documentation.

!!! note
        For more information, see the [Kedro documentation](https://kedro.readthedocs.io/en/stable/06_nodes_and_pipelines/02_pipeline_introduction.html) on Pipelines.



## Next Steps

The following sections of the documentation provide more detail on the
analysis:

- [The data/ folder](./data/overview.md): Everything you need to know about the data
  inputs and outputs in the analysis
- Steps:
  - [1. Data Processing](./steps/1-processing.md): The data processing pipeline
  - [2. Forecast Prep](./steps/2-forecast-prep.md): The forecast prep pipeline
  - [3. Exploratory Modeling](./steps/3-exploratory.md): The exploratory modeling step
  - [4. Forecasting](./steps/4-forecast.md): The forecasting pipeline
 


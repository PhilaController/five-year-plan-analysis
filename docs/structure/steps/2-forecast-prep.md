# 2. The Forecast Prep Pipeline

The forecast prep pipeline is the second step in the analysis code and relies
on the final scaled features that are output from the 
[data processing pipeline](./1-processing.md). It is responsible for preparing for the
forecasting steps by calculating correlations between features, a Granger
causality matrix, and estimates of the most suitable endogenous features for
each tax base.


The code for the pipeline is available in:

`src/fyp_analysis/pipelines/forecast_prep/`
([link](https://github.com/PhilaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/forecast_prep))


## General Workflow

The general workflow for the modeling pipeline is:

1. Calculate the correlation matrix between features
1. Calculate the [Granger causality matrix](https://en.wikipedia.org/wiki/Granger_causality) using functionality
from [statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html)
1. For each tax base, use the Granger matrix to determine which features are
suitable to include as endogenous variables in the VAR fit. 


## Running the Pipeline


To run the forecast prep pipeline, execute:

```
poetry run fyp-analysis-run --pipeline fp
```

where `fp` is short for "forecast prep". 


## Parameters

The parameters for the forecast prep pipeline can be set in the file:
`conf/base/parameters/forecast_prep.yml`
([link](https://github.com/PhilaController/five-year-plan-analysis/blob/main/conf/base/parameters/forecast_prep.yml)).
The parameters are:

- **grangers_maxlag**: When testing for Granger causality, check up to this
  many lags.
- **grangers_max_date**: When testing for Granger causality, include data up
  until this date.


## Steps

This section outlines the steps (also called nodes) in the forecast prep pipeline.
The steps are defined in the
[src/fyp_analysis/pipelines/forecast_prep/pipeline.py file](https://github.com/PhilaController/five-year-plan-analysis/blob/main/src/fyp_analysis/pipelines/forecast_prep/pipeline.py).
In this file, we define the function to run for each node, as well as the
inputs and outputs. 

This pipeline will take the scaled features output by the [data processing pipeline](./1-processing.md), 
calculate feature correlations and a Granger causality matrix.

In python, the pipeline is defined as follows:

```python
def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=get_feature_correlations,
                inputs=["final_scaled_features", "params:min_feature_year"],
                outputs="scaled_feature_correlations",
                name="scaled_feature_correlations_node",
            ),
            node(
                func=get_grangers_matrix,
                inputs=[
                    "final_scaled_features",
                    "params:grangers_maxlag",
                    "params:grangers_max_date",
                ],
                outputs="grangers_matrix",
                name="grangers_matrix_node",
            ),
            node(
                func=get_possible_endog_variables,
                inputs=["final_scaled_features", "grangers_matrix"],
                outputs="possible_endog_variables",
                name="endog_variables_node",
            ),
        ]
    )
```

!!! note "Reminder" 

    As described [here](../../usage/interactive.md), if you are
    working with IPython or in a Jupyter notebook, you can load any named
    dataset (the inputs/outputs above) using the `catalog.load()` function. 
    For example, to load the correlations matrix (the output from step 1), use:

    ``` python
    correlations = catalog.load("scaled_feature_correlations")
    ```


### Step 1: Calculate correlations

- **Function**: `get_feature_correlations()` 
- **Purpose**: Calculate and plot the correlation between scaled features over
time. A correlations figure is saved to the “data / 04_model_input” folder.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Parameter: `min_feature_year`
- **Outputs:** 
    - Dataset: `scaled_feature_correlations` in the `data/04_model_input/`
      folder

The correlations figure looks like this:

![Correlations figure](/assets/img/correlations_min_year_1996.png)

### Step 2: Calculate Granger causality

- **Function**: `get_grangers_matrix()` 
- **Purpose**: Check [Granger
  Causality](https://en.wikipedia.org/wiki/Granger_causality) of all possible
  combinations of the time series indicators.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Parameter: `grangers_maxlag`
    - Parameter: `grangers_max_date`
- **Outputs:** 
    - Dataset: `grangers_matrix` in the `data/04_model_input/` folder

### Step 3: Get possible endogenous variables

- **Function**: `get_possible_endog_variables()`
- **Purpose**: Get possible endogenous variables for tax base features, based
on Granger causality. Return a dictionary of possible endogenous variables
based on Grangers causality for each tax base feature.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Dataset: `grangers_matrix`
- **Outputs:** 
    - Dataset: `possible_endog_variables` in the `data/04_model_input/` folder


# Overview

The modeling pipeline runs the vector auto-regressions and produces
the forecasts for each tax revenue. It relies on the final scaled
features that are output from the [data processing pipeline](../03_processing/overview).

The pipeline relies on the `statsmodels` package to calculate vector
autoregressions (VAR) for each tax base. For more information on `statsmodels`, 
see the [documentation for VARs](https://www.statsmodels.org/dev/vector_ar.html#var-p-processes).

There is also an exploratory phase to the modeling where the bestfit 
parameters are determined for each tax base. This analysis is done in the 
Jupyter notebooks in the `notebooks/` folder. There is a notebook
file for each tax base.

The software for the pipeline is available in:

`src/fyp_analysis/pipelines/modeling/` ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/modeling))

## General Workflow

The general workflow for the modeling pipeline is:

1. Calculate the correlation matrix between features
1. Calculate the [Granger causality matrix](https://en.wikipedia.org/wiki/Granger_causality) using functionality
from [statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html)
1. For each tax base, use the Granger matrix to determine which features are suitable to include as endogenous variables
in the VAR fit. 
1. In an interactive environment (e.g., Jupyter notebook), perform a grid search to determine the best-fit endogenous
and exogenous variables and VAR order number based on the accuracy of the fits on the historical data. 
1. After identifying the best-fit set of parameters for each tax, run the VAR model for each tax with these
parameters to generate the final fits.

## Running the Pipeline


### The full pipeline

To run the modeling pipeline only, execute:

```
fyp-analysis run --pipelines mod
```

where `mod` is short for "modeling". 

You can also run both the data processing and modeling pipelines together.
This is the default configuration if no extra command line arguments are passed:

```
fyp-analysis run
```

### Forecasts and reporting

If we only want to run the forecast and reporting steps of the modeling parameters, 
we can run the following:

```
fyp-analysis run --pipeline mod --from-nodes forecasting_node
```

This will start the pipeline execution at the forecast step, and then run the 
reporting step (which outputs the summary spreadsheet). By starting here, we 
do not need to re-calculate the calculation of the Granger matrix and other
pre-modeling steps.

## Parameters

The parameters for the data processing pipeline can be set in the 
file: `conf/base/parameters/modeling.yml` ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters/modeling.yml)). The parameters are:


- **max_fit_date**: The maximum date to include in the VAR fits.
- **grangers_maxlag**: When testing for Granger causality, check up to this many lags.
- **grangers_max_date**: When testing for Granger causality, include data up until this date.



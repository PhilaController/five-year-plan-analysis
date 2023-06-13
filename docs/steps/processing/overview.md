# Overview

The data processing pipeline starts by downloading the 
latest economic indicators and ends by outputting 
a set of features that can be input into the VAR modeling
pipeline. 

Its main purpose is to identify the 
series of transformations that will make each 
time series indicator stationary so that the indicators are 
suitable for use in a vector autoregression.

The software for the pipeline is available in:

`src/fyp_analysis/pipelines/data_processing/` ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/data_processing))

## Calculating Stationarity

One of the main outputs of this pipeline is the "stationarity guide," a spreadsheet with information
 for making each feature stationary. For each feature, the spreadsheet contains the following information:
- Can we take the log of the variable (e.g., is it non-negative?)?
- How many differences for stationarity?
- Should we normalize the data first?

The spreadsheet is available in the `data/02_intermediate/` folder [(link)](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/02_intermediate/stationary_guide.xlsx).

The data processing pipeline also creates the diagnostic stationarity plots for all 
tax bases and save them to `data / 02_intermediate / stationary_figures`. These figures 
test the autocorrelation and partial autocorrelation of the time series. For example, 
the stationarity figure for the Wage Tax is:

![Wage Tax Stationarity Figure](https://github.com/PhiladelphiaController/five-year-plan-analysis/raw/main/data/02_intermediate/stationary_figures/WageBase.png)

## Running the Pipeline

To run the pipeline, execute:

```
fyp-analysis run --pipelines dp
```

where `dp` is short for "data processing".


## Parameters

The parameters for the data processing pipeline can be set in the 
file: `conf/base/parameters/data_processing.yml` ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/conf/base/parameters/data_processing.yml)). The parameters are:

- **fresh_indicators**: whether to download fresh economic indicators
- **seasonal_adjustments**: the names of the columns to apply seasonal adjustments to
- **min_feature_year**: the minimum year to trim the indicators to



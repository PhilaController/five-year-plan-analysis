# 1. The Data Processing Pipeline

The analysis code begins with the data processing pipeline. This pipeline
starts by downloading the latest economic indicators and ends by outputting a
set of features that can be input into the VAR modeling pipeline. 

Its main purpose is to identify the series of transformations that will make
each time series indicator stationary so that the indicators are suitable for
use in a vector autoregression.

The code for the pipeline is available at:

`src/fyp_analysis/pipelines/data_processing/`
([link](https://github.com/PhilaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/data_processing))


## Running the Pipeline

To run the pipeline, execute:

```
poetry run fyp-analysis-run --pipeline dp
```

where `dp` is short for "data processing".


## Parameters

The parameters for the data processing pipeline can be set in the file:
`conf/base/parameters/data_processing.yml`
([link](https://github.com/PhilaController/five-year-plan-analysis/blob/main/conf/base/parameters/data_processing.yml)).
The parameters are:

- **fresh_indicators**: whether to download fresh economic indicators
- **seasonal_adjustments**: the names of the columns to apply seasonal
  adjustments to
- **min_feature_year**: the minimum year to trim the indicators to


## Steps

This section outlines the steps (also called nodes) in the data processing
pipeline. The steps are defined in the
[src/fyp_analysis/pipelines/data_processing/pipeline.py
file](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/src/fyp_analysis/pipelines/data_processing/pipeline.py#L15).
In this file, we define the function to run for each step, as well as the
inputs and outputs of each function.

This pipeline will download the latest version of a set of economic indicators,
perform various transformations, and output a set of features suitable to be
used as input to the [modeling pipeline](../../modeling/overview).

!!! warning
    Make sure you have properly set up your local API credentials before running
    this pipeline. Otherwise, you won't be able to download all of the necessary indicators. 
    See the [setup instructions](../../../install/#set-up-your-api-credentials) for more information.


In python, the pipeline is defined as follows:

```python
def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=get_economic_indicators,
                inputs="params:fresh_indicators",
                outputs="economic_indicators",
                name="economic_indicators_node",
            ),
            node(
                func=get_quarterly_averages,
                inputs="economic_indicators",
                outputs="quarterly_features_raw",
                name="quarterly_features_raw_node",
            ),
            node(
                func=impute_cbo_values,
                inputs=[
                    "quarterly_features_raw",
                    "params:plan_start_year",
                    "params:cbo_forecast_date",
                ],
                outputs="quarterly_features_cbo_imputed",
                name="impute_cbo_node",
            ),
            node(
                func=combine_features_and_bases,
                inputs=["quarterly_features_cbo_imputed", "plan_details"],
                outputs="features_and_bases",
                name="combine_features_bases_node",
            ),
            node(
                func=seasonally_adjust_features,
                inputs=["features_and_bases", "params:seasonal_adjustments"],
                outputs="features_and_bases_sa",
                name="seasonal_adjustment_node",
            ),
            node(
                func=get_stationary_guide,
                inputs="features_and_bases_sa",
                outputs="stationary_guide",
                name="stationary_guide_node",
            ),
            node(
                func=get_final_unscaled_features,
                inputs=["features_and_bases_sa", "params:min_feature_year"],
                outputs="final_unscaled_features",
                name="final_unscaled_features_node",
            ),
            node(
                func=get_final_scaled_features,
                inputs=[
                    "final_unscaled_features",
                    "stationary_guide",
                ],
                outputs="final_scaled_features",
                name="final_scaled_features_node",
            ),
        ]
    )
```

!!! note "Reminder" 

    As described [here](../../../usage/interactive), if you are
    working with IPython or in a Jupyter notebook, you can load any named
    dataset (the inputs/outputs above) using the `catalog.load()` function. 
    For example, to load the "economic_indicators" dataset (the output from step 1), use:

    ``` python
    indicators = catalog.load("economic_indicators")
    ```



### Step 1: Download indicators

- **Function**: `get_economic_indicators()`
- **Purpose**: Download the latest set of economic indicators and save them
  locally
- **Inputs**: 
    - Parameter: `fresh_indicators`
- **Outputs:** 
    - Dataset: `economic_indicators` in the `data/02_intermediate/` folder

Economic indicators are defined in the
[src/fyp_analysis/pipelines/data_processing/indicators/sources](https://github.com/PhilaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/data_processing/indicators/sources)
folder. Right now, there are various sources, including FRED, Quandl, CARTO
(Philadelphia open data), and Zillow, with a JSON file for each source that
lists the information necessary for download. New indicators can be added by
adding a new entry to the appropriate JSON file.

The current set of indicators includes the following:

{{ read_csv('docs/assets/data/indicators.csv') }}


### Step 2: Impute CBO values

- **Function**: `impute_cbo_values()`
- **Purpose**: Impute CBO forecast values for Q4 of the current fiscal year.
- **Inputs**: 
    - Dataset: `economic_indicators`
- **Outputs:** 
    - Dataset: `quarterly_features_raw` in the `data/02_intermediate/` folder

For economic indicators that CBO is projections for, this will impute the
forecast value for Q4 of the current fiscal year, where an actual value is
lacking.

### Step 3: Get quarterly averages

- **Function**: `get_quarterly_averages()`
- **Purpose**: Get the quarterly averages of the indicators and remove any
  indicators with annual frequency.
- **Inputs**: 
    - Dataset: `quarterly_features_raw`
    - Parameter: `plan_start_year`
    - Parameter: `cbo_forecast_date`
- **Outputs:** 
    - Dataset: `quarterly_features_cbo_imputed` in the `data/02_intermediate/`
      folder

### Step 4: Combine indicators and tax bases

- **Function**: `combine_features_and_bases()`
- **Purpose**: Combine the economic indicator features and the tax base data
  into a single data frame.
- **Inputs**: 
    - Dataset: `quarterly_features_cbo_imputed`
    - Dataset: `plan_details`
- **Outputs:** 
    - Dataset: `features_and_bases` in the `data/02_intermediate/` folder

### Step 5: Seasonally adjust features

- **Function**: `seasonally_adjust_features()`
- **Purpose**: Seasonally adjust the specified columns, using the [LOESS
  functionality in
  statsmodels](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html).
- **Inputs**: 
    - Dataset: `features_and_bases`
    - Parameter: `seasonal_adjustments`
- **Outputs:** 
    - Dataset: `features_and_bases_sa` in the `data/02_intermediate/` folder

### Step 6: Calculate stationary guide

- **Function**: `get_stationary_guide()`
- **Purpose**: Make the stationary guide, a spreadsheet which contains the
  instructions for making each feature stationary.
- **Inputs**: 
    - Dataset: `features_and_bases_sa`
- **Outputs:** 
    - Dataset: `stationary_guide` in the `data/02_intermediate/` folder


 For each feature, the stationary guide contains the following information:

- Can we take the log of the variable (e.g., is it non-negative?)?
- How many differences for stationary?
- Should we normalize the data first?

The spreadsheet is available in the `data/02_intermediate/` folder
[(link)](https://github.com/PhilaController/five-year-plan-analysis/blob/main/data/02_intermediate/stationary_guide.xlsx).

This step also creates the diagnostic stationary plots for all tax bases and
save them to `data / 02_intermediate / stationary_figures`. These figures test
the autocorrelation and partial autocorrelation of the time series. For
example, the stationary figure for the Wage Tax is:

![Wage Tax stationary
Figure](https://github.com/PhilaController/five-year-plan-analysis/raw/main/data/02_intermediate/stationary_figures/WageBase.png)

### Step 7: Final unscaled features

- **Function**: `get_final_unscaled_features()`
- **Purpose**: Get the final unscaled features to input into the modeling
pipeline. The only additional preprocessing performed in this step is trimming
to the specific minimum year for all features and tax bases.
- **Inputs**: 
    - Dataset: `features_and_bases_sa`
    - Parameter: `min_feature_year`
- **Outputs:** 
    - Dataset: `final_unscaled_features` in the `data/03_feature/` folder

### Step 8: Final scaled features

- **Function**: `get_final_scaled_features()`
- **Purpose**: Get the final scaled features to input into the modeling
pipeline. This applies the final preprocessor based on the "stationary guide."
For each feature, it takes the log of the feature if able (if not, it applies a
normalization). Finally, the preprocessor differences the feature until it is
stationary.
- **Inputs**: 
    - Dataset: `final_unscaled_features`
- **Outputs:** 
    - Dataset: `final_scaled_features` in the `data/03_feature/` folder



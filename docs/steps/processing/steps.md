# Steps

This section outlines the steps in the data processing pipeline. The steps
are defined in the [src/fyp_analysis/pipelines/data_processing/pipeline.py file](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/src/fyp_analysis/pipelines/data_processing/pipeline.py#L15).
In this file, we define the function to run for each node, as well as the 
inputs as outputs. 

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

**Reminder**

As described [here](../01_getting_started/interactive), if you are working with IPython or in a Jupyter notebook, you 
can load any named dataset using the `catalog.load()` function. For 
example, to load the "economic_indicators" dataset, use:

```python
indicators = catalog.load("economic_indicators")
```

## Step 1

- **Function**: `get_economic_indicators()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.get_economic_indicators.html#fyp_analysis.pipelines.data_processing.nodes.get_economic_indicators)
- **Purpose**: Download the latest set of economic indicators and save them locally
- **Inputs**: 
    - Parameter: `fresh_indicators`
- **Outputs:** 
    - Dataset: `economic_indicators` in the `data/02_intermediate/` folder

## Step 2

- **Function**: `impute_cbo_values()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.impute_cbo_values.html#fyp_analysis.pipelines.data_processing.nodes.impute_cbo_values)
- **Purpose**: Impute CBO forecast values for Q4 of the current fiscal year.
- **Inputs**: 
    - Dataset: `economic_indicators`
- **Outputs:** 
    - Dataset: `quarterly_features_raw` in the `data/02_intermediate/` folder

## Step 3

- **Function**: `get_quarterly_averages()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.get_quarterly_averages.html#fyp_analysis.pipelines.data_processing.nodes.get_quarterly_averages)
- **Purpose**: Get the quarterly averages of the indicators and remove any indicators with annual frequency.
- **Inputs**: 
    - Dataset: `quarterly_features_raw`
    - Parameter: `plan_start_year`
    - Parameter: `cbo_forecast_date`
- **Outputs:** 
    - Dataset: `quarterly_features_cbo_imputed` in the `data/02_intermediate/` folder

## Step 4

- **Function**: `combine_features_and_bases()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.combine_features_and_bases.html#fyp_analysis.pipelines.data_processing.nodes.combine_features_and_bases)
- **Purpose**: Combine the economic indicator features and the tax base data into a single data frame.
- **Inputs**: 
    - Dataset: `quarterly_features_cbo_imputed`
    - Dataset: `plan_details`
- **Outputs:** 
    - Dataset: `features_and_bases` in the `data/02_intermediate/` folder

## Step 5

- **Function**: `seasonally_adjust_features()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.seasonally_adjust_features.html#fyp_analysis.pipelines.data_processing.nodes.seasonally_adjust_features)
- **Purpose**: Seasonally adjust the specified columns, using the [LOESS functionality in statsmodels](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html).
- **Inputs**: 
    - Dataset: `features_and_bases`
    - Parameter: `seasonal_adjustments`
- **Outputs:** 
    - Dataset: `features_and_bases_sa` in the `data/02_intermediate/` folder

## Step 6

- **Function**: `get_stationary_guide()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.get_stationary_guide.html#fyp_analysis.pipelines.data_processing.nodes.get_stationary_guide)
- **Purpose**: Make the stationarity guide, a spreadsheet which contains the instructions for making each feature stationary.
- **Inputs**: 
    - Dataset: `features_and_bases_sa`
- **Outputs:** 
    - Dataset: `stationary_guide` in the `data/02_intermediate/` folder

## Step 7

- **Function**: `get_final_unscaled_features()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.get_final_unscaled_features.html#fyp_analysis.pipelines.data_processing.nodes.get_final_unscaled_features)
- **Purpose**: Get the final unscaled features to input into the modeling pipeline. The only
additional step is trimming to the specific minimum year for all features and tax bases.
- **Inputs**: 
    - Dataset: `features_and_bases_sa`
    - Parameter: `min_feature_year`
- **Outputs:** 
    - Dataset: `final_unscaled_features` in the `data/03_feature/` folder

## Step 8

- **Function**: `get_final_scaled_features()` [(docs)](fyp_analysis.pipelines.data_processing.nodes.get_final_scaled_features.html#fyp_analysis.pipelines.data_processing.nodes.get_final_scaled_features)
- **Purpose**: Get the final scaled features to input into the modeling pipeline. This applies the final preprocessor based
on the "stationary guide." For each feature, it takes the log of the feature if able (if not, it applies a normalization). Finally, 
the preprocessor differences the feature until it is stationary.
- **Inputs**: 
    - Dataset: `final_unscaled_features`
- **Outputs:** 
    - Dataset: `final_scaled_features` in the `data/03_feature/` folder
# Steps

This section outlines the steps in the data processing pipeline. The steps
are defined in the [src/fyp_analysis/pipelines/data_processing/modeling.py file](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/src/fyp_analysis/pipelines/modeling/pipeline.py#L10).
In this file, we define the function to run for each node, as well as the 
inputs as outputs. 

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

## Step 1

- **Function**: `get_feature_correlations()` [(docs)](fyp_analysis.pipelines.modeling.nodes.get_feature_correlations.html#fyp_analysis.pipelines.modeling.nodes.get_feature_correlations)
- **Purpose**: Calculate and plot the correlation between scaled features over time. A correlations figure is saved 
to the “data / 04_model_input” folder.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Parameter: `min_feature_year`
- **Outputs:** 
    - Dataset: `scaled_feature_correlations` in the `data/04_model_input/` folder

## Step 2

- **Function**: `get_grangers_matrix()` [(docs)](fyp_analysis.pipelines.modeling.nodes.get_grangers_matrix.html#fyp_analysis.pipelines.modeling.nodes.get_grangers_matrix)
- **Purpose**: Check Granger Causality of all possible combinations of the time series indicators.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Parameter: `grangers_maxlag`
    - Parameter: `grangers_max_date`
- **Outputs:** 
    - Dataset: `grangers_matrix` in the `data/04_model_input/` folder

## Step 3

- **Function**: `get_possible_endog_variables()` [(docs)](fyp_analysis.pipelines.modeling.nodes.get_possible_endog_variables.html#fyp_analysis.pipelines.modeling.nodes.get_possible_endog_variables)
- **Purpose**: Get possible endogenous variables for tax base features, based on Granger causality. Return a dictionary of possible 
endogenous variables based on Grangers causality for each tax base feature.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Dataset: `grangers_matrix`
- **Outputs:** 
    - Dataset: `possible_endog_variables` in the `data/04_model_input/` folder


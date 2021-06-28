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
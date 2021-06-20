from kedro.pipeline import Pipeline, node

from .nodes import (
    get_feature_correlations,
    get_grangers_matrix,
    get_possible_endog_variables,
)


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
                inputs=["final_scaled_features"],
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

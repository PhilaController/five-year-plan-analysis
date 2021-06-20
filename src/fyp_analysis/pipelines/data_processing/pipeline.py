from kedro.pipeline import Pipeline, node

from .nodes import (
    combine_features_and_bases,
    get_economic_indicators,
    get_final_scaled_features,
    get_final_unscaled_features,
    get_quarterly_averages,
    get_stationary_guide,
    impute_cbo_values,
    seasonally_adjust_features,
)


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

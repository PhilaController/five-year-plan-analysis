from kedro.pipeline import Pipeline, node

from .nodes import (
    get_feature_correlations,
    get_grangers_matrix,
    get_possible_endog_variables,
    report_forecast_results,
    run_forecasts,
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
            node(
                func=run_forecasts,
                inputs=[
                    "final_unscaled_features",
                    "stationary_guide",
                    "plan_details",
                    "params:plan_start_year",
                    "params:cbo_forecast_date",
                ],
                outputs=["tax_base_forecasts", "tax_revenue_forecasts"],
                name="forecasting_node",
            ),
            node(
                func=report_forecast_results,
                inputs=[
                    "params:plan_start_year",
                    "tax_revenue_forecasts",
                    "tax_base_forecasts",
                ],
                outputs=None,
                name="reporting_node",
            ),
        ]
    )

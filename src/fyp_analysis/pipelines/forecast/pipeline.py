from kedro.pipeline import Pipeline, node

from .nodes import (
    report_forecast_results,
    run_forecasts,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=run_forecasts,
                inputs=[
                    "final_unscaled_features",
                    "stationary_guide",
                    "params:plan_start_year",
                    "params:plan_type",
                    "params:cbo_forecast_date",
                    "params:forecast_types",
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

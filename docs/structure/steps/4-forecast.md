# 4. The Forecasting Pipeline


The forecast pipeline runs the vector auto-regressions and produces
the final forecasts for each tax revenue. Each of the three previous steps
must be performed before this step. 

After identifying the best-fit set of 
forecast parameters for each tax in the [exploratory step](./3-exploratory.md), 
this pipeline will run the VAR model for each tax with these parameters to 
generate the final fits. It outputs a summary file of 
the revenue forecasts: `data/07_reporting/revenue_summary.xlsx`.

The pipeline relies on the `statsmodels` package to calculate vector
autoregressions (VAR) for each tax base. For more information on `statsmodels`, 
see the [documentation for VARs](https://www.statsmodels.org/dev/vector_ar.html#var-p-processes).

The code for the pipeline is available in:

`src/fyp_analysis/pipelines/forecast/` ([link](https://github.com/PhilaController/five-year-plan-analysis/tree/main/src/fyp_analysis/pipelines/forecast))




## Running the Pipeline

To run the forecast pipeline, execute:

```
poetry run fyp-analysis-run --pipeline forecast
```


## Parameters

The parameters for the data processing pipeline can be set in the 
file: `conf/base/parameters/forecast.yml` ([link](https://github.com/PhilaController/five-year-plan-analysis/blob/main/conf/base/parameters/modeling.yml)). The parameters are:


- **max_fit_date**: The maximum date to include in the VAR fits.
- **forecast_types**: For each tax base, what kind of forecast to run, either "var" or "file". This will depend on what notebook you used in the exploratory phase. If you generated a tax base forecast not from VAR fits in the notebook for a tax, you will want to specify "file" here. See for example, the realty transfer tax forecast notebook.

## Steps

This section outlines the steps (also called nodes) in the forecast pipeline.
The steps are defined in the
[src/fyp_analysis/pipelines/forecast/pipeline.py
file](https://github.com/PhilaController/five-year-plan-analysis/blob/main/src/fyp_analysis/pipelines/forecast/pipeline.py).
In this file, we define the function to run for each node, as well as the
inputs and outputs. 

This pipeline will calculate a set of forecasts and output a summary of
the results.

In python, the pipeline is defined as follows:

```python
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

```


### Step 1: Run forecasts

- **Function**: `run_forecasts()`
- **Purpose**: Run the forecasts for each tax base.
- **Inputs**: 
    - Dataset: `final_scaled_features`
    - Dataset: `grangers_matrix`
- **Outputs:** 
    - Dataset: `tax_base_forecasts`, saved as `06_model_output/final_tax_bases.csv`
    - Dataset: `tax_revenue_forecasts`, saved as `06_model_output/final_tax_revenues.csv`


### Step 2: Summarize the results

- **Function**: `report_forecast_results()`
- **Purpose**: Create the summary file of the revenue forecasts
- **Inputs**: 
    - Parameter: `plan_start_year`
    - Dataset: `tax_base_forecasts`
    - Dataset: `tax_revenue_forecasts`
- **Outputs:** 
    - This outputs a summary excel file `data/07_reporting/revenue_summary.xlsx`






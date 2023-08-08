---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.5
  kernelspec:
    display_name: Kedro (fyp_analysis)
    language: python
    name: kedro_fyp_analysis
---

<!-- #region papermill={"duration": 0.139638, "end_time": "2020-07-09T01:46:36.924518", "exception": false, "start_time": "2020-07-09T01:46:36.784880", "status": "completed"} -->
# VAR Revenue Modeling: Net Profits Tax

**Purpose:** For the tax revenue of interest, use vector auto-regression to produce forecasts on historical data and identify the model parameters that produce the most accurate forecasts.

Once the best fit is determined, we can plug the parameters into the main "parameters.yml" file and run reproducible model fits through the command line using `fyp-analysis`.
<!-- #endregion -->

```python
TAX_NAME = "NPT"
```

```python
TAX_BASE_COLUMN = f"{TAX_NAME}Base"
```

## Software Setup


If changes are made to the analysis code, run the below cell to reload the changes:

```python
%reload_kedro
```

Imports:

```python
# Base imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from phila_style.matplotlib import get_theme
```

```python
# Data inputs
from fyp_analysis.extras.datasets import PlanDetails, Taxes, load_cbo_data

# The main preprocess pipeline
from fyp_analysis.pipelines.data_processing.preprocess import PreprocessPipeline

# Prediction functions
from fyp_analysis.pipelines.modeling.predict import (
    aggregate_to_fiscal_year,
    fit_var_model,
    get_forecasts_from_fits,
    get_possible_endog_variables,
    plot_forecast_results,
    plot_projection_comparison,
    run_possible_models,
)
```

```python
pd.options.display.max_columns = 999
```

## Parameter Setup


Set up the data catalog. We can use `DATA.load()` to load specific data instances.

```python
DATA = context.catalog
```

Available keys in data catalog:

```python
DATA.list()
```

Load the parameter dict too:

```python
PARAMS = context.params
```

```python papermill={"duration": 0.107041, "end_time": "2020-07-09T01:46:39.323680", "exception": false, "start_time": "2020-07-09T01:46:39.216639", "status": "completed"}
PARAMS
```

Extract specific parameters:

```python
# Trim features to this start year
min_year = PARAMS["min_feature_year"]

# When is the CBO forecast from?
cbo_forecast_date = PARAMS["cbo_forecast_date"]

# First fiscal year of the plan and type
plan_start_year = PARAMS["plan_start_year"]
plan_type = PARAMS["plan_type"]
```

```python
f"Modeling revenue for the {TAX_NAME} tax for the {plan_type.capitalize()} FY {plan_start_year} - FY {plan_start_year+4} Five Year Plan"
```

## Data Setup


Load the correlation matrix and Granger matrix:

```python
C = DATA.load("scaled_feature_correlations")  # correlation matrix
G = DATA.load("grangers_matrix")  # Granger matrix
```

Load taxes object responsible for loading historical tax data:

```python
# Load the Plan details we are using
plan_details = PlanDetails.from_file(
    plan_start_year=plan_start_year, plan_type=plan_type
)

# All taxes
all_taxes = Taxes(plan_details)

# This tax
this_tax = all_taxes[TAX_NAME]
```

Data associated with a tax is stored in the `.data` attribute:

```python
this_tax.data.tail()
```

Load the final unscaled features:

```python
unscaled_features = DATA.load("final_unscaled_features")
```

```python
unscaled_features.head()
```

The final scaled features:

```python
scaled_features = DATA.load("final_scaled_features")
```

```python
scaled_features.head()
```

Determine the name of the scaled tax base column:

```python
SCALED_COLUMN = [col for col in scaled_features.columns if TAX_BASE_COLUMN in col][0]
```

```python
SCALED_COLUMN
```

Initialize the preprocesser that goes from unscaled to scaled features:

```python
guide = DATA.load("stationary_guide")
preprocess = PreprocessPipeline(guide)
```

```python
guide.tail(20)
```

Load the CBO data frame:

```python
cbo_data = load_cbo_data(date=cbo_forecast_date)
cbo_columns = cbo_data.columns.tolist()
```

```python
cbo_data.head()
```

<!-- #region papermill={"duration": 0.081994, "end_time": "2020-07-09T01:46:48.673887", "exception": false, "start_time": "2020-07-09T01:46:48.591893", "status": "completed"} -->
## Forecast

In this section, we use a combination of correlations, Granger matrix, and intuition to select possible endogenous variables to include in the VAR fit. Then, we do a grid search to find the bestfit parameters based on accuracy on historical data.
<!-- #endregion -->

### Correlations

Get top and bottom 10 correlations with our tax base:

```python papermill={"duration": 0.098563, "end_time": "2020-07-09T01:46:49.400253", "exception": false, "start_time": "2020-07-09T01:46:49.301690", "status": "completed"}
C[SCALED_COLUMN].sort_values().head(n=10)
```

```python papermill={"duration": 0.101371, "end_time": "2020-07-09T01:46:49.592345", "exception": false, "start_time": "2020-07-09T01:46:49.490974", "status": "completed"}
C[SCALED_COLUMN].sort_values().tail(n=10)
```

Load the possible endog variables:

```python
possible_endog = DATA.load("possible_endog_variables")[SCALED_COLUMN]
```

```python
possible_endog
```

### Run the grid search

This can take some time to run depending on how many variables we are searching over.

**Note**: the list of endogeneous variables used below is created from a combination of intuition and those variables identified in the causality analysis above. 

```python papermill={"duration": 68.918069, "end_time": "2020-07-09T01:47:58.819366", "exception": false, "start_time": "2020-07-09T01:46:49.901297", "status": "completed"}
all_fits = run_possible_models(
    unscaled_features,
    preprocess,
    main_endog=TAX_BASE_COLUMN,
    other_endog=[
        "NonresidentialInvestment",
        "GDPPriceIndex",
        "CorporateProfits",
        "NYCGasPrice",
        "ContinuedClaimsPA",
        "UnemploymentPhilly",
        "RealRetailFoodServiceSales",
        "NonfarmEmployeesPhillyMSA",
        "CarSales",
        "AlcoholSales",
    ],
    orders=[2, 3, 4, 5, 6],
    grangers=G,
    max_fit_date=[
        "2019-12-31",  # pre-covid
        f"{plan_start_year-1}-06-30",  # latest
    ],
    cbo_columns=cbo_columns,
    alpha=0.05,
    max_exog=2,
    max_other_endog=1,
    model_quarters=[False, True],
)
```

Split fits that do and do not have at least one CBO variable as exogenous variable and compare:

```python
fits_with_exog = list(filter(lambda d: len(d["exog_cols"]) > 0, all_fits))
fits_no_exog = list(filter(lambda d: len(d["exog_cols"]) == 0, all_fits))
```

Compare the historical accuracy of the top fits with and without exog variables:

```python
with plt.style.context(get_theme()):

    fig, ax = plt.subplots()

    ax.hist(
        [d["target_mape"] for d in fits_with_exog[:20]],
        bins="auto",
        histtype="step",
        label="With Exog",
        zorder=10,
        lw=2,
    )
    ax.hist(
        [d["target_mape"] for d in fits_no_exog[:20]],
        bins="auto",
        histtype="step",
        label="No Exog",
        lw=2,
    )
    ax.legend()
    plt.show();
```

### Run the VAR with the best-fit params

```python papermill={"duration": 0.097752, "end_time": "2020-07-09T01:47:59.010579", "exception": false, "start_time": "2020-07-09T01:47:58.912827", "status": "completed"}
best_params = fits_with_exog[0]
best_params
```

```python papermill={"duration": 0.406433, "end_time": "2020-07-09T01:47:59.509777", "exception": false, "start_time": "2020-07-09T01:47:59.103344", "status": "completed"}
result, forecast = fit_var_model(
    unscaled_features,
    preprocess,
    plan_start_year=plan_start_year,
    max_fit_date=best_params["max_fit_date"],
    cbo_data=cbo_data,
    endog_cols=best_params["endog_cols"],
    order=best_params["order"],
    exog_cols=best_params["exog_cols"],
    model_quarters=best_params["model_quarters"],
)
print(result.aic)
```

```python papermill={"duration": 0.109039, "end_time": "2020-07-09T01:47:59.720595", "exception": false, "start_time": "2020-07-09T01:47:59.611556", "status": "completed"}
result.summary()
```

```python papermill={"duration": 1.348711, "end_time": "2020-07-09T01:48:01.173942", "exception": false, "start_time": "2020-07-09T01:47:59.825231", "status": "completed"}
fig = plot_forecast_results(forecast, TAX_BASE_COLUMN)
plt.show()
```

### Compare to Budget Office Projections

```python
[f["target_mape"] for f in all_fits[:10]]
```

Get an average forecast over the top *N* fits:

```python
TOP = 10

all_forecasts = get_forecasts_from_fits(
    unscaled_features,
    preprocess,
    all_fits,
    TAX_BASE_COLUMN,
    plan_start_year,
    cbo_data,
    max_fits=TOP,
)
```

```python
average_fit = all_forecasts.mean(axis=1).squeeze().rename(TAX_BASE_COLUMN)
```

Plot:

```python
plot_projection_comparison(this_tax, average_fit)
plt.show()
```

### Save Best-fit Parameters

```python
DATA.save("npt_fit_params", all_fits[:TOP])
```

```python

```

```python

```

```python

```

```python

```

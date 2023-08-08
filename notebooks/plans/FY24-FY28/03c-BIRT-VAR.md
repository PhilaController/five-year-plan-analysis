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
# VAR Revenue Modeling: BIRT

**Purpose:** For the tax revenue of interest, use vector auto-regression to produce forecasts on historical data and identify the model parameters that produce the most accurate forecasts.

Once the best fit is determined, we can plug the parameters into the main "parameters.yml" file and run reproducible model fits through the command line using `fyp-analysis`.
<!-- #endregion -->

```python
TAX_NAME = "BIRT"
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
import pandas as pd
from matplotlib import pyplot as plt
from phila_style.matplotlib import get_theme
```

```python
from fyp_analysis.extras.datasets import PlanDetails, Taxes, load_cbo_data
from fyp_analysis.pipelines.data_processing.preprocess import PreprocessPipeline
from fyp_analysis.pipelines.modeling.predict import (
    get_forecasts_from_fits,
    plot_projection_comparison,
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

Available data:

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


Load taxes object responsible for loading historical tax data"

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
this_tax.data.head()
```

```python
this_tax.data.tail(20)
```

```python
this_tax.tax_bases_to_revenue??
```

Load the final unscaled features:

```python
unscaled_features = DATA.load("final_unscaled_features")
```

```python
unscaled_features.head()
```

Initialize the preprocesser that goes from unscaled to scaled features:

```python
guide = DATA.load("stationary_guide")
preprocess = PreprocessPipeline(guide)
```

```python
guide.head()
```

Load the CBO data frame:

```python
cbo_data = load_cbo_data(date=cbo_forecast_date)
cbo_columns = cbo_data.columns.tolist()
```

```python
cbo_data.head()
```

## Load Bestfit Parameters

```python
net_income_fits = DATA.load("net_income_fit_params")
gross_receipts_fits = DATA.load("gross_receipts_fit_params")
```

```python
forecast_ni_base = get_forecasts_from_fits(
    unscaled_features,
    preprocess,
    net_income_fits,
    "NetIncomeBase",
    plan_start_year,
    cbo_data,
    max_fits=1,
    average=True,
)
```

```python
forecast_gr_base = get_forecasts_from_fits(
    unscaled_features,
    preprocess,
    gross_receipts_fits,
    "GrossReceiptsBase",
    plan_start_year,
    cbo_data,
    max_fits=1,
    average=True,
)
```

### Compare to Budget Office Projections


Plot:

```python
plot_projection_comparison(this_tax, forecast_gr_base, forecast_ni_base);
```

```python

```

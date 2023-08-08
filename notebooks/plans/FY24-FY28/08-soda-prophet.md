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
# VAR Revenue Modeling: Soda Tax

**Purpose:** For the tax revenue of interest, use ARIMA modeling via the prophet package to produce forecasts on historical data.

Once the best fit is determined, we can plug the parameters into the main "parameters.yml" file and run reproducible model fits through the command line using `fyp-analysis`.
<!-- #endregion -->

```python
# Base imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from phila_style import *
from phila_style.matplotlib import get_theme

# Prophet
from prophet import Prophet

# fyp-analsis
from fyp_analysis import SRC_DIR
from fyp_analysis.extras.datasets import PlanDetails
from fyp_analysis.pipelines.modeling.predict import (
    aggregate_to_fiscal_year,
    plot_projection_comparison,
)
```

```python
pd.options.display.max_columns = 999
```

## Setup

```python
PARAMS = context.params
```

```python
# First fiscal year of the plan and type
plan_start_year = PARAMS["plan_start_year"]
plan_type = PARAMS["plan_type"]
```

```python
# Load the Plan details we are using
plan_details = PlanDetails.from_file(
    plan_start_year=plan_start_year, plan_type=plan_type
)
```

## Load the monthly data

This is monthly data pulled from the monthly Revenue Department reports.

```python
city_tax_collections = pd.read_csv(
    "https://raw.githubusercontent.com/PhilaController/phl-budget-data/main/src/phl_budget_data/data/processed/collections/city-tax-collections.csv"
)
```

```python
soda_tax = (
    city_tax_collections.query("name == 'soda' and kind=='total'")
    .assign(date=lambda df: pd.to_datetime(df.date))
    .query("total > 0")
    .set_index("date")
)
```

```python
soda_tax.head()
```

```python
with plt.style.context(get_theme()):
    soda_tax.plot(y="total", legend=False, clip_on=False, lw=2, marker="o")
    plt.show();
```

## Modeling

```python
def get_monthly_forecast(
    data,
    column="total",
    event_dates=[("2020-04-01", "2020-07-01"), ("2020-11-01", "2021-04-01")],
    **fit_kwargs,
):

    # Forecast end date
    forecast_end_date = f"{PARAMS['plan_start_year']+4}-06-30"

    # Format the input data
    df = (
        data[column]
        .rename_axis("ds")
        .reset_index()
        .rename(columns={column: "y"})
        .sort_values("ds")
        .assign(ds=lambda df: df.ds.dt.tz_localize(None))
    )

    # Create lockdowns
    events = []
    for i, dates in enumerate(event_dates, start=1):
        events.append(
            {
                "holiday": f"event_{i}",
                "ds": dates[0],
                "lower_window": 0,
                "ds_upper": dates[1],
            }
        )

    if len(events):
        events = pd.DataFrame(events)
        for t_col in ["ds", "ds_upper"]:
            events[t_col] = pd.to_datetime(events[t_col])
        events["upper_window"] = (events["ds_upper"] - events["ds"]).dt.days

    if len(events):
        model = Prophet(holidays=events, **fit_kwargs)
    else:
        model = Prophet(**fit_kwargs)

    model.fit(df)

    forecast_period = (
        pd.Timestamp(forecast_end_date).to_period(freq="M")
        - df["ds"].max().to_period(freq="M")
    ).n + 1

    future = model.make_future_dataframe(periods=forecast_period, freq="M")
    forecast = model.predict(future)
    return model, forecast
```

```python
model, forecast = get_monthly_forecast(soda_tax)
```

```python
model.plot(forecast)
plt.show();
```

```python
FORECAST = aggregate_to_fiscal_year(
    forecast.set_index("ds")["yhat"], freq="MS"
).squeeze()
```

```python
FORECAST / 1e6
```

```python
growth_rates = 100 * (FORECAST.diff() / FORECAST.shift())

growth_rates
```

## Compare to Five Year Plan and save

Five Year Plan numbers from Proposed FY24-FY28 Plan:

**Note: pull these numbers manually**

```python
FYP = pd.Series(
    [73501000, 74368000, 73624000, 73226000, 72911000],
    index=pd.Index(range(plan_start_year, plan_start_year + 5), name="fiscal_year"),
)

CURRENT_FY_ESTIMATE = 72594000
```

```python
FYP
```

```python
def get_final_dataframe(forecast, budget):
    final = pd.concat(
        [forecast.rename("Controller"), budget.rename("Five Year Plan")], axis=1
    )

    final.loc[plan_start_year - 1, :] = CURRENT_FY_ESTIMATE
    final["Five Year Plan"] = final["Five Year Plan"].fillna(final["Controller"])

    return final
```

```python
final = get_final_dataframe(FORECAST, FYP)
```

```python
final.head() / 1e6
```

```python
final.tail() / 1e6
```

Save the result:

```python
final.to_excel(
    SRC_DIR / ".." / ".." / "data" / "06_model_output" / "soda-forecast.xlsx"
)
```

Plot:

```python
comparison = final.copy()

# Put into millions
for col in comparison:
    comparison[col] /= 1e6

# Columns
col = "Controller"
start_year = 2017

# Plot
with plt.style.context(get_theme()):

    fig, ax = plt.subplots(
        figsize=(6, 2.5), gridspec_kw=dict(bottom=0.17, left=0.12, top=0.88, right=0.95)
    )

    colors = get_default_palette()
    kws = dict(
        lw=3,
        mew=2,
        alpha=0.9,
    )

    # Plot vertical line
    this_year = plan_start_year - 1
    ax.axvline(x=this_year, c=colors["dark-gray"], lw=3)

    # Plot historic
    color = colors["medium-gray"]
    comparison[col].loc[start_year:this_year].plot(
        ax=ax,
        marker="o",
        color=color,
        mec=color,
        mfc="white",
        label="",
        clip_on=False,
        **kws,
    )

    F = comparison.loc[this_year:].copy()

    # Plot Controller
    color = colors["blue"]
    F["Controller"].plot(
        ax=ax,
        marker="o",
        color=color,
        mec=color,
        mfc="white",
        label="Per Controller",
        clip_on=False,
        **kws,
    )

    # Plot Mayor
    color = colors["green"]
    F["Five Year Plan"].plot(
        ax=ax,
        marker="o",
        color=color,
        mec=color,
        mfc="white",
        label="Per Five Year Plan",
        clip_on=False,
        **kws,
    )

    ax.set_xlabel("Fiscal Year", fontsize=11)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([f"${x:,.0f}M" for x in ax.get_yticks()], fontsize=11)

    ax.set_xlim(start_year, plan_start_year + 5)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels([f"{x:.0f}" for x in ax.get_xticks()])

    ax.legend(
        loc="lower center",
        bbox_transform=ax.transAxes,
        bbox_to_anchor=(0.5, 0.98),
        ncol=2,
        fontsize=11,
    )

    plt.savefig(
        SRC_DIR
        / ".."
        / ".."
        / "data"
        / "06_model_output"
        / "forecast_figures"
        / "Soda.png"
    )

    plt.show();
```

```python

```

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
    [68938000, 69751000, 69053000, 68680000, 68385000],
    index=pd.Index(range(plan_start_year, plan_start_year + 5), name="fiscal_year"),
)
```

```python
FYP
```

```python
def get_final_dataframe(forecast, budget):
    final = pd.concat(
        [forecast.rename("Controller"), budget.rename("Five Year Plan")], axis=1
    )

    final.loc[2023, :] = 68087000
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

Make the future forecast through the end of the Plan:

```python
# Get the forecast period
freq = "M"
forecast_stop_date = "2027-06-30"
periods = (
    pd.to_datetime(forecast_stop_date).to_period(freq) - df["ds"].max().to_period(freq)
).n
future = model.make_future_dataframe(periods=periods + 24, freq=f"{freq}S")
```

```python
future.tail()
```

Run the forecast:

```python
# Forecast
forecast = model.predict(future)
```

Calculate fiscal year growth rates:

```python
fy_forecast = aggregate_to_fiscal_year(forecast.set_index("ds")["yhat"], freq="MS")
```

```python
growth_rates = 100 * (fy_forecast.diff() / fy_forecast.shift())

growth_rates
```

## Generate a "no-growth" baseline

Repeat the pre-COVID data for each year in the forecast period

```python
def project_flat_growth(X, start="2019-04", stop="2020-03"):
    """Normalize future growth to be flat at the last annual period."""
    # Make a copy first
    X = X.copy()
    freq = X.index.inferred_freq
    X.index.freq = freq

    # This is the part that will be projected
    norm = X.loc[start:stop].copy()
    latest_date = norm.index[-1]

    # This should be monthly or quarterly
    assert len(norm) in [4, 12]
    if len(norm) == 4:
        key = lambda dt: dt.quarter
    else:
        key = lambda dt: dt.month

    # Reset the index to months/quarters
    norm.index = [key(dt) for dt in norm.index]

    # Change the forecast to be flat
    forecast_start = latest_date + latest_date.freq
    Y = X.loc[forecast_start:].copy()

    # Reset index
    i = Y.index
    Y.index = [key(dt) for dt in Y.index]

    # Overwrite
    Y.loc[:] = norm.loc[Y.index].values
    Y.index = i

    # Add back to original
    X.loc[Y.index] = Y.values

    return X
```

```python
forecast = (
    forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
            "yearly",
            "trend",
        ]
    ]
    .rename(
        columns={
            "ds": "date",
            "yhat": "total",
            "yhat_lower": "lower",
            "yhat_upper": "upper",
        }
    )
    .set_index("date")
)
```

```python
flat_forecast = project_flat_growth(forecast)
```

## Examine recovery so far

Use the actual data to see how collections have responded since COVID

```python
ratios = (soda_tax["total"] / flat_forecast["total"]).dropna()
```

```python
ratios.loc["2020":]
```

## Set up future recovery

**Assumptions**

- A two-year recovery period
- After this period, growth rates is assumed to be -1%
- Permanent loss of 1% to the overall base


Set up the monthly dates for the two different forecast periods:

```python
future_dates_1 = pd.date_range("2021-07-01", "2023-06-30", freq="MS")
future_dates_2 = pd.date_range("2023-07-01", "2027-06-30", freq="MS")
```

```python
LIMIT = 0.99
```

```python
future_ratios_1 = pd.Series(
    [0.9] * 3 + [0.925] * 3 + [0.95] * 6 + [0.97] * 6 + [LIMIT] * 6,
    index=future_dates_1,
)
future_ratios_2 = pd.Series(
    [LIMIT * 0.99] * 12
    + [LIMIT * 0.99**2] * 12
    + [LIMIT * 0.99**3] * 12
    + [LIMIT] * 12,
    index=future_dates_2,
)
```

Plot the recovery:

```python
pd.concat([future_ratios_1, future_ratios_2]).plot()
```

Calculate the final forecast by re-scaling the flat forecast with our future ratios:

```python
# Get the baseline forecast
F = flat_forecast["total"].copy()
actuals = df.set_index("ds")["y"]
F = pd.concat([F.loc["2021-07-01":], actuals])

# 2-year recovery period
inter = F.index.intersection(future_ratios_1.index)
F.loc[inter] *= future_ratios_1.loc[inter].values

# -1% growth rate period
inter = F.index.intersection(future_ratios_2.index)
F.loc[inter] *= future_ratios_2.loc[inter].values
```

The final fiscal year forecast:

```python
FORECAST = aggregate_to_fiscal_year(F, freq="MS").squeeze()
```

```python
FORECAST / 1e6
```

Growth rates:

```python
(FORECAST.diff() / FORECAST.shift()).dropna()
```

## Compare to Five Year Plan and save

Five Year Plan numbers from Adopted FY22-FY26 Plan:

```python
FYP = pd.Series(
    [72515000, 76888000, 76311000, 75739000, 75171000],
    index=pd.Index(range(2022, 2022 + 5), name="fiscal_year"),
)
```

```python
FY21_ESTIMATE = 63013000  # From Adopted Plan
```

```python
def get_final_dataframe(forecast, budget):
    final = pd.concat(
        [forecast.rename("Controller"), budget.rename("Five Year Plan")], axis=1
    )

    final.loc[2021, :] = FY21_ESTIMATE
    final["Five Year Plan"] = final["Five Year Plan"].fillna(final["Controller"])

    return final
```

```python
final = get_final_dataframe(FORECAST, FYP)
```

```python
final.head()
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
    ax.axvline(x=this_year, c=colors["dark-grey"], lw=3)

    # Plot historic
    color = colors["medium-grey"]
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

    ax.set_xlim(start_year, plan_start_year + 4)
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
```

```python

```

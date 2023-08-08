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

# Revenue Modeling: RTT


**Purpose:** This notebook models realty transfer tax revenue by modeling number of sales and price per sale for residential and non-residential sectors using an ARIMA model. 


```python
import carto2gpd
import pandas as pd
from matplotlib import pyplot as plt
from phila_style.core import *
from phila_style.matplotlib import get_theme
```

```python
# Prediction functions
from fyp_analysis import SRC_DIR
from fyp_analysis.extras.datasets import PlanDetails, Taxes, load_cbo_data
from fyp_analysis.pipelines.modeling.predict import (
    aggregate_to_fiscal_year,
    get_forecasts_from_fits,
    plot_projection_comparison,
)
```

```python
DATA_DIR = SRC_DIR / ".." / ".." / "data"
```

```python
pd.options.display.max_columns = 999
```

```python
# Total by fiscal year
def get_fy_total(df):

    total_fy = df.copy().reset_index()
    total_fy["fiscal_year"] = [dt.year for dt in df.index.shift(2, freq="QS")]
    return total_fy.groupby("fiscal_year")["total"].sum()
```

```python
palette = get_default_palette()
```

```python
TAX_NAME = "RTT"
TAX_BASE_COLUMN = f"{TAX_NAME}Base"
```

```python
%reload_kedro
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

##  Data Processing


### Load revenue report data

```python
collections = pd.read_csv(
    "https://raw.githubusercontent.com/PhilaController/phl-budget-data/main/src/phl_budget_data/data/processed/collections/rtt-collections-by-sector.csv"
).assign(date=lambda df: pd.to_datetime(df.date))
```

Calculate residential/nonresidential totals

```python
collections_r = (
    collections.query("category == 'Residential'")
    .pivot_table(index="date", columns="variable", values="value")
    .assign(total_per_record=lambda df: df.total / df.num_records)
)
```

```python
collections_nr = (
    collections.query("category == 'Nonresidential'")
    .pivot_table(index="date", columns="variable", values="value")
    .assign(total_per_record=lambda df: df.total / df.num_records)
)
```

```python
collections_all = (
    collections.query("category == 'Total'")
    .pivot_table(index="date", columns="variable", values="value")
    .assign(total_per_record=lambda df: df.total / df.num_records)
)
```

### Load RTT data 

Source: https://opendataphilly.org/datasets/real-estate-transfers/

```python
# Load the full transfers dataset
rtt = pd.read_csv(
    DATA_DIR / "01_raw/historical/rtt/rtt_summary.csv",
    dtype={"document_id": str, "opa_account_num": str},
)

# Convert the dates
for col in ["display_date", "recording_date", "receipt_date"]:
    rtt[col] = pd.to_datetime(rtt[col], errors="coerce").dt.tz_localize(None)

# Trim to deeds
deed_types = [
    "DEED",
    "DEED SHERIFF",
    "DEED MISCELLANEOUS TAXABLE",
    "CERTIFICATE OF STOCK TRANSFER",
]

# Drop things that aren't taxed and only keep one per transaction
deeds = (
    rtt.query("document_type in @deed_types")
    .dropna(subset=["local_tax_amount"])
    .drop_duplicates(subset=["document_id"])
)
```

```python
# Load opa data
opa = carto2gpd.get(
    "https://phl.carto.com/api/v2/sql",
    table_name="opa_properties_public",
    fields=[
        "parcel_number",
        "category_code_description",
        "category_code",
        "building_code_description",
    ],
)
```

```python
tmp = deeds.merge(
    opa[
        [
            "parcel_number",
            "category_code_description",
            "category_code",
            "building_code_description",
        ]
    ],
    left_on="opa_account_num",
    right_on="parcel_number",
    how="left",
).assign(parcel_type=lambda df: df.parcel_number.str.slice(0, 3))
```

```python
pattern = "|".join([f"{x:02d}" for x in range(1, 77)]) + "|888|881"
residential_sel = (
    tmp["parcel_type"].str.match(f"^({pattern})", na=False)
    | tmp["parcel_number"].isnull()
)

deeds_r = tmp.loc[residential_sel]
deeds_nr = tmp.loc[~residential_sel]
```

```python
def calculate_tax_from_deeds(df, start_date="2000", end_date="2022"):
    """Calculate quarterly tax amount from deeds."""

    g = df.groupby(pd.Grouper(key="recording_date", freq="QS"))

    return (
        pd.concat(
            [
                g.size().rename("num_records"),
                g["local_tax_amount"].sum().rename("total"),
            ],
            axis=1,
        )
        .assign(total_per_record=lambda df: df.total / df.num_records)
        .rename_axis("date", axis=0)
        .loc[start_date:end_date]
    )
```

```python
transfer_tax_r = calculate_tax_from_deeds(deeds_r)
transfer_tax_nr = calculate_tax_from_deeds(deeds_nr)
```

```python
# IMPORTANT:

# Copy over from this date
start_fiscal_year = 2018
start_date = f"{start_fiscal_year-1}-07-01"

# Copy collections data from revenue reports
for q in collections_nr.loc[start_date:].index:
    transfer_tax_nr.loc[q] = collections_nr.loc[q]

for q in collections_r.loc[start_date:].index:
    transfer_tax_r.loc[q] = collections_r.loc[q]
```

### Check Totals

```python
get_fy_total(collections_all) / 1e6
```

```python
(get_fy_total(transfer_tax_nr) + get_fy_total(transfer_tax_r)) / 1e6
```

## Residential

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_r.plot(y="num_records", legend=False, clip_on=False, marker="o")
    ax.set_title("Number of Residential Sales")
    plt.show()
```

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_r.plot(y="total", legend=False, clip_on=False, marker="o")
    ax.set_title("Total Residential Revenue")
    plt.show()
```

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_r.plot(
        y="total_per_record", legend=False, clip_on=False, marker="o"
    )
    ax.set_title("Total Residential Revenue Per Sale")

    plt.show();
```

## Nonresidential

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_nr.plot(
        y="num_records",
        legend=False,
        clip_on=False,
        marker="o",
        color=palette["red"],
    )
    ax.set_title("Number of Nonresidential Sales")
    plt.show();
```

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_nr.plot(
        y="total",
        legend=False,
        clip_on=False,
        marker="o",
        color=palette["red"],
    )
    ax.set_title("Total Nonresidential Revenue")
    plt.show();
```

```python
with plt.style.context(get_theme()):
    ax = transfer_tax_nr.plot(
        y="total_per_record",
        legend=False,
        clip_on=False,
        marker="o",
        color=palette["red"],
    )
    ax.set_title("Total Nonresidential Revenue Per Sale")
    plt.show();
```

## Analysis

```python
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
```

```python
cbo = pd.read_csv("../../data/01_raw/cbo/2023-02-economic-projections.csv").assign(
    date=lambda df: pd.to_datetime(df.date)
)
```

```python
def get_forecast(
    data,
    column,
    covid_dates=[("2020-04-01", "2020-04-01"), ("2021-01-01", "2021-07-01")],
    abatement_dates=[("2021-10-01", "2022-07-01")],
    cbo_regressor=None,
    **fit_kwargs,
):

    # Forecast end date
    forecast_end_date = f"{PARAMS['plan_start_year']+4}-06-30"

    if cbo_regressor is not None:
        if isinstance(cbo_regressor, str):
            cbo_regressor = [cbo_regressor]
    else:
        cbo_regressor = []

    # Format the input data
    df = (
        data.set_index("date")[column]
        .rename_axis("ds")
        .reset_index()
        .rename(columns={column: "y"})
        .sort_values("ds")
        .assign(ds=lambda df: df.ds.dt.tz_localize(None))
    )

    # Create lockdowns
    lockdowns = []
    for i, dates in enumerate(covid_dates, start=1):
        lockdowns.append(
            {
                "holiday": f"covid_{i}",
                "ds": dates[0],
                "lower_window": 0,
                "ds_upper": dates[1],
            }
        )
    for i, dates in enumerate(abatement_dates, start=1):
        lockdowns.append(
            {
                "holiday": f"abatement_{i}",
                "ds": dates[0],
                "lower_window": 0,
                "ds_upper": dates[1],
            }
        )
    if len(lockdowns):
        lockdowns = pd.DataFrame(lockdowns)
        for t_col in ["ds", "ds_upper"]:
            lockdowns[t_col] = pd.to_datetime(lockdowns[t_col])
        lockdowns["upper_window"] = (lockdowns["ds_upper"] - lockdowns["ds"]).dt.days

    def cbo_regressor_func(ds, cbo_indicator):
        """Custom regressor function"""
        if ds in cbo_indicator.index:
            return cbo_indicator.loc[ds]
        else:
            return 0

    # CBO regressor
    for col in cbo_regressor:
        df[col] = df["ds"].apply(
            cbo_regressor_func, args=(cbo.set_index("date")[col].dropna().squeeze(),)
        )

    if len(lockdowns):
        model = Prophet(holidays=lockdowns, **fit_kwargs)
    else:
        model = Prophet(**fit_kwargs)
    for col in cbo_regressor:
        model.add_regressor(col)
    model.fit(df)

    forecast_period = (
        pd.Timestamp(forecast_end_date).to_period(freq="Q")
        - df["ds"].max().to_period(freq="Q")
    ).n

    future = model.make_future_dataframe(periods=forecast_period, freq="QS")
    for col in cbo_regressor:
        future[col] = future["ds"].apply(
            cbo_regressor_func, args=(cbo.set_index("date")[col].dropna().squeeze(),)
        )

    forecast = model.predict(future)
    return model, forecast
```

### Residential

```python
res = transfer_tax_r.reset_index()
```

```python
model, residential_sales = get_forecast(
    res,
    "num_records",
    cbo_regressor="real_res_fixed_invest",
    covid_dates=[("2020-04-01", "2020-04-01"), ("2021-01-01", "2021-04-01")],
    abatement_dates=[("2021-10-01", "2023-01-01")],
)
fig = model.plot(residential_sales)
plt.show();
```

```python
model, residential_prices = get_forecast(
    res,
    "total_per_record",
    cbo_regressor="house_price_index_fhfa",
    covid_dates=[("2021-10-01", "2021-10-01")],
    abatement_dates=[("2022-07-01", "2023-01-01")],
)
model.plot(residential_prices)
plt.show();
```

```python
R = (
    residential_prices.set_index("ds")["yhat"]
    * residential_sales.set_index("ds")["yhat"]
)

R / 1e6
```

### Nonresidential

```python
nonres = transfer_tax_nr.reset_index()
```

```python
model, nonresidential_sales = get_forecast(
    nonres,
    "num_records",
    covid_dates=[("2020-04-01", "2021-04-01")],
    abatement_dates=[("2022-01-01", "2022-07-01")],
    cbo_regressor="real_res_fixed_invest",
)
model.plot(nonresidential_sales)
plt.show();
```

```python
model, nonresidential_prices = get_forecast(
    nonres,
    "total_per_record",
    covid_dates=[("2020-04-01", "2020-04-01"), ("2021-01-01", "2021-04-01")],
    abatement_dates=[("2021-10-01", "2022-04-01")],
    cbo_regressor=None,
)
model.plot(nonresidential_prices)
plt.show();
```

```python
NR = (
    nonresidential_prices.set_index("ds")["yhat"]
    * nonresidential_sales.set_index("ds")["yhat"]
)

NR / 1e6
```

### Total

```python
quarterly_revenue = R + NR
```

```python
R.loc["2022-07":"2023-04"] / 1e6
```

```python
NR.loc["2022-07":"2023-04"] / 1e6
```

```python
quarterly_revenue.loc["2022-07":"2023-04"] / 1e6
```

```python
revenue_by_fy = (
    aggregate_to_fiscal_year(quarterly_revenue)
    .rename(columns={"total": TAX_BASE_COLUMN})
    .squeeze()
)

(revenue_by_fy / 1e6).tail(8)
```

```python
revenue_by_fy.diff() / revenue_by_fy.shift()
```

```python
tax_base_by_fy = (
    (revenue_by_fy / this_tax.rates.set_index("fiscal_year")["rate"])
    .dropna()
    .rename(TAX_BASE_COLUMN)
)
```

```python
tax_base_by_fy
```

```python
plot_projection_comparison(this_tax, tax_base_by_fy)
plt.show();
```

```python
DATA.save("rtt_tax_base_forecast", tax_base_by_fy)
```

```python

```

```python

```

```python

```

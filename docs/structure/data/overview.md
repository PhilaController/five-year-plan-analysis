# The data/ Folder

The `data/` folder holds the various data inputs and outputs from the analysis
pipelines. There is a specific folder to hold the raw input data (e.g.,
historical tax revenues and economic indicators), as well as folders to hold
intermediate data products and modeling results.

## Data Layers 

The `data/` folder follows the data engineering syntax used by the `kedro`
package, which specifies a way of organizing data into layers. The data layers
are:

![](/assets/img/kedro-data-layers.png)

**Note:** We are not using the "primary" data layer in this analysis.

There are three folders associated with the `data processing` pipeline:

- `01_raw`: The raw data files that serve as the starting point for the
  analysis. This is the ground truth data that should not be modified by the
  analysis in any way.
- `02_intermediate`: Intermediate data products produced by the data processing
  pipeline.
- `03_feature`: The final unscaled and scaled versions of the features that
  will be input into the modeling pipeline.

There are four folders associated with the `modeling` pipeline:

- `04_model_input`: Data, other than the features, that is input into the
  modeling pipeline.
- `05_models`: Regression models.
- `06_model_output`: Files output by the regression models.
- `07_reporting`: Files for reporting final results.

## Raw Data

There are four folders in the [`01_raw` folder](https://github.com/PhilaController/five-year-plan-analysis/tree/main/data/01_raw):

- `cbo`: CBO 10-year economic projection spreadsheets
- `historical`: Historical tax rates and revenue data
- `indicators`: The economic indicator data
- `plans`: The data from the Five Year Plan, e.g., projected revenues and rates
  over the Plan; this comes in two flavors: the "proposed" and the "adopted"
  versions

### Historical Data Files

The `data/01_raw/historical/` folder contains the historical data necessary for
the analysis. In particular, there is historical tax revenue data, tax rate
data, and data related to the breakdown of the net income and gross receipt
portions of BIRT. 

#### Revenues

In the `data/01_raw/historical/revenues/` folder
([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/historical/revenues)),
there are spreadsheets holding the annual and quarterly tax revenue data:

- [Annual.xlsx](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/01_raw/historical/revenues/Annual.xlsx)
- [Quarterly.xlsx](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/01_raw/historical/revenues/Quarterly.xlsx)

The quarterly data file is the main input data file required for the analysis.
The annual file is not required for the analysis but useful for tracking the
audited annual totals for each tax. Each year, these data files need to be
updated with the latest historical data. See the [update
usage instructions](../../../usage/updates) for more information.

!!! warning

    The data for Wage & Earnings Tax and the Net Profits Tax are for the current year
    only (excludes prior year totals). This will be important when updating 
    the historical data files. 


#### Rates

The `data/01_raw/historical/rates/` folder
([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/historical/rates))
contains a CSV file for each tax that contains the historical tax rate for each
fiscal year.

This does not contain any projected rates, only historical. Each year the rate
for the latest fiscal year should be added to each of the files.


#### BIRT Splits

The analysis requires the historical breakdown between the net income and gross
receipts portion of BIRT. The information for the latest fiscal year can be
obtained by the BIRT revenue model sent over by the Budget Office each year.


### Indicators

The raw economic indicators are stored in the `data/01_raw/indicators/` folder
([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/indicators)).
Other than the historical tax revenue data, this is the main source of input
data for the analysis.

### CBO

The 10-year economic projections [from the
CBO](https://www.cbo.gov/data/budget-economic-data#4) are stored in this
folder. The CBO data variables are used as exogenous variables in the
regression modeling.

### Plans

The `data/01_raw/plans/` folder
([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/plans))
holds the Five Year Plan projection information for revenues and rates. There
should be separate files for the proposed and adopted versions of the Plan. 


!!! note
    For more information on these files, see the [Plan Details
    section](../plan_details).

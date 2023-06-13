# Updating Data Sources

This section describes how to update the necessary data files each year
in order to run a fresh analysis.

## Quarterly Taxes

The [`Quarterly.xlsx`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/01_raw/historical/revenues/Quarterly.xlsx) file in the `data/01_raw/historical/revenues/` folder holds the 
quarterly tax revenues since 1996. The data file has a separate sheet
for the following taxes:

- Wage & Earnings (**Current Year Only**)
- Sales
- BIRT
- Realty Transfer
- Net Profits (**Current Year Only**)
- Parking 
- Amusement

```eval_rst
.. warning::
    Note that the Wage & Earnings and Net Profits taxes are for the 
    current year only (not total collections).
```

Each sheet includes detailed instructions about how to update the 
data. In general, the steps involved are:

1. Update the `Latest Collections Data` to get the latest actual collections data for each quarter from monthly collections reports from the Revenue Department.
1. For each sheet, use the `Latest Collections Data` totals to update
actual quarterly collections.
1. Use the latest annual [Supplemental Report of Revenues and Obligations](https://www.phila.gov/departments/office-of-the-director-of-finance/financial-reports/#/supplemental-report-of-revenues-and-obligations) to 
get the audited annual total for each tax. The historical Supplemental reports available in the `references/supplementals/` folder.
1. Given the annual total and quarterly values, update each sheet so the accrual value is automatically determined.
1. For the current fiscal year, the Q4 collections values are still projected. 
Use the Budget Office's projection for the annual total and the fiscal-year-to-date collections totals to impute a Q4 collections value.

### Getting the Latest Collections Data

We can automatically pull the latest actual collections data using the following command:

```
fyp-analysis update-quarterly-collections
```

This command relies on the [`phl-budget-data`](https://github.com/PhiladelphiaController/phl-budget-data) package to pull the latest collections data from the Revenue Department's monthly reports. The command will automatically aggregate the monthly 
data to quarters and update the `Latest Collections Data` sheet of the [`Quarterly.xlsx`](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/01_raw/historical/revenues/Quarterly.xlsx) file in the `data/01_raw/historical/revenues/` folder.


## Plan Details

Details about the five-year projected tax revenues and rates are stored 
in YAML files in the `data/01_raw/plans/` folder ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/plans)). 

Creating these YAML files for each new Plan is one of the main tasks that must be completed
before the analysis begins. A separate file should be created for the original proposal
and for the adopted version of the Plan.

This section describes how to create these files. The majority of information comes from the 
revenue spreadsheet models sent over by the Budget Office during each Plan analysis. 

```eval_rst
.. note::
    The YAML file must follow the schema outlined `here <plan_details.html#schema>`__.
```

### Revenues

For all taxes except for Sales, revenue totals can be obtained from the Supporting 
Revenue Schedule spreadsheet, typically named e.g., `FYXX-YY Revenues - Taxes.xlsx`
that is sent over from Budget. This spreadsheet includes revenue totals for each 
year of the Plan.

![Example Revenue Schedule for Five Year Plan](/_static/img/revenue-schedule-example.png)

```eval_rst
.. warning::
    The "Wage" line in the YAML file refers to the Current Year Wage & Earnings line.

    The "NPT" line in the YAML file refers to the Current Year Net Profits tax.
```

For the Sales tax, you must pull the **total City & School District** revenue totals from 
the Sales Tax revenue spreadsheet sent over by Budget. The file is typically named 
`FYXX-YY Sales Tax Model.xlsx`. See the highlighted line (a) below.

![Example Sales Tax Schedule for Five Year Plan](/_static/img/sales-tax-example.png)

### Rates

Tax rates can be obtained from the large Five Year Plan proposal document. Typically, 
any changes to tax rates are emphasized in the Plan documents. 

Generally, the Wage & Earnings and BIRT rates are the tax rates that change
over the life of the Plan. You can obtain these rates from the revenue spreadsheets 
sent over by Budget. 

In the Wage Tax model (typically named `FYXX-YY Wage Tax Model.xlsx`):

![Wage Tax Rates for Five Year Plan](/_static/img/wage-rates-example.png)

In the BIRT model (typically named `FYXX-YY BPT Model.xlsx` for "Business Privilege Tax"):

![BIRT Rates for Five Year Plan](/_static/img/birt-rates-example.png)


```eval_rst
.. note::
    The Net Profits tax uses the same tax rates (resident and non-resident) as the 
    Wage & Earnings taxes.
```

### Resident Fractions

The Budget Office assumption for the resident/non-resident splits for the Wage & Earnings
and Net Profits taxes can be found in the Wage Tax spreadsheet. These are assumed 
to be constant over the 5 years of the Plan.

![Resident/Non-residents Splits for Wage & NPT](/_static/img/resident-splits.png)

### Net Income Fraction

The Budget Office assumption for the amount of BIRT revenue from the net income 
portion can be found in the BIRT spreadsheet. The fraction changes over the life of 
the Plan.

![Net Income Fraction for BIRT](/_static/img/net-income-fraction-example.png)


## Economic Indicators

The economic indicators are stored locally in the `data/01_raw/indicators/` folder. The 
data is automatically downloaded as part of the data processing pipeline
in the analysis. To get a fresh copy of the indicators downloaded locally, you 
can change the `fresh_indicators` parameter in the `conf/base/parameters/data_processing.yml`
file to `True`. This will download the latest version of all indicators.

You can also set the `fresh_indicators` parameter to `True` when running the
data processing pipeline (see the run instructions [here](../03_processing/overview#running-the-pipeline)).

```
fyp-analysis run --pipeline dp --params fresh_indicators:True
```


# Updating Data Sources

This section describes how to update the necessary data files each year
in order to run a fresh analysis.

## Steps

### 1. Get the latest annual supplemental report

Get the most recent Supplemental Report of Revenues and Obligations. It should be available either on the [Finance Department's website](https://www.phila.gov/departments/office-of-the-director-of-finance/financial-reports/#/) or you can ask the Audit Division for it. Place it in `references/supplementals/`.

### 2. Update annual revenue file

Using the latest Supplemental report, ddd the latest fiscal year revenue totals to "Annual.xlsx" in `/data/01_raw/historical/revenues/`.

### 3. Pull the latest quarterly collection numbers

The City releases monthly reports on collections on the [Revenue Department's website](https://www.phila.gov/departments/department-of-revenue/reports/). The analysis code needs the latest collection numbers for the major taxes. These can be pulled by running:

```
poetry run fyp-analysis-update
```

### 4. Update quarterly revenue file

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

!!! warning
    Note that the Wage & Earnings and Net Profits taxes are for the 
    current year only (not total collections).

!!! note
    The sheet entitled `Latest Collections Data` contains the actual collections data for each quarter from monthly collections reports from the Revenue Department. If you succeeded in running the last step, it should be updated to show the latest numbers.

Each sheet includes detailed instructions about how to update the 
data. In general, the steps involved are:

1. For each sheet, use the `Latest Collections Data` totals to update actual quarterly collections.
1. Use the latest annual [Supplemental Report of Revenues and Obligations](https://www.phila.gov/departments/office-of-the-director-of-finance/financial-reports/#/supplemental-report-of-revenues-and-obligations) to 
get the audited annual total for each tax. The historical Supplemental reports available in the `references/supplementals/` folder.
1. Given the annual total and quarterly values, update each sheet so the accrual value is automatically determined.
2. For the current fiscal year, the Q4 collections values are still projected. Use the Budget Office's projection for the annual total and the fiscal-year-to-date collections totals to impute a Q4 collections value.

### 5. Update actual tax rates

Add the actual tax rates for the current fiscal year for each 
tax file in the `/data/01_raw/historical/rates` folder. The tax rates for the historical wage & BIRT rates can be obtained from the model spreadsheets that the Budget Office sends over.

!!! note
    These folders should not contain any **projected** tax rates.
    Those go in the file specifiying the plan details (see step #8).

### 6. Update BIRT splits

Copy over latest actual fiscal year data from the BIRT model spreadsheet (from Budget Office) to the `data/01_raw/historical/BIRT-splits.xlsx` file. This specifies how much of BIRT comes 
from the net income portion.

### 7. Pull the latest CBO forecast. 

The latest CBO forecast is used to help constrain future forecasts. To get the latest forecast, see the "Historical Data and Economic Projections" section at [https://www.cbo.gov/data/budget-economic-data](https://www.cbo.gov/data/budget-economic-data). 

Get the quarterly CSV forecast file and place it in the `data/01_raw/cbo/` and be sure to follow the same naming convention to denote which month/year the forecast is from.

### 8. Create a new file with Plan Details

Details about the five-year projected tax revenues and rates are stored 
in YAML files in the `data/01_raw/plans/` folder ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/plans)). 

Creating these YAML files for each new Plan is one of the main tasks that must be completed
before the analysis begins. A separate file should be created for the original proposal
and for the adopted version of the Plan.

This section describes how to create these files. The majority of information comes from the 
revenue spreadsheet models sent over by the Budget Office during each Plan analysis. 



#### Revenues

For all taxes except for Sales, revenue totals can be obtained from the Supporting 
Revenue Schedule spreadsheet, typically named e.g., `FYXX-YY Revenues - Taxes.xlsx`
that is sent over from Budget. This spreadsheet includes revenue totals for each 
year of the Plan.

![Example Revenue Schedule for Five Year Plan](/assets/img/revenue-schedule-example.png)

!!! warning
    The "Wage" line in the YAML file refers to the Current Year Wage & Earnings line.
    The "NPT" line in the YAML file refers to the Current Year Net Profits tax.


For the Sales tax, you must pull the **total City & School District** revenue totals from 
the Sales Tax revenue spreadsheet sent over by Budget. The file is typically named 
`FYXX-YY Sales Tax Model.xlsx`. See the highlighted line (a) below.

![Example Sales Tax Schedule for Five Year Plan](/assets/img/sales-tax-example.png)


#### Rates 

The projected tax rates in the Plan can be obtained from the large Five Year 
Plan proposal document. Typically, any changes to tax rates are emphasized in the Plan documents. 

Generally, the Wage & Earnings and BIRT rates are the tax rates that change
over the life of the Plan. You can obtain these rates from the revenue spreadsheets 
sent over by Budget. 

In the Wage Tax model (typically named `FYXX-YY Wage Tax Model.xlsx`):

![Wage Tax Rates for Five Year Plan](/assets/img/wage-rates-example.png)

In the BIRT model (typically named `FYXX-YY BPT Model.xlsx` for "Business Privilege Tax"):

![BIRT Rates for Five Year Plan](/assets/img/birt-rates-example.png)


!!! note
    The Net Profits tax uses the same tax rates (resident and non-resident) as the 
    Wage & Earnings taxes.


#### Resident Fractions

The Budget Office assumption for the resident/non-resident splits for the Wage & Earnings
and Net Profits taxes can be found in the Wage Tax spreadsheet. These are assumed 
to be constant over the 5 years of the Plan.

![Resident/Non-residents Splits for Wage & NPT](/assets/img/resident-splits.png)

#### Net Income Fraction

The Budget Office assumption for the amount of BIRT revenue from the net income 
portion can be found in the BIRT spreadsheet. The fraction changes over the life of 
the Plan.

![Net Income Fraction for BIRT](/assets/img/net-income-fraction-example.png)


### 9. Update the economic indicators

The economic indicators are stored locally in the `data/01_raw/indicators/` folder. The 
data is automatically downloaded as part of the data processing pipeline
in the analysis. 
To get a fresh copy of the indicators downloaded locally, you 
can set the `fresh_indicators` parameter to `True` and run the data processing 
pipeline using:

```
poetry run fyp-analysis-run --pipeline dp --params fresh_indicators:True
```

This will download and store the latest version of all indicators.


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
1. Use the latest annual Supplemental Report of Revenues and Obligations to 
get the audited annual total for each tax. The historical Supplemental reports available in the `references/supplementals/` folder.
1. Given the annual total and quarterly values, update each sheet so the accrual value is automatically determined.
1. For the current fiscal year, the Q4 collections values are still projected. 
Use the Budget Office's projection for the annual total and the fiscal-year-to-date collections totals to impute a Q4 collections value.

### Getting the Latest Collections Data

We can automatically pull the latest actual collections data using the following command:

```
```


## Plan Details

## Economic Indicators
# The Plan Details

Details about the five-year projected tax revenues and rates are stored 
in YAML files in the `data/01_raw/plans/` folder ([link](https://github.com/PhiladelphiaController/five-year-plan-analysis/tree/main/data/01_raw/plans)).
For a given plan, there should be a separate file for the proposed 
and adopted versions of the Plan.

There is a specific schema that must be used. See an example YAML file [here](https://github.com/PhiladelphiaController/five-year-plan-analysis/blob/main/data/01_raw/plans/FY22-FY26-Proposed.yml). This file looks like this:

```yaml
kind: Proposed
fiscal_years: [2022, 2023, 2024, 2025, 2026]
revenues:
    Amusement: [12963000, 19657000, 20414000, 21231000, 22063000]
    BIRT: [515503000, 529269000, 545311000, 557186000, 563243000]
    NPT: [25454000, 27282000, 29097000, 31036000, 33265000]
    Parking: [56429000, 73662000, 76837000, 79949000, 83107000]
    RTT: [294859000, 295832000, 304884000, 315281000, 326095000]
    Sales: [336886195, 346319008, 358682597, 372204931, 385678749]
    Wage: [1544731000, 1616891000, 1685156000, 1761687000, 1837646000]
rates:
    Amusement: [5.0, 5.0, 5.0, 5.0, 5.0]
    BIRT:
        gross_receipts: [0.1415, 0.1415, 0.1415, 0.1415, 0.1415]
        net_income: [6.10, 6.00, 5.75, 5.50, 5.25]
    NPT:
        resident: [3.8398, 3.8360, 3.8322, 3.8283, 3.8245]
        nonresident: [3.4201, 3.4167, 3.4133, 3.4099, 3.4065]
    Parking: [22.5, 22.5, 22.5, 22.5, 22.5]
    RTT: [3.278, 3.278, 3.278, 3.278, 3.278]
    Sales: [2.0, 2.0, 2.0, 2.0, 2.0]
    Wage:
        resident: [3.8398, 3.8360, 3.8322, 3.8283, 3.8245]
        nonresident: [3.4201, 3.4167, 3.4133, 3.4099, 3.4065]
resident_fractions:
    Wage: 62.4
    NPT: 47.2
net_income_fraction: [72.7, 72.3, 71.5, 70.6, 69.6]
```


!!! warning
    If the data in the YAML file does not match the schema, an error will be raised when the analysis runs.


## Schema

- **kind**: Either 'Proposed' or 'Adopted'
- **fiscal_years**: The fiscal years in the Plan (should be a list of length 5)
- **revenues:** The 5-year projected revenues for each tax: 
    - Amusement
    - BIRT
    - NPT
    - Parking
    - RTT
    - Sales
    - Wage
- **rates**: The 5-year projected tax rates for each tax
    - For `Wage` and `NPT`, you must specify the `resident` and `nonresident` rates
    - For `BIRT`, you must specify the `net_income` and `gross_receipts` rates
- **resident_fractions**: The fraction of the tax base from residents for the 
Wage and Net Profits taxes
- **net_income_fraction**: The fraction of the total BIRT revenues that 
come from the net income portion

!!! note
    For more information about how to create this file for a specific Plan year, 
    see the section on [updating data sources](../../usage/updates.md).

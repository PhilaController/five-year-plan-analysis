# Five Year Plan Revenue Projections

[![Documentation Status](https://readthedocs.org/projects/five-year-plan-analysis/badge/?version=latest)](https://five-year-plan-analysis.readthedocs.io/en/latest/?badge=latest)
      

The goal of the analysis is to produce revenue projections for the City of Philadelphia's major tax revenues 
as part of the Controller's Office review of the City's annual Five Year Plan. The tax revenues being
projected are:

- Wage & Earnings (Current Year Only)
- Business Income & Receipts (BIRT)
- Sales
- Realty Transfer
- Parking
- Amusement
- Net Profits (Current Year Only)

The analysis relies on quarterly revenue data since 1996 and uses 
[vector auto regression](https://en.wikipedia.org/wiki/Vector_autoregression) to make time-series projections. The steps involved in the analysis are:

1. Download latest economic indicator data. 
2. Preprocess economic indicators and tax revenue data to make data suitable to for time-series projections.
3. Calculate the [Granger causality](https://en.wikipedia.org/wiki/Granger_causality) matrix to determine which indicators should be used in the revenue forecasts. 
4. For each tax, use historical data to perform a brute-force grid search to identify the which regression parameters and indicators provide 
5. Perform final five-year projections for each tax and compare projections to the Budget Office projections.


## Installation

To get started, see the [installation instructions](https://five-year-plan-analysis.readthedocs.io/en/latest/01_getting_started/installation.html) in the documentation.
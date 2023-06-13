# Five Year Plan Revenue Analysis

[![github](https://img.shields.io/badge/Github-Launch-blue)](https://github.com/PhiladelphiaController/five-year-plan-analysis)

Welcome to the documentation for the City Controller's revenue analysis for the
Five Year Plan! 

The documentation outlines the steps involved in running the analysis to
produce revenue projections for the City of Philadelphia's major tax revenues.
These revenue projections are required as part of the Controller's Office
review of the City's annual Five Year Plan. 

The analysis code is written in Python and [is available on
Github](https://github.com/PhiladelphiaController/five-year-plan-analysis). It
produces projections for the following tax revenues:

- Wage & Earnings (Current Year Only)
- Business Income & Receipts (BIRT)
- Sales
- Realty Transfer
- Parking
- Amusement
- Net Profits (Current Year Only)
- Beverage


The analysis relies on quarterly revenue data since 1996 and uses [vector auto
regression](https://en.wikipedia.org/wiki/Vector_autoregression) to make
time-series projections. The regression incorporates the [CBO's latest 10-year
forecast](https://www.cbo.gov/data/budget-economic-data) as exogeneous
variables. The steps involved in the analysis are:

1. Download latest economic indicator data. 
2. Preprocess economic indicators and tax revenue data to make data suitable to
   for time-series projections.
3. Calculate the [Granger
   causality](https://en.wikipedia.org/wiki/Granger_causality) matrix to
   determine which indicators should be used in the revenue forecasts. 
4. For each tax, use historical data to perform a brute-force grid search to
   identify the which regression parameters and indicators provide the best
   accuracy. 
5. Perform final five-year projections for each tax and compare projections to
   the Budget Office projections.



## Get Started

- If this is your first time using the code, following the [installation
  instructions](./install).
- If you'd like to learn more about the structure of the code, check out the
  [usage section](./usage/overview).

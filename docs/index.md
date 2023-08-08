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


The analysis relies on quarterly revenue data since 1996 and uses either
[vector auto regression](https://en.wikipedia.org/wiki/Vector_autoregression)
via the [`statsmodels` package](https://www.statsmodels.org/stable/index.html)
or auto-regression via the [`prophet` package](https://facebook.github.io/prophet/) to make time-series projections.
In both cases, the regression forecasts incorporate the [CBO's latest 10-year
forecast](https://www.cbo.gov/data/budget-economic-data) as exogeneous
variables. 



## Get Started

- If this is your first time using the code, following the [installation
  instructions](./install).
- If you'd like to dive into using the code, check out the
  [usage section](./usage/overview).
- To learn more about the different steps involved in the analysis, check out the
  [code structure docs](./structure/overview).

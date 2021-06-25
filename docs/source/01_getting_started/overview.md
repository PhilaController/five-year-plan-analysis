# Overview

## Analysis

The goal of the analysis is to produce five-year projections for the City of Philadelphia's major tax revenues:

- Wage & Earnings
- Business Income & Receipts (BIRT)
- Sales
- Realty Transfer
- Parking
- Amusement
- Net Profits

The analysis relies on quarterly revenue data since 1996 and uses [vector auto regression](https://en.wikipedia.org/wiki/Vector_autoregression) to make time-series projections. The steps involved in the analysis are:

1. Download latest economic indicator data. 
1. Preprocess economic indicators and tax revenue data to make data suitable to for time-series projections.
1. Calculate the [Granger causality](https://en.wikipedia.org/wiki/Granger_causality) matrix to determine which indicators should be used in the revenue forecasts. 
1. For each tax, use historical data to perform a brute-force grid search to identify the which regression parameters and indicators provide 
1. Perform final five-year projections for each tax and compare projections to the Budget Office projections.



## Project Framework

Kedro is an open-source Python framework for creating reproducible, maintainable and modular data science code. It borrows concepts from software engineering best-practice and applies them to machine-learning code; applied concepts include modularity, separation of concerns and versioning.

For the source code, take a look at the [Kedro repository on Github](https://github.com/quantumblacklabs/kedro).

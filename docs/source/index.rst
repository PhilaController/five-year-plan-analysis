.. five_year_plan_analysis documentation master file, created by sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Five Year Plan Revenue Projections
==================================

.. image:: https://img.shields.io/badge/Github-Launch-blue
 :target: https://github.com/PhiladelphiaController/five-year-plan-analysis

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
`vector auto regression`_ to make time-series projections. The steps involved in the analysis are:

1. Download latest economic indicator data. 
2. Preprocess economic indicators and tax revenue data to make data suitable to for time-series projections.
3. Calculate the `Granger causality`_ matrix to determine which indicators should be used in the revenue forecasts. 
4. For each tax, use historical data to perform a brute-force grid search to identify the which regression parameters and indicators provide 
5. Perform final five-year projections for each tax and compare projections to the Budget Office projections.

The following sections provide more detailed information about each of these steps. To get started, see 
`installation instructions <01_getting_started/installation.html>`_.

.. _vector auto regression: https://en.wikipedia.org/wiki/Vector_autoregression
.. _Granger causality: https://en.wikipedia.org/wiki/Granger_causality



.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   01_getting_started/installation
   01_getting_started/overview
   01_getting_started/interactive

.. toctree::
   :maxdepth: 1
   :caption: Data

   02_data/data_folder
   02_data/plan_details
   02_data/updates

.. toctree::
   :maxdepth: 1
   :caption: Data Processing

   03_processing/overview
   03_processing/steps

.. toctree::
   :maxdepth: 1
   :caption: Modeling

   04_modeling/index


API documentation
=================

.. autosummary::
   :toctree:
   :caption: API documentation
   :recursive:

   fyp_analysis


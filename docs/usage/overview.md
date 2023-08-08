
# Overview

This section will describe how to run the various steps of the analysis code.
It assumes you have already installed the code by following the 
[installation instructions](../install.md).
It also assumes that you are already familiar with the basics of the code
structure and want to get started using the code immediately. If that's not 
the case, please read the [analysis deep dive section](../structure/intro.md) first.


If you're getting started on the analysis for a new Five Year Plan, 
you'll want to first read the instructions for performing the [annual updates](./updates.md). 


First, run the [data processing pipeline](../structure/steps/1-processing.md):

```
poetry run fyp-analysis-run --pipeline dp
```

Then, prepare for the forecast stage by running the 
[forecast prep pipeline](../structure/steps/2-forecast-prep.md):

```
poetry run fyp-analysis-run --pipeline fp
```

Then, launch an interactive environment for the [exploratory modeling step](../structure/steps/3-exploratory.md):

```
poetry run kedro jupyter lab
```

See the [documentation](./interactive.md) for working interactively for more details.

Finally, you can produce the final forecasts by running the [forecast pipeline](../structure/steps/4-forecast.md).

```
poetry run fyp-analysis-run --pipeline forecast
```

The final forecasts are summarized in the following file: `data/07_reporting/revenue_summary.xlsx`.
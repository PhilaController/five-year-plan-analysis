# 3. Exploratory Modeling

The explorating modeling step is the third step in the analysis code and relies 
on the outputs from the two previous steps, [the data processing pipeline](./1-processing.md)
and the [forecast prep pipeline](./2-forecast-prep.md).

In this step, the user identifies the bestfit forecasting
parameters for each tax base, e.g. which features to use to forecast each tax base. 
The analysis is done in the Jupyter notebooks in the `notebooks/` folder. 
There is a notebook file for each tax base.


## Running this step

This step is performed interactively in Jupyter notebooks. You can launch
the interactive environment by running:

```
poetry run kedro jupyter lab
```

This should launch the Jupyter Lab interface in your browser. Using the file
browser interface, navigate to the notebook folder. If you haven't already,
create a folder under the "plans" folder for the current analysis and copy over
a `.md` file for each tax from the "templates" folder to the folder for the
current plan. To launch the `.md` as an interactive notebook, right click on
the file, and select "Open with > Notebook". Now you have an interactive notebook
to edit and execute as you like.

## Overview

The interactive notebooks for each tax will determine the best 
parameters to use in the forecasting process by performing a *grid search* 
on the historical tax data:

1. Use a combination of the Granger matrix, correlation matrix, and intuition to 
select a list of possible endogenous variables for each tax base. 
1. For each set of parameters, split the historical data into multiple samples, make predictions, 
and evaluate the accuracy of the predictions. 
1. Select the best-fit parameters by choosing the parameter set that has the best
accuracy on the historical data.

Because we need to test all possible combinations of the parameters and run the VAR
model for each set, the grid search can be computationally expensive (it is often 
referred to as a "brute-force" method of finding the best parameters).

In the `notebooks/` folder, there are template Jupyter notebook for each tax that performs
these steps. It is useful to perform the grid search interactively so we can 
iterate through the parameters, plot the results, and verify that the fits are reasonable.

For each tax, the notebook templates have code to load the necessary variables,
run the grid search, and then once the bestfit parameters have been idenitifed, 
the last cell in the notebook will save these parameters to a file. Once you 
have done this for all taxes, you can proceed to the final step in the analysis code, 
[the forecasting pipeline](./4-forecast.md).
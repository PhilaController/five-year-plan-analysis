# Determining Best-fit Model Parameters

As part of the modeling process, we need to determine the best 
parameters to use in the fitting process. We can do this
by performing a *grid search* on the historical tax data:

1. Use a combination of the Granger matrix, correlation matrix, and intuition to 
select a list of possible endogenous variables for each tax base. 
2. For each set of parameters, split the historical data into multiple samples, make predictions, 
and evaluate the accuracy of the predictions. 
3. Select the best-fit parameters by choosing the parameter set that has the best
accuracy on the historical data.

Because we need to test all possible combinations of the parameters and run the VAR
model for each set, the grid search can be computationally expensive (it is often 
referred to as a "brute-force" method of finding the best parameters).

In the `notebooks/` folder, there is a Jupyter notebooks for each tax that performs
these steps. It is useful to perform the grid search interactively so we can 
iterate through the parameters, plot the results, and verify that the fits are reasonable.

To launch the Jupyter notebooks, follow the instructions [outlined here](../01_getting_started/interactive).
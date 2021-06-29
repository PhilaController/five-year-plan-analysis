import itertools
import multiprocessing as mp
import os
from os import stat
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.vector_ar.var_model import VARResultsWrapper

from ...data_processing.preprocess.core import PreprocessPipeline
from .utils import get_possible_exog_variables, subset_features


def _get_endog_exog_variables(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    endog_cols: List[str],
    exog_cols: List[str],
    model_quarters: bool,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Internal function to prepare variables for a VAR fit by scaling and
    splitting into endog and exog data frames.

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        the preprocess pipeline object to do the scaled
    endog_cols
        the list of endogeneous VAR variables
    exog_cols
        the list of exogenous variables to regress
    model_quarters
        whether to include quarter as an exog variable

    Returns
    -------
    scaled_features
        all input features after preprocessing
    endog
        the endog variables only
    exog
        the exog variables to regress on
    """
    # Initialize the preprocessor and scale the features
    scaled_features = preprocess.fit_transform(unscaled_features)

    # Pull the endog + exog features only
    endog = subset_features(scaled_features, endog_cols)
    exog = None
    if len(exog_cols):
        exog = subset_features(scaled_features, exog_cols)

    # Whether to include dummy variables to model quarterly seasonality
    if model_quarters:
        exog_q = pd.get_dummies(
            endog.index.month, prefix="month", drop_first=True
        ).set_index(endog.index)
        if exog is None:
            exog = exog_q
        else:
            exog = pd.concat([exog, exog_q], axis=1)

    return scaled_features, endog, exog


def fit_var_model(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    plan_start_year: int,
    max_fit_date: str,
    cbo_data: pd.DataFrame,
    endog_cols: List[str],
    order: int,
    exog_cols: List[str] = [],
    steps: int = 20,
    model_quarters: bool = False,
) -> Tuple[VARResultsWrapper, pd.DataFrame]:
    """
    Fit a VAR(X) model using statsmodels.

    References
    ----------
    [1] https://www.statsmodels.org/stable/generated/statsmodels.tsa.vector_ar.var_model.VAR.html

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        the preprocess pipeline object to do the scaled
    plan_start_year
        the first fiscal year in the plan
    max_fit_date
        the maximum date to include in the fits; you can use this to exclude COVID-related
        drops in 2020 to improve accuracy
    cbo_data
        CBO data frame that is used as exog variables in the future
    endog_cols
        the list of endogeneous VAR variables
    order
        the number of lags to include
    exog_cols, optional
        the list of exogenous variables to regress; default is None
    steps, optional
        the number of future periods to predict; default is 5 years (20 steps)
    model_quarters, optional
        whether to include quarter as an exog indicator variable to model seasonality

    Returns
    -------
    result
        the VAR result object
    unscaled_forecast
        data frame holding the unscaled in-sample endog variables and out-of-sample forecast
    """
    # Split variables into (scaled) endog and exog
    _, endog, exog = _get_endog_exog_variables(
        unscaled_features,
        preprocess,
        endog_cols,
        exog_cols,
        model_quarters,
    )

    # Run the VAR model
    kws = {}
    valid_dates = slice(None, max_fit_date)
    if exog is not None:
        kws = dict(exog=exog.loc[valid_dates])
    var_model = sm.tsa.VAR(endog.loc[valid_dates], **kws)
    var_result = var_model.fit(order, trend="c")

    # Setup forecast
    future_start_date = f"{plan_start_year-1}-07-01"
    future_dates = pd.date_range(future_start_date, periods=steps, freq="QS")

    # Use CBO forecasts for future exog vars
    future_exog = None
    if len(exog_cols):
        scaled_cbo = preprocess.transform(cbo_data[exog_cols])
        future_exog = scaled_cbo.loc[future_dates]

    # Model future quarters
    if model_quarters:
        future_exog_q = pd.get_dummies(
            future_dates.month, prefix="month", drop_first=True
        ).set_index(future_dates)
        if future_exog is None:
            future_exog = future_exog_q
        else:
            future_exog = pd.concat([future_exog, future_exog_q], axis=1)

    kws = {}
    if future_exog is not None:
        kws = dict(exog_future=future_exog)

    # Run the forecast to get scaled predictions
    scaled_forecast = pd.DataFrame(
        var_result.forecast(endog.values, steps, **kws),
        columns=endog.columns,
        index=future_dates,
    )

    # Inverse transform to get the unscaled forecast
    unscaled_forecast = preprocess.inverse_transform(
        pd.concat([endog, scaled_forecast], axis=0)
    ).asfreq("QS")

    # Return results
    return var_result, unscaled_forecast


def calculate_mape(forecast, actual):
    return ((forecast - actual).abs() / actual.abs()).mean()


def test_train_var_model(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    endog_cols: List[str],
    order: int,
    max_fit_date: str,
    exog_cols: List[str] = [],
    n_splits: int = 3,
    model_quarters: bool = False,
) -> Tuple[VARResultsWrapper, pd.DataFrame, pd.DataFrame]:
    """Do a test/train split and evaluate the model on the test set.

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        the preprocess pipeline object to do the scaled
    endog_cols
        the list of endogeneous VAR variables
    order
        the number of lags to include
    split_year
        the year to to use to split into train/test samples
    max_fit_date
        the maximum date to include in the fits; you can use this to exclude COVID-related
        drops in 2020 to improve accuracy
    exog_cols, optional
        the list of exogenous variables to regress; default is None
    model_quarters, optional
        whether to include quarter as an exog indicator variable to model seasonality

    Returns
    -------
    var_result
        the result of the VAR fit
    actual
        the actual test data
    unscaled_forecast
        the predicted test data
    """
    # Split variables into (scaled) endog and exog
    scaled_features, endog, exog = _get_endog_exog_variables(
        unscaled_features.loc[:max_fit_date],
        preprocess,
        endog_cols,
        exog_cols,
        model_quarters,
    )

    # Loop over timne series splits
    actuals = []
    forecasts = []
    mapes = []
    tscv = TimeSeriesSplit(n_splits=n_splits)
    for i, (train_idx, test_idx) in enumerate(tscv.split(scaled_features)):

        # Slice
        test = scaled_features.iloc[test_idx]
        train = scaled_features.iloc[train_idx]

        # Run the VAR model on the training set
        kws = {}
        if exog is not None:
            kws = dict(exog=exog.loc[train.index])
        var_model = sm.tsa.VAR(endog.loc[train.index], **kws)
        var_result = var_model.fit(order, trend="c")

        # Dates in test sample
        steps = len(test.index)

        # Exog vars in test sample
        kws = {}
        if exog is not None:
            kws = dict(exog_future=exog.loc[test.index])

        # Run the forecast
        endog_train = endog.loc[train.index]
        scaled_forecast = pd.DataFrame(
            var_result.forecast(endog_train.values, steps, **kws),
            columns=endog.columns,
            index=test.index,
        )

        # Unscale the forecast
        unscaled_forecast = (
            preprocess.inverse_transform(
                pd.concat([endog_train, scaled_forecast], axis=0)
            )
            .asfreq("QS")
            .loc[test.index]
        )
        forecasts.append(unscaled_forecast)

        # Get the actual test data
        actual = preprocess.inverse_transform(endog.loc[test.index]).asfreq("QS")
        actuals.append(actual)

        # Calculate this mape
        mapes.append(calculate_mape(unscaled_forecast, actual))

    # Concatenate
    actuals = pd.concat(actuals)
    forecasts = pd.concat(forecasts)
    combined_mape = calculate_mape(forecasts, actuals)

    # Return
    return {"mape_vector": mapes, "mape": combined_mape}


def _grid_search_parallel(args):
    """Run the grid search in parallel."""

    # The arguments
    (param_set, param_names, unscaled_features, preprocess, n_splits) = args

    # Get the keyword parameters for this grid cell
    kws = dict(zip(param_names, param_set))

    # Run test/train for this set of parameters
    metrics = test_train_var_model(
        unscaled_features,
        preprocess,
        n_splits=n_splits,
        **kws,
    )

    # Add the keywords
    metrics.update(kws)

    return metrics


def grid_search_var_model(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    grid_params: Dict[str, Any],
    main_endog: str,
    n_splits: int,
    seed: int = 12345,
) -> List[Dict[str, Any]]:
    """
    Perform a grid search over the input grid of parameters, using a VAR
    prediction on the test sample to determine the best parameters.

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        the preprocess pipeline object to do the scaled
    grid_params
        The dictionary of keys to pass to `test_train_var_model` as keywords;
        should include keys like: `endog_cols`, `exog_cols`, and `order`
    main_endog
        The main endog variable that we are forecasting
    split_year
        the year to to use to split into train/test samples
    seed
        Value to set the random seed

    Returns
    -------
    fits
        List of the dictionaries holding the score variables, fitting result, and
        keyword parameters used in the fit; the list is sorted in order from best
        to worst fit based on the test sample score
    """
    # Set the random seed
    np.random.seed(seed)

    # Setup the grid
    param_names = list(grid_params)
    values = [grid_params[name] for name in param_names]

    # Verify param names
    required = ["endog_cols", "order", "max_fit_date"]
    optional = ["exog_cols", "model_quarters"]
    all_args = required + optional
    if not all(col in param_names for col in required):
        missing = set(required) - set(param_names)
        raise ValueError(f"Missing required parameters: {missing}")
    if not all(col in all_args for col in param_names):
        extra = set(param_names) - set(all_args)
        raise ValueError(f"Extra grid parameters provided: {extra}")

    # The other args
    args = (
        param_names,
        unscaled_features,
        preprocess,
        n_splits,
    )

    # Run in parallel
    N = mp.cpu_count()
    with mp.Pool(processes=1) as p:
        fits = p.map(
            _grid_search_parallel,
            [tuple([param_set, *args]) for param_set in itertools.product(*values)],
        )

    # Add the MAPE for the target column
    for f in fits:
        f["target_mape"] = f["mape"][main_endog]

    # Return fits, sorted from best score to worst
    return sorted(fits, key=lambda x: x["target_mape"])


def run_possible_models(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    main_endog: str,
    other_endog: List[str],
    orders: List[int],
    grangers: pd.DataFrame,
    max_fit_date: Union[str, List[str]],
    cbo_columns: List[str],
    alpha: float = 0.05,
    max_other_endog: int = 1,
    max_exog: int = 4,
    n_splits: int = 3,
    seed: int = 12345,
    model_quarters: Union[bool, List[bool]] = False,
) -> List[Dict[str, Any]]:
    """
    Run all possible models and return the VAR fits.

    This uses the input grangers matrix to determine which exog
    variables are likely best.

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        The preprocesser to go from unscaled to scaled
    main_endog
        The main endogeneous column of interest that we are forecasting
    other_endog
        Other possible endog columns of interest that are correlated with main_endog
    orders
        The VAR orders to explore
    grangers
        The grangers causation matrix, used to find possible exog variables
    max_fit_date
        the max date to include in the fit; can be a list of values if you want to
        explore multiple values
    cbo_columns
        the list of CBO features
    alpha
        The significance level to consider for granger causation
    max_other_endog
        Consider models with a maximum of this many "other" endog variables
    max_exog
        Consider models with a maximum of this many exog variables
    split_year
        the year to to use to split into train/test samples
    seed
        Value to set the random seed
    model_quarters
        whether to include quarter as an exog variable; can be a list of values if
        you want to explore multiple values

    Returns
    -------
    fits
        List of the dictionaries holding the score variables, fitting result, and
        keyword parameters used in the fit; the list is sorted in order from best
        to worst fit based on the test sample score
    """
    # Get the combo of possible endog variables
    other_endog_combos = []
    while max_other_endog > 0:
        other_endog_combos += list(itertools.combinations(other_endog, max_other_endog))
        max_other_endog -= 1

    # Make sure we have lists
    if not isinstance(model_quarters, list):
        model_quarters = [model_quarters]
    if not isinstance(max_fit_date, list):
        max_fit_date = [max_fit_date]

    # Loop over all possible endog combos
    all_fits = []
    for cols in other_endog_combos:

        # Endog cols
        endog_cols = [main_endog] + list(cols)

        # Get possible exog variables
        possible_exog = get_possible_exog_variables(
            grangers, endog_cols, cbo_columns, alpha=alpha
        )

        # Make exog grid
        if max_exog > 0:
            max_exog = min(len(possible_exog), max_exog)
            exog_cols = []
            while max_exog > 0:
                exog_cols += [
                    list(l) for l in itertools.combinations(possible_exog, max_exog)
                ]
                max_exog -= 1
        else:
            exog_cols = [[]]

        # Make the dict of grid parameters
        grid_params = {
            "order": orders,
            "endog_cols": [endog_cols],
            "exog_cols": exog_cols,
            "model_quarters": model_quarters,
            "max_fit_date": max_fit_date,
        }

        # Do the grid search and save the fits
        all_fits += grid_search_var_model(
            unscaled_features,
            preprocess,
            grid_params,
            main_endog,
            n_splits=n_splits,
            seed=seed,
        )

    return sorted(all_fits, key=lambda x: x["target_mape"])


def get_avg_forecast_from_fits(
    unscaled_features: pd.DataFrame,
    preprocess: PreprocessPipeline,
    fits: List[Dict[str, Any]],
    main_endog: str,
    plan_start_year: int,
    cbo_data: pd.DataFrame,
    max_fits: int = 1,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Calculate the average forecast from a list of fits.

    Parameters
    ----------
    unscaled_features
        The feaures data before preprocessing, e.g., scaling or differences
    preprocess
        The preprocesser to go from unscaled to scaled
    fits
        List of the parameter dictionaries, sorted in order from best
        to worst fit on the test sample
    main_endog
        The maine endog variable of interest that were forecasting
    plan_start_year
        the first fiscal year in the plan
    cbo_data
        CBO data frame that is used as exog variables in the future
    max_fits
        Number of fits to average over, starting from the fit with
        the lowest score

    Returns
    -------
    avg_forecast
        The average forecast, summed over by fiscal year
    """
    # Iterate over the parameters
    forecasts = []
    all_params = []
    for i in range(0, max_fits):

        # Get and save these fits
        params = fits[i]
        all_params.append(params)

        # Do the fit
        result, forecast = fit_var_model(
            unscaled_features,
            preprocess,
            cbo_data=cbo_data,
            plan_start_year=plan_start_year,
            endog_cols=params["endog_cols"],
            order=params["order"],
            exog_cols=params["exog_cols"],
            max_fit_date=params["max_fit_date"],
            model_quarters=params.get("model_quarters", False),
        )

        # Group by fiscal year
        F = forecast[main_endog]
        F = F.groupby(F.index.shift(2, freq="QS").year).sum().to_frame()
        forecasts.append(F)

    # Average the forecasts
    avg_forecast = (
        pd.concat(forecasts, axis=1)
        .mean(axis=1)
        .rename_axis("fiscal_year", index=0)
        .rename(main_endog)
    )

    return avg_forecast, all_params

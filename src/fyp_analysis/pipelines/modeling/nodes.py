from typing import Dict, List

import pandas as pd

from .correlate import grangers_causation_matrix, plot_feature_correlation
from .predict import get_possible_endog_variables as _get_possible_endog_variables


def get_feature_correlations(
    scaled_features: pd.DataFrame, min_year: int
) -> pd.DataFrame:
    """
    Calculate and plot the correlation between scaled features over time.

    Notes
    -----
    Correlations figure is saved to the "data / 04_model_input" folder.

    Parameters
    ----------
    scaled_features
        the scaled features, after preprocessing is complete
    min_year
        the minimum year for the input features
    """
    return plot_feature_correlation(scaled_features, min_year)


def get_grangers_matrix(
    scaled_features: pd.DataFrame, maxlag: int = 6, max_date: str = "2021-03-31"
) -> pd.DataFrame:
    """
    Check Granger Causality of all possible combinations of the time series. The columns
    are the response variable, rows are predictors.

    The values in the table are the P-Values. P-Values lesser than the
    significance level (0.05), implies the Null Hypothesis that the coefficients
    of the corresponding past values is zero, that is, the X does not
    cause Y can be rejected.

    References
    ----------
    [1] https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html
    [2] https://en.wikipedia.org/wiki/Granger_causality

    Parameters
    ----------
    scaled_features
        the data containing the time series variables
    maxlag
        Compute the test for all lags up to maxlag.
    max_date
        Maximum date to include in the calculation

    Returns
    -------
    grangers
        the grangers correlation matrix, which holds the p-values for the test between variables
    """
    date_slice = slice(None, max_date)
    data = scaled_features.asfreq("QS").loc[date_slice]
    return grangers_causation_matrix(data, maxlag=maxlag)


def get_possible_endog_variables(
    scaled_features: pd.DataFrame, grangers: pd.DataFrame, alpha: float = 0.05
) -> Dict[str, List[str]]:
    """
    Get possible endog variables for tax base features, based on Granger causality.

    Return a dict of possible endog variables based on Grangers causality for each
    tax base feature.

    Parameters
    ----------
    scaled_features
        the scaled (preprocessed) features
    grangers
        the Grangers correlation matrix
    alpha
        The significance level to consider for granger causation

    Returns
    -------
    A list of variable names that are Granger significant for each tax base feature
    """
    out = {}
    for col in scaled_features.columns:
        if col.endswith("Base"):
            out[col] = _get_possible_endog_variables(grangers, col)

    return out

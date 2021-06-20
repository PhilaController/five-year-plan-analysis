from typing import List, Optional

import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests

from fyp_analysis import SRC_DIR


def plot_feature_correlation(
    scaled_features: pd.DataFrame, min_year: int
) -> pd.DataFrame:
    """
    Plot the time-series correlations between scaled features, and return the
    correlation matrix

    Notes
    -----
    Correlations figure is saved to the "data / 04_model_input" folder.

    Parameters
    ----------
    scaled_features
        the scaled features after preprocessing
    min_year
        trim the features to a specific minimum year before calculating the
        correlations over time

    Returns
    -------
    corr
        the correlation matrix between features

    """
    # Set the context
    sns.set(style="white")

    # Calculate the corr
    corr = scaled_features.corr()

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(
        figsize=(11, 9), gridspec_kw=dict(left=0.15, bottom=0.25, right=1.0, top=0.99)
    )

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(
        corr,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar=False,
        xticklabels=True,
        yticklabels=True,
    )
    plt.setp(ax.get_xticklabels(), fontsize=8)
    plt.setp(ax.get_yticklabels(), fontsize=8)

    # Save figure
    output_dir = SRC_DIR / ".." / ".." / "data" / "04_model_input"
    plt.savefig(output_dir / f"correlations_min_year_{min_year}.png", dpi=400)

    return corr


def grangers_causation_matrix(
    data: pd.DataFrame,
    test: str = "ssr_chi2test",
    verbose: bool = False,
    maxlag: int = 6,
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
    data
        the data containing the time series variables
    test
        the name of the test to use; statsmodels calculates four causality tests:
        'params_ftest', 'ssr_ftest', 'ssr_chi2test', 'lrtest'
    verbose
        whether to log the p-values for each variable pair
    maxlag
        Compute the test for all lags up to maxlag.

    Returns
    -------
    grangers
        the grangers correlation matrix, which holds the p-values for the test between variables
    """
    # List of variables
    variables = data.columns.tolist()

    # Initialize an empty dataframe for results
    df = pd.DataFrame(
        np.zeros((len(variables), len(variables))), columns=variables, index=variables
    )

    # Loop over each dimension
    for c in df.columns:
        for r in df.index:

            # Do the test with a specific max lag
            test_result = grangercausalitytests(
                data[[r, c]], maxlag=maxlag, verbose=False
            )
            # Extract the p-values
            p_values = [round(test_result[i + 1][0][test][1], 4) for i in range(maxlag)]
            if verbose:
                print(f"Y = {r}, X = {c}, P Values = {p_values}")

            # Get the min p-value and store it
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value

    # Columns get the _x and rows get the _y suffix
    df.columns = [var + "_x" for var in variables]
    df.index = [var + "_y" for var in variables]

    # Return
    return df.T

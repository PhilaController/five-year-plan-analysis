from typing import Tuple

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from phila_style.matplotlib import get_theme
from statsmodels.graphics import tsaplots
from statsmodels.tsa.stattools import adfuller

from fyp_analysis import SRC_DIR

FIGURE_DIR = SRC_DIR / ".." / ".." / "data" / "02_intermediate" / "stationary_figures"


def test_stationarity(data: pd.Series, alpha: float = 0.05) -> bool:
    """
    Test for stationary with the Augmented Dickey-Fuller unit root test from
    statsmodels.

    References
    ----------
    [1] https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.adfuller.html

    Parameters
    ----------
    data
        the input time series data to test
    alpha
        the significance threshold to determine stationarity

    Returns
    -------
    Whether the input feature is stationary
    """
    results = adfuller(data)
    return results[1] < alpha


def plot_data_properties(
    data: pd.Series, title: str, figsize: Tuple[int, int] = (8, 6)
) -> mpl.figure.Figure:
    """
    Plot data properties (e.g., auto-correlation and partial auto-corr) related to stationarity.

    References
    ----------
    [1] https://www.statsmodels.org/dev/generated/statsmodels.graphics.tsaplots.plot_acf.html
    [2] https://www.statsmodels.org/stable/generated/statsmodels.graphics.tsaplots.plot_pacf.html

    Parameters
    ----------
    data
        the input data feature to plot
    title
        the figure title
    figsize
        the figure size to use

    Returns
    -------
    The matplotlib figure
    """
    with plt.style.context(get_theme()):
        # Initialize the figure and set up the axes
        fig = plt.figure(constrained_layout=False, dpi=300, figsize=figsize)
        gs = fig.add_gridspec(
            nrows=2, ncols=2, hspace=0.5, left=0.1, right=0.95, top=0.9, bottom=0.1
        )
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])

        # Top axes is the time series
        data.plot(ax=ax1, title=title)
        ax1.set_xlim(str(data.index.year.min() - 1), str(data.index.year.max() + 1))

        # Plot the acf and pacf
        tsaplots.plot_acf(data, ax=ax2)
        tsaplots.plot_pacf(data, ax=ax3)

        return fig


def get_stationary_guide(
    data: pd.DataFrame, exclude_2020: bool = False
) -> pd.DataFrame:
    """
    Get a guide to making each feature variable stationary by:

    - Can we take the log of the variable (e.g., is it non-negative?)?
    - How many differences for stationarity?
    - Should we normalize the data first?

    This also creates the diagnostic stationarity plots for tax bases
    and save them to:

    "02_intermediate / stationary_figures"

    Parameters
    ----------
    data
        the input data to test
    exclude_2020, optional
        whether to exclude 2020 from the calculations

    Returns
    -------
    guide
        the data frame of meta-data that allows each variable to be stationary
    """
    # These tax bases are differenced YOY vs. quarter over quarter
    QUARTERLY_YOY = ["GrossReceiptsBase", "NetIncomeBase", "NPTBase"]

    # Make the figure dir
    if not FIGURE_DIR.exists():
        FIGURE_DIR.mkdir(parents=True)

    # Loop over all columns
    stationary = []
    for col in data.columns:
        # The feature data
        feature = data[col].dropna()

        # Can we log?
        loggable = (feature > 0).all()
        norm = 1
        if loggable:
            feature = np.log(feature)
        else:
            norm = feature.mean()
            norm = 10 ** (np.log10(norm).round())
            feature /= norm

        # Exclude 2020?
        if exclude_2020:
            slc = slice(None, "2019")
            feature = feature.loc[slc]

        # Loop until we've differenced enough
        ndiffs = 0
        while not test_stationarity(feature) or ndiffs < 1:
            # Difference tax bases only once
            if ndiffs == 1 and "Base" in col:
                break

            # How many quarters to difference over?
            periods = 1 if col not in QUARTERLY_YOY else 4
            feature = feature.diff(periods).dropna()
            ndiffs += 1

        # Make the plot for tax bases
        if "Base" in col:
            is_stationary = test_stationarity(feature)
            plot_data_properties(feature, f"{col}, stationary={is_stationary}")
            plt.savefig(FIGURE_DIR / f"{col}.png")

        # Save the data
        stationary.append([col, ndiffs, loggable, norm, periods])

    return pd.DataFrame(
        stationary, columns=["variable", "ndiffs", "loggable", "norm", "periods"]
    )

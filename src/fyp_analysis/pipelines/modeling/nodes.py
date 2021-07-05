import re
from typing import Dict, List

import pandas as pd
from kedro.framework.session import get_current_session
from loguru import logger
from matplotlib import pyplot as plt

from ... import SRC_DIR
from ...extras.datasets import PlanDetails, Taxes
from .correlate import grangers_causation_matrix, plot_feature_correlation
from .predict import get_possible_endog_variables as _get_possible_endog_variables
from .predict import get_prophet_forecast, get_var_forecast, plot_projection_comparison
from .predict import report_forecast_results as _report_forecast_results


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


def run_forecasts(
    unscaled_features: pd.DataFrame,
    stationary_guide: pd.DataFrame,
    plan_details: PlanDetails,
    plan_start_year: int,
    cbo_forecast_date: str,
):
    """Run the forecasts."""

    # Get the current session and context
    session = get_current_session()
    context = session.load_context()

    # Name of fit param datasets
    params = [k for k in context.catalog.list() if k.endswith("fit_params")]

    def _get_forecast(tax_base_name, fit_params):
        """Calculate the forecast, using the specified method."""

        # Make sure fit params are a list, not a single dict
        if isinstance(fit_params, dict):
            fit_params = [fit_params]

        # Get the VAR forecast
        if isinstance(fit_params, list):

            # Get the VAR forecast
            tax_base_forecast = get_var_forecast(
                unscaled_features,
                stationary_guide,
                fit_params,
                tax_base_name,
                plan_start_year,
                cbo_forecast_date,
            )
        else:
            # Get the VAR forecast
            tax_base_forecast = get_prophet_forecast(
                fit_params, unscaled_features, tax_base_name, plan_start_year
            )

        return tax_base_forecast

    # Loop over each tax and get the parameters
    tax_bases = []
    tax_names = []
    for key in params:

        # Get the tax name
        grp = re.match("(?P<tax_name>.*)_fit_params", key)
        tax_name = grp["tax_name"]
        tax_name = "".join([w.capitalize() for w in tax_name.split("_")])
        if tax_name in ["Rtt", "Npt"]:
            tax_name = tax_name.upper()

        # Log
        logger.info(f"Calculating forecast for {tax_name}...")

        # The name of the tax base
        tax_base_name = f"{tax_name}Base"

        # Try to load the data
        try:
            fit_params = context.catalog.load(key)
        except:
            logger.info(f"Cannot load parameters for {tax_name}")
            continue

        # Run the forecast
        tax_bases.append(_get_forecast(tax_base_name, fit_params))
        tax_names.append(tax_name)

    # Combine into a dataframe
    tax_bases = pd.concat(tax_bases, axis=1)

    # Get the revenues too
    tax_revenues = []
    taxes = Taxes(plan_details)

    # Initialize figures directory
    figures_dir = (
        SRC_DIR / ".." / ".." / "data" / "06_model_output" / "forecast_figures"
    )
    if not figures_dir.exists():
        figures_dir.mkdir()

    # Add birt
    tax_revenues.append(
        taxes["BIRT"]
        .get_budget_comparison(
            tax_bases["NetIncomeBase"], tax_bases["GrossReceiptsBase"]
        )
        .assign(tax_name="BIRT")
    )

    # Plot birt
    plot_projection_comparison(
        taxes["BIRT"], tax_bases["NetIncomeBase"], tax_bases["GrossReceiptsBase"]
    )
    plt.savefig(figures_dir / "BIRT.png")

    # Do the rest
    for i, col in enumerate(tax_bases.columns):

        # Skip BIRT
        if col in ["NetIncomeBase", "GrossReceiptsBase"]:
            continue
        logger.info(col)

        this_tax = taxes[tax_names[i]]
        tax_revenues.append(
            this_tax.get_budget_comparison(tax_bases[col]).assign(tax_name=tax_names[i])
        )

        # Plot too
        plot_projection_comparison(this_tax, tax_bases[col])
        plt.savefig(figures_dir / f"{tax_names[i]}.png")

    # Combine into a dataframe
    tax_revenues = pd.concat(tax_revenues, axis=0).reset_index()

    # Add BIRT base
    tax_bases["BIRTBase"] = tax_bases[["NetIncomeBase", "GrossReceiptsBase"]].sum(
        axis=1
    )

    return tax_bases, tax_revenues


def report_forecast_results(plan_start_year, tax_revenues, tax_bases):
    return _report_forecast_results(plan_start_year, tax_revenues, tax_bases)

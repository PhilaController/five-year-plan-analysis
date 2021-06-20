from typing import List

import pandas as pd
from loguru import logger

from ...extras.datasets import PlanDetails, Taxes, load_cbo_data
from . import utils
from .indicators import get_economic_indicators as _get_economic_indicators
from .preprocess import PreprocessPipeline, get_selected_features
from .stationary import get_stationary_guide as _get_stationary_guide


def get_economic_indicators(fresh=False) -> pd.DataFrame:
    """
    Load all economic indicators, optionally downloading fresh copies.

    Parameters
    ----------
    fresh
        whether to download a fresh copy of the indicators

    Returns
    -------
    The data frame of all economic indicators
    """
    return _get_economic_indicators(fresh=fresh)


def get_quarterly_averages(economic_indicators: pd.DataFrame) -> pd.DataFrame:
    """
    Get quarterly averages, first removing any indicators
    with annual frequency.

    Parameters
    ----------
    economic_indicators
        the raw economic indicators

    Returns
    -------
    The quarterly averaged indicatorsß
    """
    return economic_indicators.pipe(utils.get_faster_than_annual).pipe(
        utils.get_quarterly_average
    )


def impute_cbo_values(
    features: pd.DataFrame, plan_start_year: int, cbo_forecast_date: str
) -> pd.DataFrame:
    """
    Impute CBO forecast values for Q4 of the current fiscal year.

    Parameters
    ----------
    features
        the input quarterly features
    plan_start_year
        the first fiscal year of the current Plan under analysis
    cbo_forecast_date
        the date for the CBO forecast

    Returns
    -------
    The updated features with CBO values imputed
    """

    # Determime the current fiscal year
    current_fiscal_year = plan_start_year - 1

    # Load CBO data
    cbo_data = load_cbo_data(date=cbo_forecast_date)

    # The date for Q4 that we need to impute
    date = f"{current_fiscal_year}-04-01"
    q4_CBO = cbo_data.loc[date]

    # Impute FQ4 values
    features.loc[date, q4_CBO.index] = q4_CBO.values

    return features


def combine_features_and_bases(
    features: pd.DataFrame, plan_details: PlanDetails, min_year: int = 1990
) -> pd.DataFrame:
    """
    Combine the features and the tax bases.

    Parameters
    ----------
    features
        the economic indicator features
    plan_details
        the object holding the Plan details
    min_year
        trim the features to this minimum year as a preliminary cut

    Returns
    -------
    The combined data frame with features and tax bases
    """
    # Get all of the tax bases
    taxes = Taxes(plan_details)
    tax_bases = taxes.get_all_tax_bases()

    # Combine
    out = pd.concat([features, tax_bases], axis=1)

    # Trim to a min_year (index is a DateTime index)
    valid_dates = slice(str(min_year), None)
    return out.loc[valid_dates]


def seasonally_adjust_features(
    features: pd.DataFrame,
    columns: List[str] = [
        "ActivityLicensesPhilly",
        "BizLicensesPhilly",
        "BuildingPermitsPhilly",
        "CPIPhillyMSA",
        "ContinuedClaimsPA",
        "WeeklyEconomicIndex",
        "DeedTransfersPhilly",
        "InitialClaimsPA",
        "UncertaintyIndex",
        "UnemploymentPhilly",
    ],
) -> pd.DataFrame:
    """
    Seasonally adjust the specific columns, using the LOESS
    functionality in statsmodels.

    References
    ----------
    [1] https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html

    Parameters
    ----------
    features
        the input features
    columns, optional
        columns to seasonally adjust

    Returns
    -------
    Copy of input features with columns seasonally adjusted
    """
    # Make a copy
    out = features.copy()

    # Do the SA
    for col in columns:
        if col in out.columns:
            logger.info(f"Seasonally adjusting {col}")
            out[col] = utils.seasonally_adjust(out[col])

    return out


def get_stationary_guide(features: pd.DataFrame) -> pd.DataFrame:
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
    features
        the input features to calculate meta-data for

    Returns
    -------
    guide
        the data frame of meta-data that allows each variable to be stationary
    """
    return _get_stationary_guide(features)


def get_final_unscaled_features(features: pd.DataFrame, min_year: int) -> pd.DataFrame:
    """
    Get the final unscaled features to input into model.

    Parameters
    ----------
    features
        input data of unscaled features
    min_year
        trim features to a specific minimum year

    Returns
    -------
    The final unscaled data frame of features
    """
    return get_selected_features(features, min_year)


def get_final_scaled_features(
    features: pd.DataFrame, stationary_guide: pd.DataFrame
) -> pd.DataFrame:
    """
    Get the final unscaled features to input into model.

    This applies the `PreprocessPipeline` to the unscaled features to the produce
    the final scaled data frame.

    Parameters
    ----------
    features
        the final unscaled features
    stationary_guide
        the stationarity guide output from `get_stationarity_guide`

    Returns
    -------
    The final scaled data frame of features
    """

    # The preprocessor
    preprocess = PreprocessPipeline(stationary_guide)

    # Return scaled features
    return preprocess.fit_transform(features)

import pandas as pd
from statsmodels.tsa.seasonal import STL


def calculate_frequency(df: pd.DataFrame, reference_year: int = 2018) -> pd.Series:
    """
    Utility function to calculate the frequency of indicators based on date index.

    Parameters
    ----------
    df
        the input indicator data frame
    reference_year, optional
        the year used as a reference to calculate frequency
    """
    # Check input index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Index should be a datetime index")

    # Determine freq for each column
    frequency = []
    for col in df.columns:
        col_data = df[col].dropna()
        col_freq = col_data.groupby(col_data.index.year).size()
        try:
            frequency.append(col_freq.loc[reference_year])
        except:
            raise ValueError("Error trying to calculate frequencies")

    # Make the final Series
    out = pd.Series(frequency, index=df.columns)
    out = out.map(
        {12: "monthly", 4: "quarterly", 1: "annual", 6: "bi-monthly", 52: "weekly"}
    ).fillna("daily")

    return out


def seasonally_adjust(X: pd.Series) -> pd.Series:
    """
    Seasonally adjust using Season-Trend decomposition using LOESS from
    statsmodels.

    References
    ----------
    [1] https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.STL.html

    Parameters
    ----------
    X
        input Series to adjust

    Returns
    -------
    The seasonally adjusted data
    """
    # Fit the STL model with statsmodels
    stl = STL(X.dropna(), robust=True)
    res = stl.fit()

    # Get the data with seasonality
    SA = res.trend + res.resid

    # Return
    out = X.copy()
    out.loc[SA.index] = SA.values
    return out


def get_faster_than_annual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trim the input data frame to include only those indicators
    with a frequency faster than annual.

    Parameters
    ----------
    df
        the input feature data

    Returns
    -------
    A copy of the input data holding only the selected features
    """
    # Calculate the frequency
    frequency = calculate_frequency(df)

    # Select faster than annual
    faster_than_annual = ~frequency.isin(["annual"])
    feature_names = frequency[faster_than_annual].index.tolist()

    # Return a trimmed copy
    out = df.copy()
    return out[feature_names]


def get_quarterly_average(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the quarterly average of the input indicators.

    Parameters
    ----------
    df
        input feature data

    Returns
    -------
    The quarterly averaged feature data
    """
    return df.resample("QS").mean()

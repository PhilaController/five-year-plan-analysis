from typing import List

import pandas as pd


def aggregate_to_fiscal_year(data, freq="QS"):
    """Group by fiscal year and sum."""

    assert isinstance(data.index, pd.DatetimeIndex)
    assert freq in ["MS", "QS"]
    shift = 2 if freq == "QS" else 6
    return (
        data.groupby(data.index.shift(shift, freq=freq).year)
        .sum()
        .to_frame()
        .rename_axis("fiscal_year", index=0)
    )


def get_features_col(columns: List[str], col: str, how: str = "endswith") -> str:
    """
    Get a specific feature column.

    Parameters
    ----------
    columns
        the list of columns to select values from
    col
        look for matches based on this string
    how
        how to look for matches; either 'endswith' or 'contains'

    Returns
    -------
    The list of values in the input list that match
    """
    if how == "endswith":
        matcher = lambda a, b: a.endswith(b)
    elif how == "contains":
        matcher = lambda a, b: b in a
    else:
        raise ValueError("Unknown 'how'")

    matches = [c for c in columns if matcher(c, col)]
    if not len(matches):
        raise ValueError(f"No such column: {col}")

    return matches[0]


def subset_features(features: pd.DataFrame, usecols: List[str]) -> pd.DataFrame:
    """
    Utility function to return the subset of features in the
    input column list.

    Parameters
    ----------
    features
        the input data frame to trim
    usecols
        the list of columns to trim to
    """
    _usecols = [get_features_col(features.columns, col) for col in usecols]
    return features[_usecols]


def get_possible_exog_variables(
    grangers: pd.DataFrame,
    endog_cols: List[str],
    cbo_columns: List[str],
    alpha: float = 0.05,
) -> List[str]:
    """
    Return a list of possible exog variables based on Grangers causality.



    Parameters
    ----------
    grangers
        The grangers causation matrix
    endog_cols
        the list of endog columns to look for exog columns for
    cbo_columns
        the list of CBO variables
    alpha
        The significance level to consider for granger causation

    Returns
    -------
        The list of possible exog variables for the input endog columns
    """

    def _run(grangers, col, alpha):
        # The response variable (ends in _y)
        col = get_features_col(grangers.columns, col, how="contains")

        # Variables that Granger Cause input column
        forward_g = grangers[col].sort_values()
        forward_g = forward_g.loc[forward_g < alpha]

        # Trim to CBO
        forward_g_cols = [
            (i, c.split(".")[-1].split("_")[0]) for (i, c) in enumerate(forward_g.index)
        ]
        cbo_subset = [
            forward_g.index[i] for (i, c) in forward_g_cols if c in cbo_columns
        ]
        forward_g = forward_g.loc[cbo_subset]

        # Variables that are Granger Caused by input column
        reverse_g = pd.Series(
            [
                grangers.loc[col.replace("_y", "_x"), c.replace("_x", "_y")]
                for c in forward_g.index
            ],
            index=[c.replace("_x", "_y") for c in forward_g.index],
        ).sort_values()

        # We want not significant here --> exog does NOT granger cause input
        significant_one_way = reverse_g.loc[reverse_g >= 0.05].index.tolist()

        return [c.split(".")[-1][:-2] for c in significant_one_way]

    # Loop over all endog columns
    possible = []
    for col in endog_cols:
        possible.append(set(_run(grangers, col, alpha=alpha)))

    # Get the intersection
    allowed = possible[0]
    for p in possible:
        allowed = allowed.intersection(p)

    # Make sure all are CBO only
    toret = list(allowed)
    if not all(c in cbo_columns for c in allowed):
        missing = list(set(allowed) - set(cbo_columns))
        raise ValueError(f"Error: {missing}")

    return toret


def get_possible_endog_variables(
    grangers: pd.DataFrame, col: str, alpha: float = 0.05
) -> List[str]:
    """
    Return a list of possible endog variables based on Grangers causality.

    Parameters
    ----------
    grangers
        The grangers causation matrix
    col
        the column to get endog variables for
    alpha
        The significance level to consider for granger causation

    Returns
    -------
    The list of variable names that are Granger significant
    """

    # The response variable (ends in _y)
    col = get_features_col(grangers.columns, col, how="contains")

    # Variables that Granger Cause input column
    forward_g = grangers[col].sort_values()
    forward_g = forward_g.loc[forward_g < alpha]

    # Variables that are Granger Caused by input column
    reverse_g = pd.Series(
        [
            grangers.loc[col.replace("_y", "_x"), c.replace("_x", "_y")]
            for c in forward_g.index
        ],
        index=[c.replace("_x", "_y") for c in forward_g.index],
    ).sort_values()

    # Variables that are significant both ways
    significant_both_ways = reverse_g.loc[reverse_g < alpha].index.tolist()

    # Return the list of columns
    return [c.split(".")[-1][:-2] for c in significant_both_ways]

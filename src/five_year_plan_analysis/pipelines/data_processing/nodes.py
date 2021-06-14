import pandas as pd

from .indicators import get_economic_indicators as _get_economic_indicators


def get_economic_indicators(fresh=False) -> pd.DataFrame:
    """Load economic indicators."""
    return _get_economic_indicators(fresh=fresh)

import os
from dataclasses import dataclass

import pandas as pd
import quandl

from .core import DataSource


@dataclass
class DataSourceQuandl(DataSource):
    """
    Data downloaded from the Quandl database.

    Notes
    -----
    See also https://www.quandl.com/

    Parameters
    ----------
    name:
        The name of the data series.
    frequency:
        The data frequency, one of 'daily', 'weekly', 'monthly',
        'quarterly', or 'annual'
    geography:
        The geography covered by the data, one of 'national',
        'state', 'Philadelphia MSA', 'Philadelphia'
    description:
        The description for the dataset.
    series_id:
        The identifier for the data series.
    """

    JSON = "quandl.json"

    series_id: str
    description: str

    def extract(self) -> pd.Series:
        """Download data from Quandl."""

        # API key for QUANDL
        QUANDL_API_KEY = os.environ.get("QUANDL_API_KEY")

        # Make sure the API key is valid
        if QUANDL_API_KEY is None:
            raise ValueError(
                "Please set the 'QUANDL_API_KEY' variable in the .env file to download data from Quandl"
            )

        return quandl.get(self.series_id, api_key=QUANDL_API_KEY)

    def transform(self, df: pd.Series) -> pd.Series:
        """Set the name properly."""
        date_slice = slice("01-01-1950", None)
        return (
            df.rename_axis("Date", axis="index")
            .squeeze()
            .rename(self.name)
            .loc[date_slice]
        )

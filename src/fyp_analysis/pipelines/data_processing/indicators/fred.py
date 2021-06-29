import os
from dataclasses import dataclass

import fredapi
import pandas as pd
from kedro.config import MissingConfigException

from .core import DataSource


@dataclass
class DataSourceFRED(DataSource):
    """
    Data downloaded from the FRED database.

    Note:
        See also https://fred.stlouisfed.org/

    Parameters
    ----------
    name:
        The name of the data series.
    frequency:
        The data freq
    geography:
        The geography covered by the data, one of 'national',
        'state', 'Philadelphia MSA', 'Philadelphia'
    description:
        The FRED description for the dataset.
    series_id:
        The FRED identifier for the data series.
    """

    JSON = "fred.json"

    series_id: str
    description: str
    seas_adjusted: bool

    def extract(self) -> pd.Series:
        """Download data from FRED."""

        # API key for FRED
        FRED_API_KEY = self.credentials.get("FRED_API_KEY")

        # Make sure the API key is valid
        if FRED_API_KEY is None:
            raise MissingConfigException(
                (
                    "Please set the 'FRED_API_KEY' variable conf/local/credentials.yml file. "
                    "An API key can be obtained from: https://fred.stlouisfed.org/docs/api/api_key.html"
                )
            )

        f = fredapi.Fred(api_key=FRED_API_KEY)
        return f.get_series(series_id=self.series_id)

    def transform(self, df: pd.Series) -> pd.Series:
        """Set the name properly."""
        return df.rename_axis("Date", axis="index").rename(self.name)

from dataclasses import dataclass

import pandas as pd

from .core import DataSource


@dataclass
class DataSourceZillow(DataSource):
    """
    A Zillow dataset.

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
    url:
        The download URL for the data.
    """

    JSON = "zillow.json"

    url: str

    def extract(self) -> pd.DataFrame:
        """Load the CSV data from the URL."""
        return pd.read_csv(self.url, encoding="ISO-8859-1")

    def transform(self, df: pd.DataFrame) -> pd.Series:
        """
        Process the raw data, returning the time series data for
        Philadelphia only.
        """

        # columns we can safely remove
        unnecessary = [
            "City",
            "Metro",
            "RegionType",
            "DataTypeDescription",
            "CountyName",
            "SizeRank",
            "RegionID",
            "RegionName",
            "StateName",
            "State",
            "StateFullName",
        ]

        # Build the query
        query = "((RegionName == 'Philadelphia') or (RegionName == 'Philadelphia, PA'))"
        if "StateName" in df.columns:
            query += " and (StateName == 'Pennsylvania' or StateName == 'PA')"
        elif "StateFullName" in df.columns:
            query += " and (StateFullName == 'Pennsylvania')"
        elif "State" in df.columns:
            query += " and (State == 'Pennsylvania' or State == 'PA')"

        # do the selection
        df = df.query(query)
        if not len(df):
            raise ValueError("Unable to accurately parse Zillow data")

        # remove unnecessary columns
        df = df.drop(labels=[col for col in unnecessary if col in df.columns], axis=1)

        # transpose
        data = df.melt(var_name="Date", value_name=self.name)

        # add date columns
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        return data.set_index("Date")

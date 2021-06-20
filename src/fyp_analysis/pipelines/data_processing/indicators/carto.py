from dataclasses import dataclass

import carto2gpd
import pandas as pd

from .core import DataSource


@dataclass
class DataSourceCARTO(DataSource):
    """
    Data downloaded from the City of Philadelphia's CARTO database.

    Parameters
    ----------
    name:
        The name of the data series.
    frequency:
        The data frequency, one of 'daily', 'weekly', 'monthly',
        'quarterly', or 'annual'
    geography:
        The geography covered by the data, one of 'national',
        'state', Philadelphia MSA', 'Philadelphia'
    description:
        The description of the dataset.
    table_name:
        The name of the CARTO table.
    where:
        The SQL clause for specifying which data to download.
    data_column:
        The name of the date column in the database.
    """

    JSON = "carto.json"

    table_name: str
    where: str
    date_column: str

    def extract(self) -> pd.DataFrame:
        """Load the data from the CARTO database."""

        return carto2gpd.get(
            "https://phl.carto.com/api/v2/sql",
            self.table_name,
            where=self.where,
        )

    def transform(self, df: pd.DataFrame) -> pd.Series:
        """Process raw from CARTO into a monthly time series."""

        # Get number per month and year
        N = (
            df.assign(
                **{
                    self.date_column: lambda df: pd.to_datetime(
                        df[self.date_column], errors="coerce"
                    ),
                    "year": lambda df: df[self.date_column].dt.year,
                    "month": lambda df: df[self.date_column].dt.month,
                }
            )
            .groupby(["year", "month"])
            .size()
            .reset_index(name=self.name)
            .assign(
                Date=lambda df: df.apply(
                    lambda r: pd.to_datetime(
                        f"{r['month']:.0f}/{r['year']:.0f}", format="%m/%Y"
                    ),
                    axis=1,
                )
            )
        )

        return N.set_index("Date")[self.name]

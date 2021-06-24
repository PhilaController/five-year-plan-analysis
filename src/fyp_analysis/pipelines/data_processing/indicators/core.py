import abc
import datetime
import json
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from fyp_analysis import SRC_DIR
from fyp_analysis.extras.datasets.utils import DataclassSchema

# Data directory
DATA_DIR = SRC_DIR / ".." / ".." / "data" / "01_raw" / "indicators"


# Allowed options
ALLOWED_FREQ = ["daily", "weekly", "monthly", "quarterly", "annual"]
ALLOWED_GEO = ["national", "state", "Philadelphia MSA", "Philadelphia"]
ALLOWED_SOURCES = {
    "carto": "DataSourceCARTO",
    "fred": "DataSourceFRED",
    "zillow": "DataSourceZillow",
    "quandl": "DataSourceQuandl",
}


def _as_frame(df):
    """Utility function to ensure input is a data frame."""
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df


@dataclass
class _DataclassMixin(DataclassSchema):
    name: str
    frequency: str
    geography: str
    description: str


class DataSource(_DataclassMixin, abc.ABC):
    """
    An abstract base class to represent a source of economic indicator data.

    Parameters
    ----------
    name: The name of the data series.
    frequency: The data frequency, one of 'daily', 'weekly', 'monthly',
        'quarterly', or 'annual'
    geography: The geography covered by the data, one of 'national',
        'state', 'Philadelphia MSA', 'Philadelphia'
    description: The description of the dataset.
    """

    REGISTRY: List[Any] = []
    JSON: Optional[str] = None

    def __post_init__(self) -> None:
        """Check the values of input arguments."""

        # Check 'frequency' value
        if self.frequency not in ALLOWED_FREQ:
            raise ValueError(f"Allowed values for 'frequency' arg: {ALLOWED_FREQ}")

        # Check 'geography' value
        if self.geography not in ALLOWED_GEO:
            raise ValueError(f"Allowed values for 'geography' arg: {ALLOWED_GEO}")

        # Load the env variables
        load_dotenv()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Add the class to the registry."""
        super().__init_subclass__(**kwargs)
        cls.REGISTRY.append(cls)

    @classmethod
    def get_sources(cls):
        """The available data sources for this type of data."""
        assert cls.JSON is not None

        path = Path(__file__).parent.absolute() / "sources" / cls.JSON
        return json.load(path.open("r"))

    @property
    def local_path(self):
        """The local file path for the dataset."""

        # Get the human-friendly source name
        name = self.__class__.__name__
        lookup = {v: k for k, v in ALLOWED_SOURCES.items()}

        return DATA_DIR / self.frequency / lookup[name] / f"{self.name}.csv"

    @abc.abstractmethod
    def extract(self):
        """Extract the raw data from a remote source."""
        pass

    def transform(self, df: pd.Series) -> pd.Series:
        """Method to post-process the downloaded data."""
        return df

    def load(self, df: pd.Series) -> pd.Series:
        """Save the data locally."""

        # Make sure we have an output directory
        out_dir = self.local_path.parent
        if not out_dir.is_dir():
            out_dir.mkdir(parents=True)

        # Save to the output file
        df.reset_index().to_csv(self.local_path, header=True, index=False)

        return df

    def extract_transform(self) -> pd.Series:
        """Convenience function to extract and transform."""
        return self.transform(self.extract())

    def extract_transform_load(self) -> pd.Series:
        """Convenience function to extract, transform, and load"""
        return self.load(self.extract_transform())

    def get(self, fresh: bool = False) -> pd.Series:
        """Get the data, downloading the data if it is not cached,
        or a fresh copy is requested.

        Args:
            fresh (optional): If True, download a fresh copy of the data,
                regardless of the cache status. Defaults to False.

        Returns:
            The loaded data series.
        """
        # Get the data if we need to
        if fresh or not self.local_path.is_file():
            logger.info(f"Getting fresh copy of '{self.name}' dataset...")
            df = self.extract_transform_load()

        # Load from cache
        else:
            df = pd.read_csv(self.local_path, index_col=0, parse_dates=[0]).squeeze()

        return df


def get_economic_indicators(
    name=None, frequency=None, source=None, geography=None, fresh=False
):
    """
    Return data sets as a single data frame.

    Parameters
    ----------
    name:
    frequency:
    source:
    geography:
    fresh:

    Returns
    -------
    df : pandas.DataFrame
        the data frame holding the indicators
    """
    # Map the sources
    if source is not None:
        source = source.lower()
        if source not in ALLOWED_SOURCES:
            raise ValueError(
                f"Invalid source '{source}'; allowed options are: {list(ALLOWED_SOURCES)}"
            )
        source = ALLOWED_SOURCES[source]

    def filter_by_name(d):
        """Filter by the name of the indicator."""
        return name is None or d["name"] == name

    def filter_by_frequency(d):
        """Filter by the frequency of the indicator."""
        return frequency is None or d["frequency"] == frequency

    def filter_by_source(d):
        """Filter by the source of the indicator."""
        return source is None or d["cls"].__name__ == source

    def filter_by_geography(d):
        """Filter by the geography of the indicator."""
        return geography is None or d["geography"] == geography

    # Get the JSON data for all sources
    SOURCES = [{**d, "cls": cls} for cls in DataSource.REGISTRY for d in cls.SOURCES]

    NOW = datetime.datetime.now()

    # Return the specific name
    if name is not None:

        # Filter by the name
        matches = list(filter(lambda d: d["name"] == name, SOURCES))

        if not len(matches):
            raise ValueError(f"'{name}' is not a valid dataset name.")
        else:
            match = matches[0]
            cls = match.pop("cls")
            return cls.from_dict(match).get(fresh=fresh)

    # Get all of the data sources
    data = []
    for d in filter(
        lambda d: filter_by_frequency(d) & filter_by_source(d) & filter_by_geography(d),
        SOURCES,
    ):
        cls = d.pop("cls")
        data.append(_as_frame(cls.from_dict(d).get(fresh=fresh)))

    # Make sure we got a match
    if not len(data):
        raise ValueError("No datasets found, try relaxing the keyword filters")

    # merge on the datetime index
    result = reduce(
        lambda left, right: pd.merge(
            left, right, how="outer", left_index=True, right_index=True
        ),
        data,
    )

    # Return < today
    return result.loc[:NOW]

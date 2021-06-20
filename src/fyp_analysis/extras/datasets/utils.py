import json
from pathlib import Path
from typing import Dict, Optional, Type, TypeVar, Union

import desert
import numpy as np
import pandas as pd

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="DataclassSchema")


class DataclassSchema:
    """Base class to handled serializing and deserializing dataclasses."""

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """
        Return a new class instance from a dictionary
        representation.

        Parameters
        ----------
        data :
            The dictionary representation of the class.
        """
        schema = desert.schema(cls)
        return schema.load(data)

    @classmethod
    def from_json(cls: Type[T], path_or_json: Union[str, Path]) -> T:
        """
        Return a new class instance from either a file path
        or a valid JSON string.

        Parameters
        ----------
        path_or_json :
            Either the path of the file to load or a valid JSON string.
        """

        # Convert to Path() first to check
        _path = path_or_json
        if isinstance(_path, str):
            _path = Path(_path)
            if not _path.exists():
                raise FileNotFoundError(f"No such file: '{_path}'")
        assert isinstance(_path, Path)

        d = None
        try:  # catch file error too long
            if _path.exists():
                d = json.load(_path.open("r"))
        except OSError:
            pass
        finally:
            if d is None:
                d = json.loads(str(path_or_json))

        return cls.from_dict(d)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the data."""
        schema = desert.schema(self.__class__)
        return schema.dump(self)

    def to_json(self, path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Serialize the object to JSON, either returning a valid JSON
        string or saving to the input file path.

        Parameters
        ----------
        path :
            the file path to save the JSON encoding to
        """

        # Dump to a dictionary
        schema = desert.schema(self.__class__)
        d = schema.dump(self)

        if path is None:
            return json.dumps(d)
        else:
            if isinstance(path, str):
                path = Path(path)
            json.dump(
                d,
                path.open("w"),
            )

            return None


def get_effective_rate_with_pica(rates, pica_share, resident_fraction, start=1992):
    """
    Compute the effective rate, accounting for the PICA share.

    Parameters
    ----------
    rates : pandas.DataFrame
        a DataFrame holding the year, resident, and nonresident columns; it should
        have index 'fiscal_year' and columns 'rate_resident', and 'rate_nonresident'
    pica_share : float
        the percent value that goes to PICA, e.g., 1.5% or 2.0%
    resident_fraction : float
        the fraction of residents to assume, e.g., 0.6; must be less than one
    start : int, optional
        the first year for which PICA received a portion of the revenue

    Returns
    -------
    effective_rate : pandas.Series
        the effective rate (minus the PICA share)
    """
    # Make sure we have all of the neccessary columns
    assert rates.index.name == "fiscal_year"
    assert all(col in rates.columns for col in ["rate_resident", "rate_nonresident"])
    assert 0 <= resident_fraction <= 1.0

    # Get the rates
    rates = rates.copy()
    resident = rates["rate_resident"]
    nonresident = rates["rate_nonresident"]

    # Subtract PICA share from resident part
    valid = rates.index >= start
    resident.loc[valid] -= pica_share

    # Return the linear combo
    return resident * resident_fraction + nonresident * (1 - resident_fraction)


def date_from_fiscal_quarter(row):
    """Return a timestamp from the specified fiscal quarter"""

    fiscal_quarter = row["fiscal_quarter"]
    fiscal_year = row["fiscal_year"]
    if fiscal_quarter == 1:
        dt = f"7/1/{fiscal_year-1:.0f}"
    elif fiscal_quarter == 2:
        dt = f"10/1/{fiscal_year-1:.0f}"
    elif fiscal_quarter == 3:
        dt = f"1/1/{fiscal_year:.0f}"
    elif fiscal_quarter == 4:
        dt = f"4/1/{fiscal_year:.0f}"
    else:
        return np.nan

    return pd.to_datetime(dt)

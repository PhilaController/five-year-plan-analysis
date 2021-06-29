"""Core module for loading quarterly tax data."""
import abc
from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd
from cached_property import cached_property

from fyp_analysis import SRC_DIR

# Registry for taxes
TAXES = {}

# Data directory
HISTORICAL_DIR = SRC_DIR / ".." / ".." / "data" / "01_raw" / "historical"


@dataclass
class QuarterlyTaxData(abc.ABC):
    """
    Abstract base class to load quarterly tax data.

    Notes
    -----
    Historical quarterly data is loaded from 'data / 01_raw / historical / revenues'

    Parameters
    ----------
    latest_historical_year
        the last fiscal year before the Plan starts
    projected_rates
        the projexted rates in the Plan for this tax
    projected_revenues
        the projected revenues in the Plan for this tax
    accrual_method, optional
        how to handle accruals when loading historical data; either 'net' or 'quarters'
    """

    latest_historical_year: int
    projected_rates: pd.DataFrame
    projected_revenues: pd.DataFrame
    accrual_method: str = field(default="net", init=False)

    name: ClassVar[str] = ""

    def __post_init__(self):
        """Check inputs and add new attributes."""
        # Check the allowed values
        allowed = ["net", "quarters"]
        if self.accrual_method not in allowed:
            raise ValueError(f"Allowed values for 'accrual_method': {allowed}")

        self.start_year = 1996
        self.fiscal_years = list(
            range(self.start_year, self.latest_historical_year + 1)
        )
        self.path = HISTORICAL_DIR / "revenues" / "Quarterly.xlsx"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Register the subclass."""
        super().__init_subclass__(**kwargs)
        TAXES[cls.name] = cls

    @cached_property
    def rates(self) -> pd.DataFrame:
        """Return the tax rate data."""
        return self.load_rates()

    @cached_property
    def data(self) -> pd.DataFrame:
        """Return the tax revenue data."""
        return self.load_data()

    @cached_property
    def budget_projections(self):
        """Return the Budget Office's projections."""
        return self.projected_revenues.reset_index(name=f"{self.name}RevenueBudget")

    @abc.abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Each tax should define this function."""
        pass

    @abc.abstractmethod
    def load_rates(self) -> pd.DataFrame:
        """Each tax should define this function."""
        pass

    def _load_raw_rate_data(self, file_tag: str) -> pd.DataFrame:
        """Load the raw tax rate data.

        Notes
        -----
        Data is loaded from the 'historical/rates/' data folder.

        Parameters
        ----------
        file_tag : str
            The name of the file to load, e.g., RTT, BIRT, etc.

        Returns
        -------
            The data frame holding the tax rate data.
        """
        # Read in the raw data
        path = HISTORICAL_DIR / "rates" / f"{file_tag}.csv"
        data = pd.read_csv(path, header=0)

        # Normalize by 100
        for col in data.columns:
            if "rate" in col:
                data[col] = data[col] / 100.0

        return data

    def _load_wide_quarterly_collections(
        self, sheet_name: str, skiprows: int = 4
    ) -> pd.DataFrame:
        """Read quarterly collections data in wide format.

        Parameters
        ----------
        sheet_name : str
            the name of the excel sheet to read from
        skiprows : int
            the number of rows to skip before starting to read

        Returns
        -------
            the data loaded from the file in tidy format

        Raises
        ------
        ValueError
            If loading data fails
        """
        # Number of columns is years + 1 for index
        nyears = len(self.fiscal_years)
        ncols = nyears + 1

        # Read the raw data
        df = (
            pd.read_excel(
                self.path,
                sheet_name=sheet_name,
                skiprows=skiprows,
                usecols=list(range(ncols)),
                nrows=8,
                index_col=0,
            )
            .drop(["Subtotal", "Total"])
            .rename_axis("fiscal_quarter")
            .reset_index()
        )

        # Validate the fiscal year columns
        if not df.columns[1:].astype(str).str.strip().str.match("[0-9]{4}").all():
            raise ValueError(
                "Error in reading data — the 'latest_historical_year' should be one year before the current Plan"
            )

        # Add Net accrual
        if self.accrual_method == "net":
            net_accrual = df.iloc[-2:].sum(axis=0)
            net_accrual["fiscal_quarter"] = "Net Accrual"
            df = df.append(net_accrual, ignore_index=True)
        # Handle by the quarter
        # NOTE: This is important for BIRT/NPT due to shifted dates in FY20
        else:
            # Add Prior Year Accrual to Q1
            q1 = df["fiscal_quarter"] == 1
            prior = df["fiscal_quarter"] == "PY Accrual"
            df.loc[q1, self.fiscal_years] += df.loc[prior, self.fiscal_years].values

            # Add current year to Q4
            q4 = df["fiscal_quarter"] == 4
            current = df["fiscal_quarter"] == "CY Accrual"
            df.loc[q4, self.fiscal_years] += df.loc[current, self.fiscal_years].values

        # Melt into long format
        revenue_col = f"{self.name}Revenue"
        df = df.melt(
            value_name=revenue_col,
            id_vars=["fiscal_quarter"],
            var_name="fiscal_year",
        )

        # Add the net accrual
        if self.accrual_method == "net":
            q4_plus_accrual = (
                df.query("fiscal_quarter in [4, 'Net Accrual']")
                .groupby("fiscal_year")[revenue_col]
                .sum()
            )

            q4 = df.fiscal_quarter == 4
            df.loc[q4, revenue_col] = q4_plus_accrual.values

        # Remove accrual values
        df = df.query("fiscal_quarter in [1, 2, 3, 4]").copy()

        # Convert columns to int
        for col in ["fiscal_year", "fiscal_quarter"]:
            df[col] = df[col].astype(int)

        return df

    def tax_base_to_revenue(self, tax_base: pd.Series) -> pd.Series:
        """Convert tax base to revenue.

        Raises
        ------
        ValueError
            If index of input series is not named 'fiscal_year'

        Parameters
        ----------
        tax_base : pandas Series
            The input tax base data as a pandas Series

        Returns
        -------
        The revenue data
        """
        # Check the tax base index —> must be by fiscal year
        if tax_base.index.name != "fiscal_year":
            raise ValueError("Input tax base should be aggregated by fiscal year")

        # Get the rates
        rates = self.rates.set_index("fiscal_year")
        rate_col = "combined_rate"
        if rate_col not in rates.columns:
            rate_col = "rate"

        # Multiply base by rate
        data = pd.merge(tax_base, rates[rate_col], left_index=True, right_index=True)
        return (data[tax_base.name] * data[rate_col]).rename(f"{self.name}Revenue")

    def get_budget_comparison(self, tax_base: pd.Series) -> pd.DataFrame:
        """Get the comparison between input tax base and Budget projections."""
        # Convert to revenue
        revenue = self.tax_base_to_revenue(tax_base)

        # Combine
        out = (
            pd.merge(
                self.budget_projections,
                revenue.reset_index(),
                on="fiscal_year",
                how="outer",
            )
            .set_index("fiscal_year")
            .sort_index()
        )

        # Fill the missing values with actuals
        out[f"{self.name}RevenueBudget"] = out[f"{self.name}RevenueBudget"].fillna(
            out[f"{self.name}Revenue"]
        )

        # Rename the columns
        return out.rename(
            columns={
                f"{self.name}RevenueBudget": "Five Year Plan",
                f"{self.name}Revenue": "Controller",
            }
        )

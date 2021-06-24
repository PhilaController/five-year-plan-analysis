import pandas as pd

from .core import QuarterlyTaxData


class SalesTax(QuarterlyTaxData):
    """Sales tax data."""

    name = "Sales"

    def load_rates(self):
        """Load tax rates"""
        return pd.concat(
            [
                self._load_raw_rate_data("Sales").set_index("fiscal_year"),
                self.projected_rates.to_frame(),
            ]
        ).reset_index()

    def load_data(self):
        """Return revenue and base data."""

        # Load the raw data
        df = self._load_wide_quarterly_collections("Sales")

        # Merge in the rates
        df = pd.merge(df, self.load_rates(), on="fiscal_year")

        # Handle mid-year tax rate change
        valid = (df["fiscal_year"] == 2010) & (df["fiscal_quarter"].isin([1, 2]))
        df.loc[valid, "rate"] = 0.01
        valid = (df["fiscal_year"] == 2010) & (df["fiscal_quarter"].isin([3, 4]))
        df.loc[valid, "rate"] = 0.02

        return df.assign(SalesBase=lambda df: df.SalesRevenue / df.rate)

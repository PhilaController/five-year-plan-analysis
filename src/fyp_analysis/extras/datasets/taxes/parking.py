"""Class for loading Parking Tax data."""
import pandas as pd

from .core import QuarterlyTaxData


class ParkingTax(QuarterlyTaxData):
    """Parking tax data."""

    name = "Parking"

    def load_rates(self):
        """Load tax rates"""
        return pd.concat(
            [
                self._load_raw_rate_data("Parking").set_index("fiscal_year"),
                self.projected_rates,
            ]
        ).reset_index()

    def load_data(self):
        """Return revenue and base data"""

        # Load the raw data
        df = self._load_wide_quarterly_collections("Parking")

        # Merge in the rates
        return pd.merge(df, self.load_rates(), on="fiscal_year").assign(
            ParkingBase=lambda df: df.ParkingRevenue / df.rate
        )

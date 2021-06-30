"""Class for loading Amusement Tax data."""
import pandas as pd

from .core import QuarterlyTaxData


class AmusementTax(QuarterlyTaxData):
    """Amusement tax data."""

    name = "Amusement"
    accrual_method = "quarters"

    def load_rates(self):
        """Load tax rates."""
        return pd.concat(
            [
                self._load_raw_rate_data("Amusement").set_index("fiscal_year"),
                self.projected_rates.to_frame(),
            ]
        ).reset_index()

    def load_data(self):
        """Return revenue and base data."""
        # Load the raw data
        df = self._load_wide_quarterly_collections("Amusement")

        # Merge in the rates
        return pd.merge(df, self.load_rates(), on="fiscal_year").assign(
            AmusementBase=lambda df: df.AmusementRevenue / df.rate
        )

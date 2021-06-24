"""Class for loading Realty Transfer Tax data."""
import pandas as pd

from .core import QuarterlyTaxData


class RealtyTransferTax(QuarterlyTaxData):
    """Realty transfer tax data."""

    name = "RTT"

    def load_rates(self):
        """Load tax rates."""
        return pd.concat(
            [
                self._load_raw_rate_data("RTT").set_index("fiscal_year"),
                self.projected_rates.to_frame(),
            ]
        ).reset_index()

    def load_data(self):
        """Return revenue and base data."""
        # Load the raw data
        df = self._load_wide_quarterly_collections("RTT")

        # Merge in the rates
        return pd.merge(df, self.load_rates(), on="fiscal_year").assign(
            RTTBase=lambda df: df.RTTRevenue / df.rate
        )

"""Class for loading Net Profits Tax data."""
from dataclasses import dataclass

import pandas as pd

from ..utils import get_effective_rate_with_pica
from .core import QuarterlyTaxData


@dataclass
class NetProfitsTax(QuarterlyTaxData):
    """Current year net profits tax data."""

    resident_fraction: float
    name = "NPT"
    accrual_method = "quarters"

    def __post_init__(self):

        # Call the base init
        super().__post_init__()

        # Check valid range
        valid_range = 0 <= self.resident_fraction <= 1.0
        if not valid_range:
            raise ValueError("'resident_fraction' should be between 0 and 1")

    def load_rates(self):
        """Load tax rates."""
        # Merge the raw historical data and projected data
        rates = pd.concat(
            [
                self._load_raw_rate_data("NPT").set_index("fiscal_year"),
                self.projected_rates,
            ]
        )

        # Get the effective rate but subtracting PICA portion
        rates["combined_rate"] = get_effective_rate_with_pica(
            rates,
            pica_share=0.02,
            resident_fraction=self.resident_fraction,
            start=1992,
        )

        # Return
        return rates.reset_index()

    def load_data(self):
        """Return revenue and base data."""
        # Load the raw data
        df = self._load_wide_quarterly_collections("NPT")

        # Merge in the rates
        return pd.merge(df, self.load_rates(), on="fiscal_year").assign(
            NPTBase=lambda df: df.NPTRevenue / df.combined_rate
        )

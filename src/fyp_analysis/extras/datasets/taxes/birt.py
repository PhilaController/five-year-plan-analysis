"""Class for loading BIRT data."""
import pandas as pd
from cached_property import cached_property

from .core import HISTORICAL_DIR, QuarterlyTaxData


class BIRT(QuarterlyTaxData):
    """BIRT data."""

    name = "BIRT"
    accrual_method = "quarters"

    @cached_property
    def splits(self):
        """Load net income / gross receipts breakdown."""
        path = HISTORICAL_DIR / "BIRT-splits.xlsx"
        return pd.read_excel(path).assign(
            gross_receipts_fraction=lambda df: 1 - df.net_income_fraction
        )

    def load_rates(self):
        """Load tax rates."""
        return pd.concat(
            [
                self._load_raw_rate_data("BIRT").set_index("fiscal_year"),
                self.projected_rates,
            ]
        ).reset_index()

    def load_data(self):
        """Return revenue and base data."""
        # Load the raw data
        df = self._load_wide_quarterly_collections("BIRT")

        # Merge in the rates
        return pd.merge(
            pd.merge(df, self.rates, on="fiscal_year"), self.splits, on="fiscal_year"
        ).assign(
            GrossReceiptsRevenue=lambda df: df.BIRTRevenue * df.gross_receipts_fraction,
            GrossReceiptsBase=lambda df: df.GrossReceiptsRevenue
            / df.gross_receipts_rate,
            NetIncomeRevenue=lambda df: df.BIRTRevenue * df.net_income_fraction,
            NetIncomeBase=lambda df: df.NetIncomeRevenue / df.net_income_rate,
        )

    # def tax_base_to_revenue(self, tax_base, kind):
    #     """Convert gross receipts or net income tax base to revenue."""

    #     assert kind in ["gross_receipts", "net_income"]
    #     assert tax_base.index.name == "fiscal_year"

    #     # Get the rates / fraction
    #     rate = self.rates.set_index("fiscal_year")[f"{kind}_rate"]

    #     # Merge
    #     data = pd.merge(
    #         tax_base,
    #         rate,
    #         left_index=True,
    #         right_index=True,
    #     )
    #     name = "GrossReceipts" if kind == "gross_receipts" else "NetIncome"
    #     return (data[tax_base.name] * data[f"{kind}_rate"]).rename(f"{name}Revenue")

    # def get_mayor_comparison(self, *tax_bases):
    #     """Get the comparison between input tax base and mayor projections"""

    #     # Check input
    #     assert len(tax_bases) == 2
    #     tax_bases = pd.concat(list(tax_bases), axis=1)
    #     assert "GrossReceiptsBase" in tax_bases.columns
    #     assert "NetIncomeBase" in tax_bases.columns

    #     # Convert to revenue
    #     gross_receipts = self.tax_base_to_revenue(
    #         tax_bases["GrossReceiptsBase"], "gross_receipts"
    #     )
    #     net_income = self.tax_base_to_revenue(tax_bases["NetIncomeBase"], "net_income")
    #     revenue = gross_receipts + net_income

    #     # Combine
    #     return (
    #         pd.merge(
    #             self.mayor_projections,
    #             revenue.reset_index(name=f"{self.name}Revenue"),
    #             on="fiscal_year",
    #             how="outer",
    #         )
    #         .set_index("fiscal_year")
    #         .sort_index()
    #     )

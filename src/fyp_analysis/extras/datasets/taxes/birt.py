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
            / df.rate_gross_receipts,
            NetIncomeRevenue=lambda df: df.BIRTRevenue * df.net_income_fraction,
            NetIncomeBase=lambda df: df.NetIncomeRevenue / df.rate_net_income,
        )

    def tax_base_to_revenue(self, tax_base, kind):
        """Convert gross receipts or net income tax base to revenue."""

        assert kind in ["gross_receipts", "net_income"]
        if tax_base.index.name != "fiscal_year":
            raise ValueError("Input tax base should be aggregated by fiscal year")

        # Get the rates / fraction
        rate = self.rates.set_index("fiscal_year")[f"rate_{kind}"]

        # Merge
        data = pd.merge(
            tax_base,
            rate,
            left_index=True,
            right_index=True,
        )
        name = "GrossReceipts" if kind == "gross_receipts" else "NetIncome"
        return (data[tax_base.name] * data[f"rate_{kind}"]).rename(
            f"{self.name}Revenue"
        )

    def get_budget_comparison(self, *tax_bases):
        """Get the comparison between input tax base and mayor projections"""

        # Check input
        assert len(tax_bases) == 2
        tax_bases = pd.concat(list(tax_bases), axis=1)
        assert "GrossReceiptsBase" in tax_bases.columns
        assert "NetIncomeBase" in tax_bases.columns

        # Convert to revenue
        gross_receipts = self.tax_base_to_revenue(
            tax_bases["GrossReceiptsBase"], "gross_receipts"
        )
        net_income = self.tax_base_to_revenue(tax_bases["NetIncomeBase"], "net_income")
        revenue = gross_receipts + net_income

        # Combine
        out = (
            pd.merge(
                self.budget_projections,
                revenue.reset_index(name=f"{self.name}Revenue"),
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

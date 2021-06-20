from dataclasses import dataclass
from functools import reduce

import pandas as pd

from .plan_details import PlanDetails
from .taxes import TAXES
from .utils import date_from_fiscal_quarter


@dataclass
class Taxes:
    """
    Class for handling tax data in a Five Year Plan analysis.

    Parameters
    ----------
    plan_details
        the object holding the projected rates and revenues in the Five Year Plan

    Attributes
    ----------
    latest_historical_year
        this is the last fiscal year before the Plan starts
    taxes
        a dict holding the individual tax objects

    """

    plan_details: PlanDetails

    def __post_init__(self):

        # Latest historical year
        self.latest_historical_year = self.plan_details.fiscal_years[0] - 1

        # Initialize the taxes
        self.taxes = {}
        for name in TAXES:

            # Need the latest actual year
            kws = {"latest_historical_year": self.latest_historical_year}

            # Add resident fractions
            if name == "Wage":
                kws["resident_fraction"] = (
                    self.plan_details.resident_fractions.Wage / 100
                )
            elif name == "NPT":
                kws["resident_fraction"] = (
                    self.plan_details.resident_fractions.NPT / 100
                )

            # Add in the projected rates and revenues
            kws["projected_rates"] = self.plan_details.get_projected_rates(name) / 100
            kws["projected_revenues"] = self.plan_details.get_projected_revenues(name)

            # Initialize
            self.taxes[name] = TAXES[name](**kws)

    def __getitem__(self, key):
        """Convenience function to return tax objects in dict-like fashion."""
        if key in self.taxes:
            return self.taxes[key]
        else:
            raise KeyError(f"'{key}' is not a valid tax name")

    def __iter__(self):
        """Iterate over the taxes dict."""
        yield from self.taxes

    def get_all_tax_bases(self) -> pd.DataFrame:
        """Load tax base data for all taxes."""

        # Combine taxes
        def get_cols(columns):
            cols = [col for col in columns if col.endswith("Base")]
            return cols + ["fiscal_year", "fiscal_quarter"]

        # Merge base data together
        result = reduce(
            lambda left, right: pd.merge(
                left, right, how="outer", on=["fiscal_year", "fiscal_quarter"]
            ),
            [t.data[get_cols(t.data.columns)] for name, t in self.taxes.items()],
        )

        # Add the Date index and return
        return (
            result.set_index(result.apply(date_from_fiscal_quarter, axis=1))
            .rename_axis("Date")
            .reset_index()
            .dropna(subset=["Date"])
            .set_index("Date")
            .drop(labels=["fiscal_year", "fiscal_quarter"], axis=1)
        )

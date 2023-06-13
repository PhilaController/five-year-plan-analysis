from dataclasses import dataclass, fields, make_dataclass
from typing import Dict, Iterator, List, Literal, Optional, Union

import pandas as pd
import yaml
from kedro.extras.datasets.yaml import YAMLDataSet

from ... import SRC_DIR
from .taxes import TAX_NAMES
from .utils import DataclassSchema


class EnhancedDataclass:
    """Add some enhancements to the builtin Dataclass."""

    def __iter__(self) -> Iterator[str]:
        yield from sorted([f.name for f in fields(self)])

    def __getitem__(self, key: str):
        return getattr(self, key)


# The Revenues class
Revenues = make_dataclass(
    "Revenues", [(name, List[float]) for name in TAX_NAMES], bases=(EnhancedDataclass,)
)


# The Rates class
Rates = make_dataclass(
    "Rates",
    [(name, Dict[str, List[float]]) for name in TAX_NAMES],
    bases=(EnhancedDataclass,),
)


@dataclass
class BIRTSplits(DataclassSchema):
    """The BIRT splits between Net Income and Gross Receipts."""

    net_income_fraction: List[float]

    @property
    def gross_receipts_fraction(self):
        return [100 - f for f in self.net_income]


@dataclass
class ResidentFractions(DataclassSchema):
    """Assumptions for the percent of tax base
    represented by residents and non-residents."""

    Wage: float
    NPT: float


@dataclass
class PlanDetails(DataclassSchema):
    """
    Details for a proposed/adopted Five Year Plan.

    Parameters
    ----------
    kind :
        either 'Proposed' or 'Adopted'
    fiscal_years :
        list of the fiscal years in the Plan
    revenues :
        the tax revenue data
    rates :
        the tax rate data
    resident_fractions :
        the fraction of residents in the tax base
    birt_splits :
        the breakdown between BIRT components
    """

    kind: str
    fiscal_years: List[int]
    revenues: Revenues  # type: ignore
    rates: Rates  # type: ignore
    resident_fractions: ResidentFractions
    birt_splits: BIRTSplits

    def __repr__(self):
        first = str(self.fiscal_years[0])[-2:]
        last = str(self.fiscal_years[-1])[-2:]
        return f"FiveYearPlanDetails('FY{first}-FY{last} {self.kind}')"

    def __post_init__(self):

        # Validate "kind"
        if self.kind not in ["Proposed", "Adopted"]:
            raise ValueError("Valid 'kind' values: 'Proposed' or 'Adopted'")

        # Validate "fiscal_years"
        if len(self.fiscal_years) != 5:
            raise ValueError("'fiscal_years' should have length 5")

        # Validate revenues
        for name in self.revenues:
            if len(self.revenues[name]) != len(self.fiscal_years):
                raise ValueError(f"Revenues for {name} has the wrong length")

        # Validate rates
        for name in self.rates:
            d = self.rates[name]
            for col in d:
                if len(d[col]) != len(self.fiscal_years):
                    raise ValueError(f"Rates for {name} has the wrong length")

    def get_projected_revenues(
        self, tax_name: Optional[str] = None
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Get the tax revenue data in the plan. If no tax name is specified,
        return all tax revenues.

        Parameters
        ----------
        tax_name :
            the optional name of the tax revenue to return
        """
        # Make sure the name is valid
        if tax_name is not None and tax_name not in self.revenues:  # type: ignore
            raise ValueError(f"Valid tax names: {list(self.revenues)}")

        # Which tax names to get
        if tax_name is None:
            tax_names = list(self.revenues)
        else:
            tax_names = [tax_name]

        return pd.DataFrame(
            {name: self.revenues[name] for name in tax_names},  # type: ignore
            index=pd.Index(self.fiscal_years, name="fiscal_year"),
        ).squeeze()

    def get_projected_rates(self, tax_name):
        """Get the tax rate data in the plan for the specified tax."""
        # Make sure name is valid
        if tax_name not in self.rates:
            raise ValueError(f"Valid tax names: {list(self.rates)}")

        return pd.DataFrame(
            self.rates[tax_name],
            index=pd.Index(self.fiscal_years, name="fiscal_year"),
        ).squeeze()

    @classmethod
    def from_file(cls, plan_type: Literal["proposed", "adopted"], plan_start_year: int):
        """
        Load the plan details from file.

        Parameters
        ----------
        plan_type :
            either 'proposed' or 'adopted'
        plan_start_year :
            first year of the plan
        """
        # Check input types
        plan_type = plan_type.lower()
        if plan_type not in ["proposed", "adopted"]:
            raise ValueError("Allowed plan types: 'proposed', 'adopted'")

        # First and last fiscal year
        first = str(plan_start_year)[2:]
        last = str(plan_start_year + 4)[2:]

        # Get the file path
        filename = f"FY{first}-FY{last}-{plan_type.capitalize()}.yml"
        filepath = SRC_DIR / ".." / ".." / "data" / "01_raw" / "plans" / filename
        filepath = filepath.absolute().resolve()
        if not filepath.exists():
            raise FileNotFoundError(f"No file found at path: '{str(filepath)}'")

        # Load data
        with filepath.open("r") as ff:
            data = yaml.safe_load(ff)

        # Format the rates
        assert "rates" in data
        for tax_name in data["rates"]:
            value = data["rates"][tax_name]
            if isinstance(value, list):
                data["rates"][tax_name] = {"rate": value}
            elif isinstance(value, dict):
                data["rates"][tax_name] = {f"rate_{k}": v for (k, v) in value.items()}
            else:
                raise ValueError("Error parsing rate info in YAML file.")

        # Format birt splits
        assert "net_income_fraction" in data
        value = data.pop("net_income_fraction")
        data["birt_splits"] = {"net_income_fraction": value}

        # Initialize and return from dict
        return cls.from_dict(data)


class PlanDetailsYAMLDataSet(YAMLDataSet):
    def _load(self) -> PlanDetails:

        # Load the data as a dictionary
        data = super()._load()

        # Format the rates
        assert "rates" in data
        for tax_name in data["rates"]:
            value = data["rates"][tax_name]
            if isinstance(value, list):
                data["rates"][tax_name] = {"rate": value}
            elif isinstance(value, dict):
                data["rates"][tax_name] = {f"rate_{k}": v for (k, v) in value.items()}
            else:
                raise ValueError("Error parsing rate info in YAML file.")

        # Format birt splits
        assert "net_income_fraction" in data
        value = data.pop("net_income_fraction")
        data["birt_splits"] = {"net_income_fraction": value}

        return PlanDetails.from_dict(data)

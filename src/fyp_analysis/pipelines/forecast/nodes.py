from typing import Dict, List, Literal

import pandas as pd
import yaml
from kedro.io import DataCatalog
from loguru import logger
from matplotlib import pyplot as plt

from ... import SRC_DIR
from ...extras.datasets import PlanDetails, Taxes
from .predict import get_prophet_forecast, get_var_forecast, plot_projection_comparison
from .predict import report_forecast_results as _report_forecast_results


def run_forecasts(
    unscaled_features: pd.DataFrame,
    stationary_guide: pd.DataFrame,
    plan_start_year: int,
    plan_type: Literal["proposed", "adopted"],
    cbo_forecast_date: str,
    forecast_types: List[Dict[str, Literal["file", "var", "prophet"]]],
):
    """Run the forecasts."""

    # The catalog path
    catalog_path = SRC_DIR / ".." / ".." / "conf" / "base" / "catalog.yml"
    catalog_config = yaml.load(catalog_path.open("r"), Loader=yaml.Loader)
    catalog = DataCatalog.from_config(catalog_config)

    # Get the tax names
    tax_names = list(forecast_types)

    # Loop over each tax and get the parameters
    tax_bases = []
    formatted_tax_names = []
    for tax_name in tax_names:
        # Forecast kind
        forecast_type = forecast_types[tax_name]

        # Format the tax name
        tax_name_formatted = "".join([w.capitalize() for w in tax_name.split("_")])
        if tax_name_formatted in ["Rtt", "Npt"]:
            tax_name_formatted = tax_name_formatted.upper()

        # Log
        logger.info(f"Calculating forecast for {tax_name_formatted}...")

        # The name of the tax base
        tax_base_name = f"{tax_name_formatted}Base"

        # Run the forecast
        if forecast_type in ["var", "prophet"]:
            # Try to load the fit params
            try:
                fit_params = catalog.load(f"{tax_name}_fit_params")
            except:
                raise ValueError(f"No fit params for tax '{tax_name_formatted}'")

            # Make sure fit params are a list, not a single dict
            if isinstance(fit_params, dict):
                fit_params = [fit_params]

            if forecast_type == "var":
                tax_base_forecast = get_var_forecast(
                    unscaled_features,
                    stationary_guide,
                    fit_params,
                    tax_base_name,
                    plan_start_year,
                    cbo_forecast_date,
                )
            else:
                tax_base_forecast = get_prophet_forecast(
                    fit_params, unscaled_features, tax_base_name, plan_start_year
                )

        # Load from file
        elif forecast_type == "file":
            # Try to load the forecast from file
            try:
                tax_base_forecast = catalog.load(f"{tax_name}_tax_base_forecast")
            except:
                raise ValueError(
                    f"No tax base forecast to load for tax '{tax_name_formatted}'"
                )

        else:
            raise ValueError(f"Unknown forecast type '{forecast_type}'")

        tax_bases.append(tax_base_forecast)
        formatted_tax_names.append(tax_name_formatted)

    # Combine into a dataframe
    tax_bases = pd.concat(tax_bases, axis=1)

    # Plan details
    plan_details = PlanDetails.from_file(plan_type, plan_start_year)

    # Get the revenues too
    tax_revenues = []
    taxes = Taxes(plan_details)

    # Initialize figures directory
    figures_dir = (
        SRC_DIR / ".." / ".." / "data" / "06_model_output" / "forecast_figures"
    )
    if not figures_dir.exists():
        figures_dir.mkdir()

    # Add birt
    tax_revenues.append(
        taxes["BIRT"]
        .get_budget_comparison(
            tax_bases["NetIncomeBase"], tax_bases["GrossReceiptsBase"]
        )
        .assign(tax_name="BIRT")
    )

    # Plot birt
    plot_projection_comparison(
        taxes["BIRT"], tax_bases["NetIncomeBase"], tax_bases["GrossReceiptsBase"]
    )
    plt.savefig(figures_dir / "BIRT.png")

    # Do the rest
    for i, col in enumerate(tax_bases.columns):
        # Skip BIRT
        if col in ["NetIncomeBase", "GrossReceiptsBase"]:
            continue
        logger.info(col)

        tax_name = formatted_tax_names[i]
        this_tax = taxes[tax_name]
        tax_revenues.append(
            this_tax.get_budget_comparison(tax_bases[col]).assign(tax_name=tax_name)
        )

        # Plot too
        plot_projection_comparison(this_tax, tax_bases[col])
        plt.savefig(figures_dir / f"{tax_name}.png")

    # Combine into a dataframe
    tax_revenues = pd.concat(tax_revenues, axis=0).reset_index()

    # Add BIRT base
    tax_bases["BIRTBase"] = tax_bases[["NetIncomeBase", "GrossReceiptsBase"]].sum(
        axis=1
    )

    return tax_bases, tax_revenues


def report_forecast_results(plan_start_year, tax_revenues, tax_bases):
    return _report_forecast_results(plan_start_year, tax_revenues, tax_bases)

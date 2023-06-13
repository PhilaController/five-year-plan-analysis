"""Load historical data."""
import shutil
import tempfile
from pathlib import Path

import click
import numpy as np
import openpyxl
import pandas as pd
from loguru import logger

from . import SRC_DIR

PHL_BUDGET_REPO = "https://raw.githubusercontent.com/PhilaController/phl-budget-data"


@click.command()
def update_quarterly_collections():
    """
    Update the quarterly collection actuals in the
    following spreadsheet:

    "data/01_raw/historical/revenues/Quarterly.xlsx"
    """

    # All
    df = pd.read_csv(
        f"{PHL_BUDGET_REPO}/main/src/phl_budget_data/data/processed/collections/city-tax-collections.csv"
    )
    latest_date = df["date"].max()

    # Add fiscal quarter
    df["fiscal_quarter"] = np.select(
        [
            df["fiscal_month"].isin([1, 2, 3]),
            df["fiscal_month"].isin([4, 5, 6]),
            df["fiscal_month"].isin([7, 8, 9]),
            df["fiscal_month"].isin([10, 11, 12]),
        ],
        [1, 2, 3, 4],
    )

    # Subsets for each tax we need
    queries = [
        "name in ['wage_city', 'earnings_city'] and kind == 'current'",
        "name == 'birt' and kind == 'total'",
        "name == 'real_estate_transfer' and kind == 'total'",
        "name == 'net_profits_city' and kind == 'current'",
        "name == 'parking' and kind == 'total'",
        "name == 'amusement' and kind == 'total'",
        "name == 'soda' and kind == 'total'",
    ]

    # Output path
    DATA_DIR = SRC_DIR / ".." / ".." / "data"
    data_dir = DATA_DIR / "01_raw" / "historical" / "revenues"
    path = data_dir / "Quarterly.xlsx"

    # Log it
    relpath = path.relative_to(DATA_DIR)
    logger.info(f"Updating data in data/{relpath}")

    # Work in a temp folder
    with tempfile.TemporaryDirectory() as tmpdir:

        # Copy over template
        tmpfile = Path(tmpdir) / "Quarterly.xlsx"
        shutil.copy(path, tmpfile)

        # Load the file
        with pd.ExcelWriter(
            tmpfile, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        ) as writer:

            # Add latest date
            sheet_name = "Latest Collections Data"
            sheet = writer.book[sheet_name]
            sheet["B4"] = latest_date

            start_row = 6
            for i, query in enumerate(queries):

                # Get the subset
                sub = df.query(query)

                # Pivot
                min_count = 6 if i == 0 else 3
                X = (
                    sub.groupby(["fiscal_year", "fiscal_quarter"], as_index=False)[
                        "total"
                    ]
                    .sum(min_count=min_count)
                    .pivot_table(
                        columns="fiscal_year", index="fiscal_quarter", values="total"
                    )
                ).sort_index()

                # Save
                X.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    startrow=start_row,
                    startcol=1 if "soda" not in query else 3,
                    index=False,
                )

                start_row += 7

        # Copy back
        tmpfile = Path(tmpdir) / "Quarterly.xlsx"
        shutil.copy(tmpfile, path)


if __name__ == "__main__":
    update_quarterly_collections()

import numpy as np
import openpyxl
import pandas as pd
from loguru import logger
from phl_budget_data.clean import load_city_tax_collections

from . import SRC_DIR


def update_quarterly_collections():
    """
    Update the quarterly collection actuals in the
    following spreadsheet:

    "data/01_raw/historical/revenues/Quarterly.xlsx"
    """

    # All
    df = load_city_tax_collections()
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
    ]

    # Output path
    DATA_DIR = SRC_DIR / ".." / ".." / "data"
    data_dir = DATA_DIR / "01_raw" / "historical" / "revenues"
    path = data_dir / "Quarterly.xlsx"

    # Log it
    relpath = path.relative_to(DATA_DIR)
    logger.info(f"Updating data in data/{relpath}")

    # Read the book
    book = openpyxl.load_workbook(path)

    # Add latest date
    sheet_name = "Latest Collections Data"
    sheet = book[sheet_name]
    sheet["B4"] = latest_date

    start_row = 6
    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        # Copy over the sheets
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        for i, query in enumerate(queries):

            # Get the subset
            sub = df.query(query)

            # Pivot
            min_count = 6 if i == 0 else 3
            X = (
                sub.groupby(["fiscal_year", "fiscal_quarter"], as_index=False)["total"]
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
                startcol=1,
                index=False,
            )

            start_row += 7

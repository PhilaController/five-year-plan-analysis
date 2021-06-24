import re

import pandas as pd

from ... import SRC_DIR

DATA_DIR = SRC_DIR / ".." / ".." / "data" / "01_raw" / "cbo"


def load_cbo_data(date="latest"):
    """
    Load economic projections from the Congressional
    Budget Offic (CBO).

    See 10-year projections at:
    https://www.cbo.gov/data/budget-economic-data#4

    Parameters
    ----------
    date : str
        either "latest" or the month to load in format YYYY-MM
    """

    # Pull the latest set of projections
    if date == "latest":
        path = sorted(DATA_DIR.glob("*.xlsx"), reverse=True)[0]
    # Pick a specific date
    else:
        if not re.match("[0-9]{4}-[0-9]{2}", date):
            raise ValueError("Date should be in format YYYY-MM")
        files = list(DATA_DIR.glob(f"{date}*.xlsx"))
        if not len(files):
            raise ValueError(f"No files found for date '{date}'")
        path = files[0]

    # Read the raw data
    cbo = pd.read_excel(
        path,
        sheet_name="1. Quarterly",
        usecols="B:BH",
        skiprows=6,
    ).dropna(how="all", axis=0)

    # Columns to rename
    rename = {
        "Real GDP": "RealGDP",
        "Price Index, Personal Consumption Expenditures (PCE)": "PCEPriceIndex",
        "Consumer Price Index, All Urban Consumers (CPI-U)": "CPIU",
        "GDP Price Index": "GDPPriceIndex",
        "Price of Crude Oil, West Texas Intermediate (WTI)": "OilPriceWTI",
        "FHFA House Price Index, Purchase Only": "FHFAHousePriceIndex",
        "Unemployment Rate, Civilian, 16 Years or Older": "UnemploymentRate",
        "Employment, Total Nonfarm (Establishment Survey)": "NonfarmEmployment",
        "10-Year Treasury Note": "10YearTreasury",
        "3-Month Treasury Bill": "3MonthTreasury",
        "Federal Funds Rate": "FedFundsRate",
        "Income, Personal": "PersonalIncome",
        "Wages and Salaries": "Wage&Salaries",
        "Profits, Corporate, With IVA & CCAdj": "CorporateProfits",
        "Personal Consumption Expenditures": "PCE",
        "Nonresidential fixed investment": "NonresidentialInvestment",
        "Residential fixed investment": "ResidentialInvestment",
    }

    # Format
    X = (
        cbo.loc[[5, 40, 44, 50, 55, 57, 61, 67, 80, 81, 82, 85, 89, 103, 109, 113, 115]]
        .rename(columns={"Unnamed: 1": "var1", "Unnamed: 2": "var2"})
        .assign(var1=lambda df: df["var1"].fillna(df["var2"]))
        .drop(labels=["var2", "Units"], axis=1)
        .melt(id_vars=["var1"], var_name="Date")
        .assign(
            Date=lambda df: pd.to_datetime(df.Date),
            var1=lambda df: df.var1.str.strip()
            .str.lower()
            .map({k.lower(): v for k, v in rename.items()}),
        )
        .pivot_table(columns="var1", index="Date", values="value")
        .assign(NonfarmEmployment=lambda df: df.NonfarmEmployment * 1e3)
    )

    return X

"""Commercial metrics and life-sciences business logic."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_monthly_market_share(pharma: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly brand TRx market share within the GLP-1 class."""
    result = pharma.copy()
    monthly_total = result.groupby("Month")["TRx"].transform("sum")
    result["TRx_Market_Share"] = np.where(
        monthly_total > 0,
        result["TRx"] / monthly_total,
        0.0,
    )
    return result[
        ["Month", "Brand_Name", "TRx", "TRx_Market_Share"]
    ].sort_values(["Month", "Brand_Name"])


def calculate_annual_market_share(pharma: pd.DataFrame) -> pd.DataFrame:
    """Calculate annual brand TRx market share within the GLP-1 class."""
    annual = (
        pharma.assign(Year=pharma["Month"].dt.year)
        .groupby(["Year", "Brand_Name"], as_index=False)["TRx"]
        .sum()
    )
    annual_total = annual.groupby("Year")["TRx"].transform("sum")
    annual["TRx_Market_Share"] = np.where(
        annual_total > 0,
        annual["TRx"] / annual_total,
        0.0,
    )
    return annual.sort_values(["Year", "Brand_Name"]).reset_index(drop=True)


def _first_positive_year_value(group: pd.DataFrame, value_col: str) -> tuple:
    """Return first/last positive annual observation for a segment."""
    positive = group[group[value_col] > 0].sort_values("Year")
    if positive.empty:
        return np.nan, np.nan, np.nan, np.nan
    first = positive.iloc[0]
    last = positive.iloc[-1]
    return first["Year"], first[value_col], last["Year"], last[value_col]


def calculate_segment_cagr(
    data: pd.DataFrame,
    segment_col: str,
    value_col: str,
) -> pd.DataFrame:
    """Calculate segment CAGR using annual totals across available years.

    CAGR is computed from the first positive annual value to the last positive
    annual value. This avoids treating pre-launch zero prescription volume as
    an economic starting point for later entrants.
    """
    annual = (
        data.assign(Year=data["Month"].dt.year)
        .groupby(["Year", segment_col], as_index=False)[value_col]
        .sum()
    )

    records = []
    for segment, group in annual.groupby(segment_col):
        start_year, start_value, end_year, end_value = _first_positive_year_value(
            group, value_col
        )
        periods = end_year - start_year if pd.notna(start_year) else np.nan
        if pd.isna(periods) or periods <= 0 or start_value <= 0:
            cagr = np.nan
        else:
            cagr = (end_value / start_value) ** (1.0 / periods) - 1.0

        records.append(
            {
                segment_col: segment,
                "Start_Year": start_year,
                "End_Year": end_year,
                "Start_Value": start_value,
                "End_Value": end_value,
                "CAGR": cagr,
            }
        )

    return pd.DataFrame(records).sort_values(segment_col).reset_index(drop=True)


def calculate_annual_yoy_growth(
    data: pd.DataFrame,
    segment_col: str,
    value_col: str,
) -> pd.DataFrame:
    """Calculate annual year-over-year growth to complement endpoint CAGR."""
    annual = (
        data.assign(Year=data["Month"].dt.year)
        .groupby([segment_col, "Year"], as_index=False)[value_col]
        .sum()
        .sort_values([segment_col, "Year"])
    )
    annual["YoY_Growth"] = annual.groupby(segment_col)[value_col].pct_change()
    return annual


def calculate_monthly_hhi(pharma: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly HHI using percentage-share squared convention.

    The resulting HHI lies between 0 and 10,000. Higher values indicate a more
    concentrated market. This function intentionally reports the conventional
    antitrust scale rather than a 0-to-1 normalized HHI.
    """
    shares = calculate_monthly_market_share(pharma)
    shares["Share_Percent"] = shares["TRx_Market_Share"] * 100.0
    hhi = (
        shares.assign(Squared_Share=shares["Share_Percent"] ** 2)
        .groupby("Month", as_index=False)["Squared_Share"]
        .sum()
        .rename(columns={"Squared_Share": "HHI"})
    )
    return hhi


def build_commercial_metrics(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build the complete commercial metric pack."""
    return {
        "monthly_market_share": calculate_monthly_market_share(pharma),
        "annual_market_share": calculate_annual_market_share(pharma),
        "brand_trx_cagr": calculate_segment_cagr(
            pharma,
            segment_col="Brand_Name",
            value_col="TRx",
        ),
        "brand_trx_yoy": calculate_annual_yoy_growth(
            pharma,
            segment_col="Brand_Name",
            value_col="TRx",
        ),
        "supplement_sales_cagr": calculate_segment_cagr(
            supplements,
            segment_col="Supplement_Category",
            value_col="Total_Sales_USD",
        ),
        "supplement_sales_yoy": calculate_annual_yoy_growth(
            supplements,
            segment_col="Supplement_Category",
            value_col="Total_Sales_USD",
        ),
        "monthly_hhi": calculate_monthly_hhi(pharma),
    }

"""Transparent commercial assumptions applied to a synthetic base forecast."""

import pandas as pd

from glp1_market.metrics import calculate_monthly_market_share


def build_scenario(forecasts, pharma, lag_months, volume=0, shift=0, price=0, response=0):
    """Apply decimal changes to volume, portfolio mix, revenue per TRx and nutrition."""
    manufacturer = pharma.drop_duplicates("Brand_Name").set_index("Brand_Name")["Manufacturer"]
    brands = forecasts.query("Metric == 'TRx'").pivot(index="Month", columns="Segment", values="Forecast").sort_index()
    gross = forecasts.query("Metric == 'Gross_Revenue_USD'").pivot(index="Month", columns="Segment", values="Forecast").reindex_like(brands)
    baseline = brands.sum(axis=1)
    shares = brands.div(baseline.where(baseline > 0), axis=0).fillna(0)
    lilly = shares.columns.map(manufacturer) == "Eli Lilly"
    lilly_share = shares.loc[:, lilly].sum(axis=1)
    shifted_share = (lilly_share + shift).clip(0, 1).where(lilly_share.between(0, 1, inclusive="neither"), lilly_share)
    adjusted = shares.copy()
    adjusted.loc[:, lilly] = shares.loc[:, lilly].mul(shifted_share.div(lilly_share.where(lilly_share > 0)).fillna(0), axis=0)
    adjusted.loc[:, ~lilly] = shares.loc[:, ~lilly].mul((1 - shifted_share).div((1 - lilly_share).where(lilly_share < 1)).fillna(0), axis=0)
    adjusted_trx = adjusted.mul(baseline * (1 + volume), axis=0)
    long = adjusted_trx.rename_axis(columns="Brand_Name").stack().rename("TRx").reset_index()
    share_table = calculate_monthly_market_share(long)
    share_table["Manufacturer"] = share_table["Brand_Name"].map(manufacturer)
    company = share_table.groupby(["Month", "Manufacturer"])["TRx_Market_Share"].sum()
    hhi = company.pow(2).groupby("Month").sum() * 10_000
    nutrition = forecasts.query("Metric == 'Total_Sales_USD'").groupby("Month")["Forecast"].sum()
    # A scenario adds only its incremental effect. The base nutrition model
    # already contains the historical synthetic relationship.
    lagged_change = pd.Series(volume, index=baseline.index).shift(lag_months, fill_value=0)
    revenue_per_trx = gross.div(brands.where(brands > 0)).fillna(0)
    result = pd.DataFrame({
        "Base_TRx": baseline, "TRx": adjusted_trx.sum(axis=1),
        "Lilly_Share": shifted_share, "Manufacturer_HHI": hhi,
        "Base_Gross_USD": gross.sum(axis=1),
        "Gross_USD": (adjusted_trx * revenue_per_trx).sum(axis=1) * (1 + price),
        "Base_Nutrition_USD": nutrition,
        "Nutrition_USD": nutrition * (1 + lagged_change * response),
        "Data_Type": "Synthetic scenario",
    }).reset_index()
    return result, share_table

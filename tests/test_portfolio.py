"""Regression checks for forecast cutoffs and scenario reconciliation."""

import numpy as np
import pandas as pd

from glp1_market.scenarios import build_scenario
from glp1_market.validation import backtest, summarize_backtest


def test_backtest_pairs_targets_and_never_trains_on_them(monkeypatch):
    dates = pd.date_range("2022-01-01", periods=27, freq="MS")
    pharma = pd.DataFrame({"Month": dates, "Brand_Name": "Brand", "TRx": range(1, 28)})
    nutrition = pd.DataFrame(columns=["Month", "Supplement_Category", "Total_Sales_USD"])

    def fake_forecast(train, periods, metric, segment):
        future = pd.date_range(train.index[-1] + pd.offsets.MonthBegin(), periods=periods, freq="MS")
        end = train.iloc[-1]
        return pd.DataFrame({
            "Month": future, "Forecast": end + np.arange(1, periods + 1),
            "Lower_80": end, "Upper_80": end + periods,
            "Lower_95": end, "Upper_95": end + periods,
        }), type("Spec", (), {"converged": True})()

    monkeypatch.setattr("glp1_market.validation.forecast_series", fake_forecast)
    rows = backtest(pharma, nutrition)
    assert (rows["Origin"] < rows["Month"]).all()
    assert rows.groupby(["Origin", "Month"])["Model"].nunique().eq(2).all()
    audit = summarize_backtest(rows)
    assert audit.query("Model == 'SARIMAX'")["MAE"].eq(0).all()
    assert audit.query("Model == 'Last value'")["MAE"].gt(0).all()


def test_scenario_conserves_share_and_applies_only_lagged_nutrition_effect():
    dates = pd.date_range("2026-01-01", periods=3, freq="MS")
    pharma = pd.DataFrame({"Brand_Name": ["A", "B"], "Manufacturer": ["Eli Lilly", "Novo Nordisk"]})
    forecasts = pd.DataFrame([
        (month, segment, metric, value)
        for month in dates
        for segment, metric, value in [
            ("A", "TRx", 30), ("B", "TRx", 70),
            ("A", "Gross_Revenue_USD", 60), ("B", "Gross_Revenue_USD", 70),
            ("Protein", "Total_Sales_USD", 100),
        ]
    ], columns=["Month", "Segment", "Metric", "Forecast"])
    base, _ = build_scenario(forecasts, pharma, lag_months=2)
    assert np.allclose(base["TRx"], base["Base_TRx"])
    assert np.allclose(base["Gross_USD"], base["Base_Gross_USD"])
    case, shares = build_scenario(forecasts, pharma, 2, volume=.1, shift=.2, price=-.1, response=.5)
    assert np.allclose(case["TRx"], 110)
    assert np.allclose(case["Lilly_Share"], .5)
    assert np.allclose(case["Manufacturer_HHI"], 5000)
    assert np.allclose(shares.groupby("Month")["TRx_Market_Share"].sum(), 1)
    assert np.allclose(case["Nutrition_USD"], [100, 100, 105])

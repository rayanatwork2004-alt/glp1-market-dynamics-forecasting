"""Expanding window validation on synthetic history."""

import numpy as np
import pandas as pd

from glp1_market.forecasting import forecast_series


def backtest(pharma, supplements, horizons=(1, 3, 6), stride=3):
    """Re-select the SARIMAX specification using only data available at each origin."""
    rows = []
    for frame, segment_key, metric in (
        (pharma, "Brand_Name", "TRx"),
        (supplements, "Supplement_Category", "Total_Sales_USD"),
    ):
        for segment, group in frame.groupby(segment_key):
            series = group.set_index("Month")[metric].sort_index().asfreq("MS")
            if series.isna().any():
                raise ValueError(f"Missing monthly observation for {segment}")
            active = np.flatnonzero(series.to_numpy() > 0)
            if not len(active):
                continue
            series = series.iloc[active[0]:]
            for end in range(len(series) - max(horizons), 17, -stride):
                train = series.iloc[:end]
                fitted, spec = forecast_series(train, max(horizons), metric, segment)
                for horizon in horizons:
                    actual = series.iloc[end + horizon - 1]
                    prediction = fitted.iloc[horizon - 1]
                    common = {
                        "Segment": segment, "Metric": metric, "Horizon": horizon,
                        "Origin": train.index[-1], "Month": prediction["Month"],
                        "Actual": actual, "Data_Type": "Synthetic",
                    }
                    rows.append({
                        **common, "Model": "SARIMAX",
                        "Prediction": prediction["Forecast"],
                        "Covered_80": prediction["Lower_80"] <= actual <= prediction["Upper_80"],
                        "Covered_95": prediction["Lower_95"] <= actual <= prediction["Upper_95"],
                        "Converged": spec.converged,
                    })
                    rows.append({
                        **common, "Model": "Last value",
                        "Prediction": train.iloc[-1],
                        "Covered_80": np.nan, "Covered_95": np.nan, "Converged": pd.NA,
                    })
    return pd.DataFrame(rows, columns=[
        "Segment", "Metric", "Horizon", "Origin", "Month", "Actual", "Data_Type",
        "Model", "Prediction", "Covered_80", "Covered_95", "Converged",
    ])


def summarize_backtest(detail):
    """Score comparable origins separately by segment, model and lead time."""
    keys = ["Metric", "Segment", "Horizon", "Model"]
    rows = []
    for key, group in detail.groupby(keys):
        error = group["Prediction"] - group["Actual"]
        actual_total = group["Actual"].abs().sum()
        rows.append({
            **dict(zip(keys, key)),
            "N": len(error), "MAE": error.abs().mean(),
            "RMSE": np.sqrt(error.pow(2).mean()),
            "WAPE": error.abs().sum() / actual_total if actual_total else np.nan,
            "Bias": error.mean(),
            "Coverage_80": group["Covered_80"].mean(),
            "Coverage_95": group["Covered_95"].mean(),
            "Nonconverged": int(group["Converged"].eq(False).sum()),
            "Data_Type": "Synthetic",
        })
    return pd.DataFrame(rows, columns=keys + [
        "N", "MAE", "RMSE", "WAPE", "Bias", "Coverage_80", "Coverage_95",
        "Nonconverged", "Data_Type",
    ])

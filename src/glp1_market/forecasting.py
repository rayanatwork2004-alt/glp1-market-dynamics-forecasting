"""Segment-level SARIMAX forecasting for GLP-1 and nutrition markets."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


@dataclass(frozen=True)
class SarimaxSpec:
    """Selected SARIMAX model specification and fit quality."""

    order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int]
    aic: float


def _trim_leading_zeros(series: pd.Series) -> pd.Series:
    """Remove structural pre-launch zeros while preserving later observations."""
    positive_positions = np.flatnonzero(series.to_numpy() > 0)
    if positive_positions.size == 0:
        return series
    return series.iloc[positive_positions[0] :]


def _candidate_specs(
    n_observations: int,
) -> Iterable[tuple[tuple[int, int, int], tuple[int, int, int, int]]]:
    """Yield a deliberately compact SARIMAX search grid.

    With only 26-48 post-launch monthly observations, exhaustive ARIMA grid
    search is computationally wasteful and statistically fragile. This set
    covers parsimonious level, differenced, and short-memory structures while
    adding annual seasonality only when at least three years of history exist.
    """
    non_seasonal = [
        (0, 1, 1),
        (1, 1, 0),
        (1, 1, 1),
        (2, 1, 0),
        (0, 1, 2),
        (1, 0, 1),
    ]

    if n_observations >= 36:
        seasonal = [
            (0, 0, 0, 0),
            (1, 0, 0, 12),
            (0, 0, 1, 12),
        ]
    else:
        seasonal = [(0, 0, 0, 0)]

    for order in non_seasonal:
        for seasonal_order in seasonal:
            yield order, seasonal_order


def select_sarimax_model(series: pd.Series) -> SarimaxSpec:
    """Select the lowest-AIC SARIMAX specification on log-transformed data."""
    clean = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    clean = _trim_leading_zeros(clean)

    if len(clean) < 12:
        raise ValueError(
            f"At least 12 post-launch observations are required; got {len(clean)}."
        )

    transformed = np.log1p(clean)
    best: Optional[SarimaxSpec] = None

    for order, seasonal_order in _candidate_specs(len(transformed)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = SARIMAX(
                    transformed,
                    order=order,
                    seasonal_order=seasonal_order,
                    trend="t",
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                fitted = model.fit(disp=False, maxiter=120)

            if np.isfinite(fitted.aic) and (
                best is None or fitted.aic < best.aic
            ):
                best = SarimaxSpec(
                    order=order,
                    seasonal_order=seasonal_order,
                    aic=float(fitted.aic),
                )
        except (ValueError, np.linalg.LinAlgError):
            continue

    if best is None:
        return SarimaxSpec(
            order=(1, 1, 0),
            seasonal_order=(0, 0, 0, 0),
            aic=np.nan,
        )
    return best


def forecast_series(
    series: pd.Series,
    forecast_periods: int,
    metric_name: str,
    segment_name: str,
) -> tuple[pd.DataFrame, SarimaxSpec]:
    """Fit a SARIMAX model and return mean forecast with 95% intervals."""
    clean = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    clean = _trim_leading_zeros(clean)
    spec = select_sarimax_model(clean)

    transformed = np.log1p(clean)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            transformed,
            order=spec.order,
            seasonal_order=spec.seasonal_order,
            trend="t",
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted = model.fit(disp=False, maxiter=150)

    prediction = fitted.get_forecast(steps=forecast_periods)
    mean_log = prediction.predicted_mean
    interval_log = prediction.conf_int(alpha=0.05)

    forecast_index = pd.date_range(
        clean.index.max() + pd.offsets.MonthBegin(1),
        periods=forecast_periods,
        freq="MS",
    )

    result = pd.DataFrame(
        {
            "Month": forecast_index,
            "Segment": segment_name,
            "Metric": metric_name,
            "Forecast": np.maximum(np.expm1(mean_log.to_numpy()), 0.0),
            "Lower_95": np.maximum(
                np.expm1(interval_log.iloc[:, 0].to_numpy()),
                0.0,
            ),
            "Upper_95": np.maximum(
                np.expm1(interval_log.iloc[:, 1].to_numpy()),
                0.0,
            ),
            "AIC": fitted.aic,
            "Order": str(spec.order),
            "Seasonal_Order": str(spec.seasonal_order),
        }
    )
    return result, SarimaxSpec(spec.order, spec.seasonal_order, fitted.aic)


def forecast_segmented_metric(
    data: pd.DataFrame,
    segment_col: str,
    value_col: str,
    forecast_periods: int,
    metric_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Forecast a metric independently for every segment."""
    forecasts = []
    diagnostics = []

    for segment_name, group in data.groupby(segment_col):
        series = (
            group.groupby("Month")[value_col]
            .sum()
            .sort_index()
            .asfreq("MS", fill_value=0.0)
        )
        segment_forecast, spec = forecast_series(
            series=series,
            forecast_periods=forecast_periods,
            metric_name=metric_name,
            segment_name=str(segment_name),
        )
        forecasts.append(segment_forecast)
        diagnostics.append(
            {
                "Segment": segment_name,
                "Metric": metric_name,
                "AIC": spec.aic,
                "Order": str(spec.order),
                "Seasonal_Order": str(spec.seasonal_order),
                "Training_Observations": int((_trim_leading_zeros(series)).shape[0]),
            }
        )

    return (
        pd.concat(forecasts, ignore_index=True),
        pd.DataFrame(diagnostics),
    )


def build_forecasts(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
    forecast_periods: int = 24,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build all required 24-month segment forecasts and diagnostics."""
    trx_forecast, trx_diag = forecast_segmented_metric(
        pharma,
        segment_col="Brand_Name",
        value_col="TRx",
        forecast_periods=forecast_periods,
        metric_name="TRx",
    )
    nutrition_revenue_forecast, nutrition_revenue_diag = (
        forecast_segmented_metric(
            supplements,
            segment_col="Supplement_Category",
            value_col="Total_Sales_USD",
            forecast_periods=forecast_periods,
            metric_name="Total_Sales_USD",
        )
    )

    # Translate TRx forecasts into an implied gross-revenue scenario using each
    # brand's trailing-12-month realized gross revenue per prescription. This
    # keeps the predictive requirement focused on TRx while still supporting
    # the executive dual-axis revenue visualization without fitting a redundant
    # second time-series model to a mechanically related synthetic measure.
    trailing = pharma[pharma["TRx"] > 0].copy()
    trailing = trailing.sort_values(["Brand_Name", "Month"])
    trailing["Revenue_Per_TRx"] = (
        trailing["Gross_Revenue_USD"] / trailing["TRx"]
    )
    revenue_per_trx = (
        trailing.groupby("Brand_Name", group_keys=False)
        .tail(12)
        .groupby("Brand_Name")["Revenue_Per_TRx"]
        .mean()
    )

    pharma_revenue_forecast = trx_forecast.copy()
    pharma_revenue_forecast["Revenue_Per_TRx"] = (
        pharma_revenue_forecast["Segment"].map(revenue_per_trx)
    )
    for column in ["Forecast", "Lower_95", "Upper_95"]:
        pharma_revenue_forecast[column] = (
            pharma_revenue_forecast[column]
            * pharma_revenue_forecast["Revenue_Per_TRx"]
        )
    pharma_revenue_forecast["Metric"] = "Gross_Revenue_USD"
    pharma_revenue_forecast = pharma_revenue_forecast.drop(
        columns=["Revenue_Per_TRx"]
    )

    forecasts = pd.concat(
        [trx_forecast, pharma_revenue_forecast, nutrition_revenue_forecast],
        ignore_index=True,
    )
    diagnostics = pd.concat(
        [trx_diag, nutrition_revenue_diag],
        ignore_index=True,
    )
    return forecasts, diagnostics

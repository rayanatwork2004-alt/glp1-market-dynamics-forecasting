"""End-to-end orchestration for the GLP-1 market analytics workflow."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from glp1_market.config import ProjectConfig
from glp1_market.data_generation import (
    calculate_cross_market_correlation,
    generate_all_data,
)
from glp1_market.forecasting import build_forecasts
from glp1_market.metrics import build_commercial_metrics
from glp1_market.visualization import (
    plot_dual_axis_market_trajectory,
    plot_market_share_evolution,
    plot_segment_forecast,
)


def _save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to CSV with reproducible formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, date_format="%Y-%m-%d")


def _data_quality_summary(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
    unified: pd.DataFrame,
) -> dict:
    """Return compact data-quality checks for pipeline observability."""
    return {
        "pharma_rows": int(len(pharma)),
        "supplement_rows": int(len(supplements)),
        "unified_rows": int(len(unified)),
        "pharma_null_cells": int(pharma.isna().sum().sum()),
        "supplement_null_cells": int(supplements.isna().sum().sum()),
        "pharma_duplicate_rows": int(pharma.duplicated().sum()),
        "supplement_duplicate_rows": int(supplements.duplicated().sum()),
        "historical_months": int(pharma["Month"].nunique()),
        "minimum_trx": int(pharma["TRx"].min()),
        "minimum_supplement_units": int(supplements["Units_Sold"].min()),
    }


def run_pipeline(config: ProjectConfig | None = None) -> dict[str, pd.DataFrame]:
    """Execute generation, metrics, forecasting, persistence, and charts."""
    config = config or ProjectConfig()
    data_dir = Path(config.data_dir)
    output_dir = Path(config.output_dir)
    figure_dir = output_dir / "figures"
    metric_dir = output_dir / "metrics"
    forecast_dir = output_dir / "forecasts"

    pharma, supplements, unified = generate_all_data(config)
    correlation = calculate_cross_market_correlation(
        pharma,
        supplements,
        lag_months=config.consumer_adoption_lag_months,
    )
    metrics = build_commercial_metrics(pharma, supplements)
    forecasts, diagnostics = build_forecasts(
        pharma,
        supplements,
        forecast_periods=config.forecast_periods,
    )

    _save_dataframe(pharma, data_dir / "pharmaceutical_market.csv")
    _save_dataframe(supplements, data_dir / "companion_nutrition_market.csv")
    _save_dataframe(unified, data_dir / "unified_cross_market_fact.csv")
    _save_dataframe(correlation, output_dir / "cross_market_correlation.csv")
    _save_dataframe(forecasts, forecast_dir / "segment_forecasts.csv")
    _save_dataframe(diagnostics, forecast_dir / "model_diagnostics.csv")

    for metric_name, metric_df in metrics.items():
        _save_dataframe(metric_df, metric_dir / f"{metric_name}.csv")

    quality_summary = _data_quality_summary(pharma, supplements, unified)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "data_quality_summary.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(quality_summary, file, indent=2)

    fig = plot_dual_axis_market_trajectory(
        pharma,
        supplements,
        forecasts,
        figure_dir / "01_dual_axis_market_trajectory.png",
    )
    plt.close(fig)

    fig = plot_market_share_evolution(
        metrics["monthly_market_share"],
        figure_dir / "02_market_share_evolution.png",
    )
    plt.close(fig)

    fig = plot_segment_forecast(
        historical=pharma,
        forecasts=forecasts,
        segment_col="Brand_Name",
        value_col="TRx",
        metric_name="TRx",
        segment_name="Zepbound",
        output_path=figure_dir / "03_zepbound_trx_forecast.png",
    )
    plt.close(fig)

    fig = plot_segment_forecast(
        historical=supplements,
        forecasts=forecasts,
        segment_col="Supplement_Category",
        value_col="Total_Sales_USD",
        metric_name="Total_Sales_USD",
        segment_name="Protein & Amino Acids for muscle retention",
        output_path=figure_dir / "04_protein_nutrition_sales_forecast.png",
    )
    plt.close(fig)

    return {
        "pharma": pharma,
        "supplements": supplements,
        "unified": unified,
        "correlation": correlation,
        "forecasts": forecasts,
        "diagnostics": diagnostics,
        **metrics,
    }

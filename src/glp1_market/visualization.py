"""Publication-quality executive visualization functions."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter, PercentFormatter


BRAND_PALETTE = {
    "Ozempic": "#4C78A8",
    "Wegovy": "#72B7B2",
    "Mounjaro": "#F58518",
    "Zepbound": "#E45756",
}


def _set_theme() -> None:
    """Apply a consistent executive visualization theme."""
    sns.set_theme(
        context="talk",
        style="whitegrid",
        font_scale=0.92,
        rc={
            "axes.titleweight": "bold",
            "axes.labelweight": "semibold",
            "grid.alpha": 0.20,
            "axes.spines.top": False,
            "axes.spines.right": False,
        },
    )


def _money_formatter(value: float, _: int) -> str:
    """Format large currency values compactly."""
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def plot_dual_axis_market_trajectory(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
    forecasts: pd.DataFrame,
    output_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot historical/projected pharma and nutrition revenue trajectories."""
    _set_theme()

    pharma_hist = pharma.groupby("Month")["Gross_Revenue_USD"].sum()
    nutrition_hist = supplements.groupby("Month")["Total_Sales_USD"].sum()

    pharma_fcst = (
        forecasts[forecasts["Metric"] == "Gross_Revenue_USD"]
        .groupby("Month")[["Forecast", "Lower_95", "Upper_95"]]
        .sum()
    )
    nutrition_fcst = (
        forecasts[forecasts["Metric"] == "Total_Sales_USD"]
        .groupby("Month")[["Forecast", "Lower_95", "Upper_95"]]
        .sum()
    )

    fig, ax1 = plt.subplots(figsize=(14, 7.5))
    ax2 = ax1.twinx()

    pharma_color = "#2F5597"
    nutrition_color = "#008C95"

    line1 = ax1.plot(
        pharma_hist.index,
        pharma_hist.values,
        color=pharma_color,
        linewidth=2.8,
        label="GLP-1 Gross Revenue — Historical",
    )[0]
    line2 = ax1.plot(
        pharma_fcst.index,
        pharma_fcst["Forecast"],
        color=pharma_color,
        linestyle="--",
        linewidth=2.8,
        label="GLP-1 Gross Revenue — Forecast",
    )[0]
    ax1.fill_between(
        pharma_fcst.index,
        pharma_fcst["Lower_95"],
        pharma_fcst["Upper_95"],
        color=pharma_color,
        alpha=0.12,
    )

    line3 = ax2.plot(
        nutrition_hist.index,
        nutrition_hist.values,
        color=nutrition_color,
        linewidth=2.6,
        label="Nutrition Sales — Historical",
    )[0]
    line4 = ax2.plot(
        nutrition_fcst.index,
        nutrition_fcst["Forecast"],
        color=nutrition_color,
        linestyle="--",
        linewidth=2.6,
        label="Nutrition Sales — Forecast",
    )[0]
    ax2.fill_between(
        nutrition_fcst.index,
        nutrition_fcst["Lower_95"],
        nutrition_fcst["Upper_95"],
        color=nutrition_color,
        alpha=0.10,
    )

    forecast_start = pharma_fcst.index.min()
    ax1.axvline(forecast_start, linestyle=":", linewidth=1.5, alpha=0.8)
    ax1.text(
        forecast_start,
        ax1.get_ylim()[1] * 0.94,
        " Forecast period",
        fontsize=10,
        va="top",
    )

    ax1.set_title(
        "GLP-1 Commercial Expansion and Companion Nutrition Ripple Effect",
        pad=16,
    )
    ax1.set_xlabel("Month")
    ax1.set_ylabel("GLP-1 Gross Revenue")
    ax2.set_ylabel("Companion Nutrition Sales")
    ax1.yaxis.set_major_formatter(FuncFormatter(_money_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(_money_formatter))

    handles = [line1, line2, line3, line4]
    labels = [handle.get_label() for handle in handles]
    ax1.legend(
        handles,
        labels,
        loc="upper left",
        frameon=True,
        fontsize=10,
    )
    fig.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")
    return fig


def plot_market_share_evolution(
    monthly_market_share: pd.DataFrame,
    output_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot stacked monthly TRx share evolution by brand."""
    _set_theme()
    pivot = monthly_market_share.pivot(
        index="Month",
        columns="Brand_Name",
        values="TRx_Market_Share",
    ).fillna(0.0)

    ordered_brands = [
        brand for brand in BRAND_PALETTE if brand in pivot.columns
    ]
    pivot = pivot[ordered_brands]

    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.stackplot(
        pivot.index,
        *[pivot[col].values for col in pivot.columns],
        labels=pivot.columns,
        colors=[BRAND_PALETTE[col] for col in pivot.columns],
        alpha=0.92,
    )
    ax.set_title("GLP-1 Brand TRx Market Share Evolution", pad=16)
    ax.set_xlabel("Month")
    ax.set_ylabel("TRx Market Share")
    ax.set_ylim(0.0, 1.0)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=4,
        frameon=False,
    )
    fig.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")
    return fig


def plot_segment_forecast(
    historical: pd.DataFrame,
    forecasts: pd.DataFrame,
    segment_col: str,
    value_col: str,
    metric_name: str,
    segment_name: str,
    output_path: Optional[Path] = None,
) -> plt.Figure:
    """Plot one segment's history, forecast, and 95% confidence interval."""
    _set_theme()

    hist = (
        historical[historical[segment_col] == segment_name]
        .groupby("Month")[value_col]
        .sum()
        .sort_index()
    )
    positive_positions = hist.to_numpy().nonzero()[0]
    if positive_positions.size > 0:
        start_position = max(int(positive_positions[0]) - 1, 0)
        hist = hist.iloc[start_position:]
    fcst = forecasts[
        (forecasts["Metric"] == metric_name)
        & (forecasts["Segment"] == segment_name)
    ].sort_values("Month")

    if fcst.empty:
        raise ValueError(
            f"No forecast found for segment={segment_name!r}, metric={metric_name!r}."
        )

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(hist.index, hist.values, linewidth=2.6, label="Historical")
    ax.plot(
        fcst["Month"],
        fcst["Forecast"],
        linestyle="--",
        linewidth=2.6,
        label="24-Month Forecast",
    )
    ax.fill_between(
        fcst["Month"],
        fcst["Lower_95"],
        fcst["Upper_95"],
        alpha=0.18,
        label="95% Confidence Interval",
    )
    ax.axvline(fcst["Month"].min(), linestyle=":", linewidth=1.5)
    ax.set_title(f"Predictive Forecast — {segment_name}", pad=16)
    ax.set_xlabel("Month")
    ax.set_ylabel(metric_name.replace("_", " "))

    if "USD" in metric_name:
        ax.yaxis.set_major_formatter(FuncFormatter(_money_formatter))
    else:
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}M")
        )

    ax.legend(frameon=True)
    fig.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")
    return fig

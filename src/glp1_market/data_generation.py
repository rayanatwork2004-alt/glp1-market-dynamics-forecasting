"""Synthetic cross-market data generation engine."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd

from glp1_market.config import ProjectConfig


SUPPLEMENT_LABELS = {
    "Protein & Amino Acids": "Protein & Amino Acids for muscle retention",
    "Viscous Fibers": "Viscous Fibers for GI tracking",
    "Targeted Micronutrients": (
        "Targeted Micronutrients for vitamin deficits"
    ),
}


def _logistic_capacity_modifier(
    month_number: int,
    midpoint: float,
    steepness: float = 0.10,
) -> float:
    """Return a smooth saturation modifier to prevent runaway growth."""
    return 1.0 / (1.0 + np.exp(steepness * (month_number - midpoint)))


def generate_pharma_data(config: ProjectConfig) -> pd.DataFrame:
    """Generate monthly synthetic pharmaceutical prescription data.

    The generator combines brand-specific exponential growth, a gradual
    saturation modifier, realistic NRx/TRx ratios, price inflation, and
    Gaussian market noise. Pre-launch rows are retained with zero volumes so
    downstream class-level calculations operate on a balanced monthly panel.
    """
    rng = np.random.default_rng(config.random_seed)
    records = []

    for brand_name, assumptions in config.brands.items():
        launch_month = pd.Timestamp(assumptions.launch_month)
        launch_index = 0

        for month in config.historical_months:
            if month < launch_month:
                trx = 0
                nrx = 0
                awp = assumptions.average_wholesale_price_usd
                gross_revenue = 0.0
            else:
                months_since_launch = (
                    (month.year - launch_month.year) * 12
                    + month.month
                    - launch_month.month
                )
                launch_index += 1

                raw_growth = (
                    assumptions.initial_trx
                    * (1.0 + assumptions.monthly_growth) ** months_since_launch
                )
                capacity_modifier = 0.72 + 0.55 * _logistic_capacity_modifier(
                    month_number=months_since_launch,
                    midpoint=42.0,
                )
                seasonal_modifier = 1.0 + 0.035 * np.sin(
                    2.0 * np.pi * month.month / 12.0
                )
                noise = rng.normal(0.0, config.pharma_monthly_noise_sd)
                trx = int(
                    max(
                        0.0,
                        raw_growth
                        * capacity_modifier
                        * seasonal_modifier
                        * (1.0 + noise),
                    )
                )

                nrx_ratio = rng.uniform(*assumptions.nrx_ratio_range)
                nrx = int(round(trx * nrx_ratio))

                years_since_start = (
                    month.year - config.historical_months[0].year
                ) + (month.month - 1) / 12.0
                awp = assumptions.average_wholesale_price_usd * (
                    1.0 + assumptions.price_growth_annual
                ) ** years_since_start

                revenue_noise = max(0.90, 1.0 + rng.normal(0.0, 0.018))
                gross_revenue = (
                    trx
                    * awp
                    * assumptions.gross_to_awp_factor
                    * revenue_noise
                )

            records.append(
                {
                    "Month": month,
                    "Brand_Name": brand_name,
                    "Manufacturer": assumptions.manufacturer,
                    "Molecule": assumptions.molecule,
                    "TRx": trx,
                    "NRx": nrx,
                    "Average_Wholesale_Price_USD": round(awp, 2),
                    "Gross_Revenue_USD": round(gross_revenue, 2),
                }
            )

    pharma = pd.DataFrame.from_records(records)
    pharma = pharma.sort_values(["Month", "Brand_Name"]).reset_index(drop=True)
    return pharma


def generate_supplement_data(
    pharma: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    """Generate companion nutrition demand linked to lagged GLP-1 TRx.

    Demand is driven by two-month lagged class TRx and cumulative class
    exposure. The explicit lag creates a measurable lead-lag relationship
    suitable for cross-market analytics while category-specific sensitivities
    prevent the three series from becoming deterministic clones.
    """
    rng = np.random.default_rng(config.random_seed + 100)

    class_trx = (
        pharma.groupby("Month", as_index=False)["TRx"]
        .sum()
        .rename(columns={"TRx": "Class_TRx"})
        .sort_values("Month")
    )
    class_trx["Lagged_TRx"] = class_trx["Class_TRx"].shift(
        config.consumer_adoption_lag_months
    )
    class_trx["Lagged_TRx"] = class_trx["Lagged_TRx"].bfill()
    class_trx["Cumulative_TRx"] = class_trx["Class_TRx"].cumsum()

    lag_min = class_trx["Lagged_TRx"].min()
    lag_range = class_trx["Lagged_TRx"].max() - lag_min
    cumulative_max = class_trx["Cumulative_TRx"].max()
    class_trx["Lagged_TRx_Index"] = (
        (class_trx["Lagged_TRx"] - lag_min) / max(lag_range, 1.0)
    )
    class_trx["Cumulative_Exposure_Index"] = (
        class_trx["Cumulative_TRx"] / max(cumulative_max, 1.0)
    )

    records = []
    base_month = config.historical_months[0]

    for category, assumptions in config.supplements.items():
        for row in class_trx.itertuples(index=False):
            months_from_start = (
                (row.Month.year - base_month.year) * 12
                + row.Month.month
                - base_month.month
            )

            demand_signal = (
                0.58 * row.Lagged_TRx_Index
                + 0.42 * row.Cumulative_Exposure_Index
            )
            linked_units = (
                row.Lagged_TRx
                * assumptions.trx_capture_rate
                * assumptions.sensitivity_to_trx
            )
            organic_growth = assumptions.baseline_units * (
                1.0 + 0.0065
            ) ** months_from_start
            seasonal_modifier = 1.0 + 0.025 * np.cos(
                2.0 * np.pi * row.Month.month / 12.0
            )
            noise = rng.normal(0.0, config.supplement_monthly_noise_sd)

            units = int(
                max(
                    0.0,
                    (
                        organic_growth * (0.80 + 0.45 * demand_signal)
                        + linked_units
                    )
                    * seasonal_modifier
                    * (1.0 + noise),
                )
            )

            years_since_start = months_from_start / 12.0
            retail_price = assumptions.average_retail_price_usd * (
                1.0 + assumptions.price_growth_annual
            ) ** years_since_start
            price_noise = max(0.96, 1.0 + rng.normal(0.0, 0.008))
            retail_price *= price_noise
            total_sales = units * retail_price

            records.append(
                {
                    "Month": row.Month,
                    "Supplement_Category": SUPPLEMENT_LABELS[category],
                    "Units_Sold": units,
                    "Average_Retail_Price_USD": round(retail_price, 2),
                    "Total_Sales_USD": round(total_sales, 2),
                }
            )

    supplements = pd.DataFrame.from_records(records)
    supplements = supplements.sort_values(
        ["Month", "Supplement_Category"]
    ).reset_index(drop=True)
    return supplements


def build_unified_analytical_layout(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
) -> pd.DataFrame:
    """Return a normalized cross-market fact table for integrated analytics."""
    pharma_fact = pharma.rename(
        columns={
            "Brand_Name": "Segment",
            "TRx": "Volume",
            "Gross_Revenue_USD": "Revenue_USD",
        }
    ).copy()
    pharma_fact["Market"] = "Pharmaceutical Prescriptions"
    pharma_fact["Segment_Type"] = "Brand"
    pharma_fact["Price_USD"] = pharma_fact["Average_Wholesale_Price_USD"]
    pharma_fact["New_Volume"] = pharma_fact["NRx"]

    pharma_fact = pharma_fact[
        [
            "Month",
            "Market",
            "Segment_Type",
            "Segment",
            "Manufacturer",
            "Molecule",
            "Volume",
            "New_Volume",
            "Price_USD",
            "Revenue_USD",
        ]
    ]

    supplement_fact = supplements.rename(
        columns={
            "Supplement_Category": "Segment",
            "Units_Sold": "Volume",
            "Average_Retail_Price_USD": "Price_USD",
            "Total_Sales_USD": "Revenue_USD",
        }
    ).copy()
    supplement_fact["Market"] = "Companion Medical Nutrition"
    supplement_fact["Segment_Type"] = "Supplement Category"
    supplement_fact["Manufacturer"] = pd.NA
    supplement_fact["Molecule"] = pd.NA
    supplement_fact["New_Volume"] = pd.NA

    supplement_fact = supplement_fact[
        [
            "Month",
            "Market",
            "Segment_Type",
            "Segment",
            "Manufacturer",
            "Molecule",
            "Volume",
            "New_Volume",
            "Price_USD",
            "Revenue_USD",
        ]
    ]

    unified = pd.concat([pharma_fact, supplement_fact], ignore_index=True)
    unified = unified.sort_values(["Month", "Market", "Segment"]).reset_index(
        drop=True
    )
    return unified


def calculate_cross_market_correlation(
    pharma: pd.DataFrame,
    supplements: pd.DataFrame,
    lag_months: int = 2,
) -> pd.DataFrame:
    """Quantify lead-lag correlation in levels and first differences.

    Level correlations demonstrate the engineered cross-market co-movement,
    while first-difference correlations provide a stricter check that the
    relationship is not solely an artifact of two upward-trending series.
    """
    class_trx = pharma.groupby("Month")["TRx"].sum().sort_index()
    nutrition_sales = (
        supplements.groupby("Month")["Total_Sales_USD"].sum().sort_index()
    )

    rows = []
    maximum_lag = max(lag_months + 3, 6)
    for correlation_type in ["Levels", "First_Difference"]:
        for lag in range(0, maximum_lag):
            trx_signal = class_trx.shift(lag)
            nutrition_signal = nutrition_sales.copy()

            if correlation_type == "First_Difference":
                trx_signal = trx_signal.diff()
                nutrition_signal = nutrition_signal.diff()

            aligned = pd.concat(
                [trx_signal, nutrition_signal],
                axis=1,
                join="inner",
            ).dropna()
            aligned.columns = ["GLP1_TRx", "Nutrition_Sales"]
            rows.append(
                {
                    "Correlation_Type": correlation_type,
                    "TRx_Lead_Months": lag,
                    "Pearson_Correlation": aligned["GLP1_TRx"].corr(
                        aligned["Nutrition_Sales"]
                    ),
                }
            )

    return pd.DataFrame(rows)


def generate_all_data(
    config: ProjectConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate all synthetic datasets in one reproducible call."""
    pharma = generate_pharma_data(config)
    supplements = generate_supplement_data(pharma, config)
    unified = build_unified_analytical_layout(pharma, supplements)
    return pharma, supplements, unified

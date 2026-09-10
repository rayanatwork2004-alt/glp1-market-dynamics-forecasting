"""Central configuration for the GLP-1 cross-market analytics project."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


@dataclass(frozen=True)
class BrandConfig:
    """Commercial assumptions for one pharmaceutical brand."""

    manufacturer: str
    molecule: str
    launch_month: str
    initial_trx: float
    monthly_growth: float
    nrx_ratio_range: Tuple[float, float]
    average_wholesale_price_usd: float
    price_growth_annual: float
    gross_to_awp_factor: float


@dataclass(frozen=True)
class SupplementConfig:
    """Demand and pricing assumptions for a supplement category."""

    baseline_units: float
    trx_capture_rate: float
    average_retail_price_usd: float
    price_growth_annual: float
    sensitivity_to_trx: float


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level reproducible project configuration."""

    start_month: str = "2022-01-01"
    end_month: str = "2025-12-01"
    forecast_start: str = "2026-01-01"
    forecast_periods: int = 24
    random_seed: int = 42
    consumer_adoption_lag_months: int = 2
    pharma_monthly_noise_sd: float = 0.055
    supplement_monthly_noise_sd: float = 0.020
    output_dir: Path = Path("outputs")
    data_dir: Path = Path("data")
    figure_dpi: int = 180
    brands: Dict[str, BrandConfig] = field(
        default_factory=lambda: {
            "Ozempic": BrandConfig(
                manufacturer="Novo Nordisk",
                molecule="Semaglutide",
                launch_month="2022-01-01",
                initial_trx=520_000,
                monthly_growth=0.023,
                nrx_ratio_range=(0.25, 0.31),
                average_wholesale_price_usd=935.77,
                price_growth_annual=0.025,
                gross_to_awp_factor=0.69,
            ),
            "Wegovy": BrandConfig(
                manufacturer="Novo Nordisk",
                molecule="Semaglutide",
                launch_month="2022-01-01",
                initial_trx=165_000,
                monthly_growth=0.043,
                nrx_ratio_range=(0.28, 0.35),
                average_wholesale_price_usd=1_349.02,
                price_growth_annual=0.020,
                gross_to_awp_factor=0.66,
            ),
            "Mounjaro": BrandConfig(
                manufacturer="Eli Lilly",
                molecule="Tirzepatide",
                launch_month="2022-05-01",
                initial_trx=48_000,
                monthly_growth=0.070,
                nrx_ratio_range=(0.27, 0.34),
                average_wholesale_price_usd=1_069.08,
                price_growth_annual=0.022,
                gross_to_awp_factor=0.68,
            ),
            "Zepbound": BrandConfig(
                manufacturer="Eli Lilly",
                molecule="Tirzepatide",
                launch_month="2023-11-01",
                initial_trx=36_000,
                monthly_growth=0.105,
                nrx_ratio_range=(0.29, 0.35),
                average_wholesale_price_usd=1_059.87,
                price_growth_annual=0.018,
                gross_to_awp_factor=0.67,
            ),
        }
    )
    supplements: Dict[str, SupplementConfig] = field(
        default_factory=lambda: {
            "Protein & Amino Acids": SupplementConfig(
                baseline_units=115_000,
                trx_capture_rate=0.082,
                average_retail_price_usd=42.00,
                price_growth_annual=0.025,
                sensitivity_to_trx=1.18,
            ),
            "Viscous Fibers": SupplementConfig(
                baseline_units=72_000,
                trx_capture_rate=0.050,
                average_retail_price_usd=28.00,
                price_growth_annual=0.020,
                sensitivity_to_trx=0.92,
            ),
            "Targeted Micronutrients": SupplementConfig(
                baseline_units=91_000,
                trx_capture_rate=0.064,
                average_retail_price_usd=34.00,
                price_growth_annual=0.023,
                sensitivity_to_trx=1.05,
            ),
        }
    )

    @property
    def historical_months(self) -> pd.DatetimeIndex:
        """Return the complete monthly historical date range."""
        return pd.date_range(self.start_month, self.end_month, freq="MS")

    @property
    def forecast_months(self) -> pd.DatetimeIndex:
        """Return the complete monthly forecast date range."""
        return pd.date_range(
            self.forecast_start,
            periods=self.forecast_periods,
            freq="MS",
        )

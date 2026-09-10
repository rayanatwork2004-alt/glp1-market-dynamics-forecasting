"""Core tests for synthetic data, metrics, and forecasting inputs."""

import numpy as np
import pandas as pd

from glp1_market.config import ProjectConfig
from glp1_market.data_generation import (
    calculate_cross_market_correlation,
    generate_all_data,
)
from glp1_market.metrics import (
    calculate_monthly_hhi,
    calculate_monthly_market_share,
)


def test_generated_row_counts_and_months() -> None:
    config = ProjectConfig()
    pharma, supplements, unified = generate_all_data(config)

    assert pharma["Month"].nunique() == 48
    assert len(pharma) == 48 * 4
    assert len(supplements) == 48 * 3
    assert len(unified) == len(pharma) + len(supplements)


def test_nrx_ratio_is_in_configured_business_range() -> None:
    config = ProjectConfig()
    pharma, _, _ = generate_all_data(config)
    active = pharma[pharma["TRx"] > 0].copy()
    active["NRx_TRx_Ratio"] = active["NRx"] / active["TRx"]

    assert active["NRx_TRx_Ratio"].between(0.249, 0.351).all()


def test_monthly_market_shares_sum_to_one() -> None:
    config = ProjectConfig()
    pharma, _, _ = generate_all_data(config)
    shares = calculate_monthly_market_share(pharma)
    totals = shares.groupby("Month")["TRx_Market_Share"].sum()

    assert np.allclose(totals.values, 1.0)


def test_hhi_is_on_conventional_scale() -> None:
    config = ProjectConfig()
    pharma, _, _ = generate_all_data(config)
    hhi = calculate_monthly_hhi(pharma)

    assert hhi["HHI"].between(2_500.0, 10_000.0).all()


def test_cross_market_correlation_is_positive_and_strong() -> None:
    config = ProjectConfig()
    pharma, supplements, _ = generate_all_data(config)
    correlation = calculate_cross_market_correlation(pharma, supplements)

    levels = correlation.query("Correlation_Type == 'Levels'")
    differences = correlation.query("Correlation_Type == 'First_Difference'")

    assert levels["Pearson_Correlation"].max() > 0.90
    assert differences["Pearson_Correlation"].max() > 0.60
    best_level_lag = levels.loc[
        levels["Pearson_Correlation"].idxmax(), "TRx_Lead_Months"
    ]
    assert int(best_level_lag) == 2
    assert int(
        differences.loc[
            differences["Pearson_Correlation"].idxmax(),
            "TRx_Lead_Months",
        ]
    ) == 2
    assert correlation["Pearson_Correlation"].notna().all()


def test_later_brand_launches_have_structural_prelaunch_zeros() -> None:
    config = ProjectConfig()
    pharma, _, _ = generate_all_data(config)

    mounjaro_prelaunch = pharma[
        (pharma["Brand_Name"] == "Mounjaro")
        & (pharma["Month"] < pd.Timestamp("2022-05-01"))
    ]
    zepbound_prelaunch = pharma[
        (pharma["Brand_Name"] == "Zepbound")
        & (pharma["Month"] < pd.Timestamp("2023-11-01"))
    ]

    assert (mounjaro_prelaunch["TRx"] == 0).all()
    assert (zepbound_prelaunch["TRx"] == 0).all()

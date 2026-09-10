"""Command-line entry point for the complete analytics pipeline."""

from glp1_market import ProjectConfig, run_pipeline


if __name__ == "__main__":
    config = ProjectConfig()
    results = run_pipeline(config)

    level_correlations = results["correlation"].query(
        "Correlation_Type == 'Levels'"
    )
    difference_correlations = results["correlation"].query(
        "Correlation_Type == 'First_Difference'"
    )
    best_level = level_correlations.loc[
        level_correlations["Pearson_Correlation"].idxmax()
    ]
    best_difference = difference_correlations.loc[
        difference_correlations["Pearson_Correlation"].idxmax()
    ]

    print("Pipeline completed successfully.")
    print(f"Pharmaceutical rows: {len(results['pharma']):,}")
    print(f"Nutrition rows: {len(results['supplements']):,}")
    print(f"Forecast rows: {len(results['forecasts']):,}")
    print(
        "Peak level correlation: "
        f"r={best_level['Pearson_Correlation']:.3f} at "
        f"{int(best_level['TRx_Lead_Months'])}-month TRx lead."
    )
    print(
        "Peak first-difference correlation: "
        f"r={best_difference['Pearson_Correlation']:.3f} at "
        f"{int(best_difference['TRx_Lead_Months'])}-month TRx lead."
    )

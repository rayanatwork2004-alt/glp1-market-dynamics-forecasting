# GLP-1 Market Dynamics, Prescription Forecasting, and Companion Nutrition Cross-Market Analytics

A portfolio-grade healthcare commercial analytics project that simulates a longitudinal GLP-1 prescription market, links therapy adoption to a synthetic companion medical-nutrition market, calculates life-sciences commercial KPIs, and produces 24-month segment-level forecasts with uncertainty intervals.

> **Important:** All prescription, pricing, revenue, supplement-demand, and forecast values in this repository are synthetic. Brand and manufacturer names are used to make the analytical scenario recognizable; the generated values must not be represented as IQVIA, FDA, manufacturer, payer, claims, or audited commercial data.

## Why this project is commercially relevant

The project demonstrates capabilities commonly expected in healthcare intelligence and life-sciences analytics: longitudinal market construction, launch-aware brand dynamics, NRx/TRx logic, market share, CAGR, HHI concentration analysis, cross-market lead/lag measurement, time-series model selection, forecast confidence intervals, and executive visualization.

The generator uses real-world launch timing for two later entrants to keep the synthetic panel commercially plausible: Mounjaro begins in May 2022 and Zepbound in November 2023. The numerical demand, price, revenue, and market-response assumptions remain synthetic.

## Architecture

```text
glp1_market_project/
├── README.md
├── pyproject.toml
├── requirements.txt
├── run_pipeline.py
├── Makefile
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
├── notebooks/
│   └── GLP1_cross_market_analysis.ipynb
├── src/
│   └── glp1_market/
│       ├── __init__.py
│       ├── config.py
│       ├── data_generation.py
│       ├── metrics.py
│       ├── forecasting.py
│       ├── visualization.py
│       └── pipeline.py
└── tests/
    └── test_pipeline.py
```

Running the pipeline creates:

```text
data/
├── pharmaceutical_market.csv
├── companion_nutrition_market.csv
└── unified_cross_market_fact.csv

outputs/
├── cross_market_correlation.csv
├── data_quality_summary.json
├── metrics/
├── forecasts/
└── figures/
```

## Module 1 — Synthetic cross-market generation

The pharmaceutical engine produces a balanced monthly panel from January 2022 through December 2025 for Ozempic, Wegovy, Mounjaro, and Zepbound. Brand-specific assumptions drive growth, NRx/TRx ratios, wholesale-price inflation, commercialization factors, seasonality, and Gaussian noise. Structural pre-launch months are represented as zero TRx/NRx rather than missing observations.

The companion-nutrition engine generates Protein & Amino Acids, Viscous Fibers, and Targeted Micronutrients demand. Units are linked to two-month lagged total GLP-1 TRx plus cumulative treatment exposure, creating a deliberately strong but noisy cross-market relationship.

A normalized fact table unifies both markets with standardized fields: `Month`, `Market`, `Segment_Type`, `Segment`, `Manufacturer`, `Molecule`, `Volume`, `New_Volume`, `Price_USD`, and `Revenue_USD`.

## Module 2 — Commercial metrics

The metric layer calculates:

- Monthly and annual TRx market share by brand.
- Endpoint CAGR using first and last positive annual observations.
- Annual YoY growth as a companion metric to CAGR.
- Monthly Herfindahl-Hirschman Index on the conventional 0–10,000 scale.
- Cross-market Pearson correlation across multiple TRx lead periods in both levels and first differences.

## Module 3 — Forecasting

Each brand/category is modeled independently using SARIMAX. The pipeline:

1. Removes structural pre-launch zeros.
2. Applies `log1p` transformation to preserve non-negative forecasts.
3. Searches a compact set of non-seasonal and, when sample size permits, 12-month seasonal specifications.
4. Selects the minimum-AIC model.
5. Produces January 2026–December 2027 forecasts with 95% intervals.
6. Persists model order, seasonal order, AIC, and training-window length for auditability.

Forecasted metrics include pharmaceutical TRx, pharmaceutical gross revenue, and companion-nutrition revenue.

## Module 4 — Executive visualizations

The pipeline produces:

- Dual-axis historical + projected GLP-1 gross revenue and companion-nutrition sales.
- Stacked-area GLP-1 TRx market-share evolution.
- Zepbound TRx historical/forecast chart with 95% interval.
- Protein & Amino Acids companion-nutrition revenue historical/forecast chart with 95% interval.

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows PowerShell

pip install --upgrade pip
pip install -e .[dev]
```

## Execute the full pipeline

```bash
python run_pipeline.py
```

## Run tests

```bash
pytest
```

## Suggested GitHub story

A strong repository should explain not only *what* the code produces but *why* each analytic layer matters commercially. In the final README or portfolio case study, frame the narrative around four executive questions:

1. How rapidly is the GLP-1 class expanding, and which brands are gaining share?
2. Is competitive concentration increasing or decreasing as new entrants scale?
3. Does GLP-1 adoption create a measurable lagged commercial signal in adjacent nutrition categories?
4. What does the next 24 months look like by brand/category, and how uncertain are those projections?

## Methodological limitations

This is a synthetic market simulation, not a causal clinical study. The two-month lead/lag structure is intentionally engineered and therefore cannot establish real-world causality. SARIMAX forecasts are based on a relatively short synthetic history and should be presented as a modeling demonstration, not investment guidance or a commercial forecast of actual manufacturer performance. Likewise, AWP-like values and gross-revenue calculations are synthetic assumptions and should not be interpreted as net realized price, net sales, payer reimbursement, or audited revenue.

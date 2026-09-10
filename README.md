# GLP-1 Market Dynamics, Prescription Forecasting, and Companion Nutrition Analytics

## Overview

This project explores how the GLP-1 market changed from January 2022 through December 2025 and how continued prescription growth could influence a related companion nutrition market.

I built the project as an end to end healthcare analytics case study using Python. It combines synthetic data generation, pharmaceutical market share analysis, competitive concentration metrics, time series forecasting, and data visualization.

The main goal was to create a project that goes beyond simply building a model. I wanted to show how healthcare data can be turned into commercial insights that help explain market growth, competition, and possible future demand.

> **Data note:** All prescription, pricing, revenue, supplement demand, and forecast values in this project are synthetic. Brand and manufacturer names are used only to make the analysis realistic and easier to understand. The generated values should not be interpreted as actual IQVIA, manufacturer, claims, payer, or audited commercial data.

## Key Questions

This project focuses on four main questions:

1. How is GLP-1 prescription volume changing over time?
2. Which brands are gaining or losing market share?
3. How does competition change as newer products enter the market?
4. Could increasing GLP-1 adoption create additional demand in companion nutrition categories?

## Market Trajectory

The first view compares the historical and projected pharmaceutical market with the companion nutrition market.

![GLP-1 and Companion Nutrition Market Trajectory](outputs/figures/01_dual_axis_market_trajectory.png)

The purpose of this chart is to show how growth in one healthcare market could create a related commercial opportunity in another market. In the synthetic data, companion nutrition demand follows GLP-1 adoption with a two month lag.

## Market Share Evolution

![GLP-1 Market Share Evolution](outputs/figures/02_market_share_evolution.png)

The market share view shows how prescription volume changes across Ozempic, Wegovy, Mounjaro, and Zepbound during the historical period.

Instead of assuming every product existed for the full time period, the synthetic data accounts for later market entry for Mounjaro and Zepbound. This makes the competitive dynamics more realistic and creates a clearer shift in market concentration over time.

## Forecast Example

![Zepbound TRx Forecast](outputs/figures/03_zepbound_trx_forecast.png)

The forecasting pipeline projects prescription volume through December 2027 and includes 95% confidence intervals to show forecast uncertainty.

I used SARIMAX because it provides a transparent way to model time series trends while also producing interpretable uncertainty ranges.

## Data Generated

The project creates 48 months of synthetic data covering two connected markets.

### Pharmaceutical Market

The pharmaceutical dataset includes:

* Month
* Brand Name
* Manufacturer
* Molecule
* TRx
* NRx
* Average Wholesale Price USD
* Gross Revenue USD

Brands included:

* Ozempic
* Wegovy
* Mounjaro
* Zepbound

The pharmaceutical data includes growth trends, monthly variation, product launch timing, pricing changes, and realistic NRx to TRx relationships.

### Companion Nutrition Market

The companion nutrition dataset includes:

* Month
* Supplement Category
* Units Sold
* Average Retail Price USD
* Total Sales USD

Categories included:

* Protein and Amino Acids
* Viscous Fibers
* Targeted Micronutrients

The synthetic demand model links nutrition sales to previous GLP-1 prescription activity. A two month lag is used to represent the idea that consumer demand may respond after treatment adoption rather than immediately.

## Commercial Metrics

I calculated several metrics commonly used in pharmaceutical and healthcare market analysis.

### Market Share

Monthly and annual market share are calculated using each brand's share of total GLP-1 TRx volume.

### CAGR

Compound Annual Growth Rate is calculated for both individual drug brands and companion nutrition categories.

### HHI

The Herfindahl Hirschman Index is calculated each month to measure market concentration.

A higher HHI indicates that prescription volume is concentrated among fewer brands, while a lower HHI suggests a more competitive market.

## Forecasting Approach

Each pharmaceutical brand and nutrition category is forecast independently.

The forecasting workflow:

1. Prepares each monthly time series.
2. Removes structural periods before product launch where appropriate.
3. Applies a log transformation to reduce the chance of unrealistic negative forecasts.
4. Tests multiple SARIMAX specifications.
5. Selects the model using Akaike Information Criterion.
6. Generates forecasts from January 2026 through December 2027.
7. Produces 95% confidence intervals for each forecast.

This approach keeps the forecasting process understandable and reproducible rather than treating the model as a black box.

## Project Structure

```text
glp1_market_project/
|
|-- README.md
|-- requirements.txt
|-- pyproject.toml
|-- run_pipeline.py
|-- Makefile
|
|-- docs/
|   |-- data_dictionary.md
|   |-- methodology.md
|
|-- notebooks/
|   |-- GLP1_cross_market_analysis.ipynb
|
|-- src/
|   |-- glp1_market/
|       |-- __init__.py
|       |-- config.py
|       |-- data_generation.py
|       |-- metrics.py
|       |-- forecasting.py
|       |-- visualization.py
|       |-- pipeline.py
|
|-- tests/
|   |-- test_pipeline.py
|
|-- outputs/
    |-- figures/
```

## Tools Used

* Python
* Pandas
* NumPy
* Statsmodels
* Matplotlib
* Seaborn
* Jupyter Notebook
* Pytest
* Git and GitHub

## Running the Project

Clone the repository and move into the project folder:

```bash
git clone YOUR_REPOSITORY_URL
cd glp1-market-dynamics-forecasting
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install --upgrade pip
pip install -e .[dev]
```

Run the complete pipeline:

```bash
python run_pipeline.py
```

Run the tests:

```bash
pytest
```

## What I Learned

This project helped me practice combining technical analysis with healthcare business questions. One of the biggest lessons was that a forecast alone is not enough. The analysis becomes more useful when prescription growth, market share, competition, adjacent market demand, and forecast uncertainty are viewed together.

I also learned the importance of separating synthetic assumptions from real world evidence. The relationship between GLP-1 prescriptions and companion nutrition demand in this project is intentionally simulated. It demonstrates how I would analyze a possible cross market relationship, but it does not prove that the same relationship exists in real commercial data.

## Future Improvements

I plan to continue developing the project by adding:

* Rolling forecast validation using MAE, RMSE, WAPE, and forecast bias
* Base, upside, and downside commercial scenarios
* An interactive dashboard for exploring brands and forecasts
* Additional SQL based data transformation and validation
* More detailed model diagnostics and forecast comparison

## Disclaimer

This project is for educational and portfolio purposes only. All market volumes, prices, revenues, demand relationships, and forecasts are synthetically generated and should not be used for clinical, investment, pricing, or commercial decision making.

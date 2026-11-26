# GLP-1 Market Lab

**A healthcare analytics portfolio project on brand competition, forecast reliability, and companion nutrition.**

This is my first healthcare analytics project. I brought together what I learned in school and what I was learning on my own about the pharmaceutical industry. An obesity market brief shared by someone working in pharma helped me decide which questions to explore, especially around competition, insurance coverage, and companion nutrition.

I started with one question. If access or competition changes, which part of the prescription forecast should I revisit first?

This project simulates monthly prescriptions for Ozempic, Wegovy, Mounjaro, and Zepbound, alongside three companion nutrition categories. It uses 48 months of synthetic history from January 2022 to December 2025 and projects 24 months through December 2027. The forecasts, historical inputs, and scenario results are synthetic. The dashboard also includes [public U.S. benchmarks](https://rayanatwork2004-alt.github.io/glp1-market-dynamics-forecasting/#evidence) for reported Wegovy volume, Foundayo affordability, and clinical trial results. Each benchmark links to its source. The four brands define the modeled panel. The data do not distinguish individual indications or count unique patients.

## Explore the dashboard

**[Open the live dashboard](https://rayanatwork2004-alt.github.io/glp1-market-dynamics-forecasting/)**

Start with **Medicare Part D** to see published fills, spending, share of the four brands, and the real-data forecast check. For the simulation, open **Forecast audit → Zepbound → 3 months ahead**. Compare the two models, then switch to **6 months ahead** to see how the result changes.

| View | Question it answers |
| --- | --- |
| Medicare Part D | How have real fills and spending changed for four selected brands, and how well do simple forecasts track them? |
| Canada context | What does the new Canadian semaglutide advisory tell us, and what evidence would we need to study its effects? |
| U.S. market benchmarks | What do real prescription volume estimates, published patient costs, and trial results tell us about competition and access? |
| Simulated market overview | Which brands gained share within this panel, and which manufacturers own them? |
| Forecast audit | Does SARIMAX beat the last observed value at the lead time I care about? How often do the intervals cover the simulated outcomes? |
| Scenario explorer | How much of the difference from the base comes from more prescriptions, a shift between manufacturers, or a change in revenue per prescription? |

![Synthetic brand share over time](docs/assets/synthetic-brand-share.png)

In the simulation, Wegovy prescriptions rose from **972,443 in October 2025** to **992,972 in November**, while its share of the four brands fell from **28.4% to 26.1%**. The panel grew faster than Wegovy did. If I only looked at share, I’d miss that Wegovy’s prescription volume actually went up.

## How I built it

- **Real claims.** I use the CMS all-manufacturer rows by brand. The annual release provides the comparable time series. The preliminary release offers a more recent view in its original reporting windows. I only calculate share where all four brands report fills. The annual check compares last value with a simple trend, one year ahead, for brands with enough history. [Medicare methods and sources](docs/medicare.md)

- **Market data.** A seeded simulation generates monthly total prescriptions (TRx), new prescriptions (NRx), synthetic prices and sales. Structural zeroes before modeled launch are preserved for share calculations and removed from forecast training.
- **Forecast validation.** I keep the original log SARIMAX approach and reselect model orders within each training window. Every three months, I compare the model with a last value baseline at 1, 3 and 6 months ahead. I report MAE, RMSE, WAPE, signed bias and observed coverage of the 80% and 95% prediction intervals.
- **Commercial scenarios.** I separate changes in total prescriptions from shifts between manufacturers and changes in synthetic gross revenue per prescription. This lets a reader see how rising volume and falling revenue per prescription can pull in different directions. The nutrition adjustment uses a declared sensitivity and starts after the configured lag.
- **Research boundaries.** The nutrition relationship was built into the simulation. Comparing levels with monthly changes helps explain why two upward trends can look related. Neither correlation establishes a real commercial effect. The model uses aggregate synthetic records and contains no patient data.

## Would I use this forecast?

At three months ahead, SARIMAX had **0.3% WAPE** for simulated Zepbound prescriptions, compared with **30.6%** for the last value baseline. At six months, the errors rose to **21.6%** and **39.5%**, respectively. WAPE measures absolute forecast error relative to observed volume. SARIMAX did better in both comparisons, but each horizon had just **one held out observation**. I’d keep it as a candidate and test it on more months before relying on it for planning.

## What I’d ask for on day one

- **Monthly prescription fills by brand** to test the forecast against real dispensing data.
- **Insurer coverage change dates** to check whether fill patterns shifted afterward and what else changed at the same time.
- **Independent nutrition sales** to see whether actual purchases show the kind of lag I simulated.

## Run locally

The default local build includes the simulation. To include public claims, run `python -m glp1_market.medicare` after installation and set `GLP1_MEDICARE_DATA=.cache/medicare.json` in your shell before running the pipeline. GitHub Actions includes the claims automatically.

Run the pipeline and open `outputs/dashboard.html` in a browser. The dashboard also works offline. You can also open a successful **Portfolio checks** run in the repository’s **Actions** tab, download the **glp1-market-lab** artifact, and open `dashboard.html` from the extracted folder.

```bash
git clone https://github.com/rayanatwork2004-alt/glp1-market-dynamics-forecasting.git
cd glp1-market-dynamics-forecasting
python -m venv .venv
```

Activate the environment with `.\.venv\Scripts\Activate.ps1` on Windows PowerShell or `source .venv/bin/activate` on macOS or Linux.

```bash
python -m pip install -e ".[dev]"
python run_pipeline.py
python -m pytest
```

The pipeline saves the interactive dashboard, the original static charts, and CSVs for the scorecard, individual held out predictions and commercial scenarios. The Python package lives in [src/glp1_market](src/glp1_market), with the method and metric definitions in [docs](docs).


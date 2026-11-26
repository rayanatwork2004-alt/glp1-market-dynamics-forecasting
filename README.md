# GLP-1 Market Lab

**A healthcare analytics project on prescription demand, brand competition, and nutrition sales.**

This is my first healthcare analytics project. I combined what I learned in school with my own research into the pharmaceutical industry. An obesity market brief made me curious about what drives prescription demand. New treatments give patients more choices, and insurance coverage can affect which medicines they can get. I also wanted to explore whether growth in prescriptions could affect demand for related nutrition products.

My main question was simple. If coverage or competition changes, what should I look at first to understand prescription demand?

I use published Medicare Part D data to compare fills and spending for Ozempic, Wegovy, Mounjaro, and Zepbound and test simple forecasts where the annual history allows it. The dashboard also includes [public U.S. benchmarks](https://rayanatwork2004-alt.github.io/glp1-market-dynamics-forecasting/#evidence) for reported Wegovy volume, Foundayo affordability, and clinical trial results. A separate simulation uses 48 months of synthetic history to explore how changes in volume, share, and pricing could affect a forecast. The companion nutrition response is an assumption in that simulation and would need independent sales data to test.

## Explore the dashboard

**[Open the live dashboard](https://rayanatwork2004-alt.github.io/glp1-market-dynamics-forecasting/)**

Start with **Medicare Part D** to see published fills, spending, share of the four brands, and a forecast tested against published figures. For the simulation, open **Forecast audit → Zepbound → 3 months ahead**. Compare the two models, then switch to **6 months ahead** to see how the result changes.

| View | Question it answers |
| --- | --- |
| Medicare Part D (Prescription Drug Coverage) | How have real fills and spending changed for four selected brands, and how well do simple forecasts track them? |
| Canada context | What does the new Canadian semaglutide advisory tell us, and what evidence would we need to study its effects? |
| U.S. market benchmarks | What do real prescription volume estimates, published patient costs, and trial results tell us about competition and access? |
| Simulated market overview | Which brands gained share within this panel, and which manufacturers own them? |
| Forecast audit | Does SARIMAX beat the last observed value for the month I’m trying to predict? How often does the forecast range contain the simulated result? |
| Scenario explorer | How much of the difference from the base comes from more prescriptions, a shift between manufacturers, or a change in revenue per prescription? |

![Synthetic brand share over time](docs/assets/synthetic-brand-share.png)

In the simulation, Wegovy prescriptions rose from **972,443 in October 2025** to **992,972 in November**, while its share of the four brands fell from **28.4% to 26.1%**. The panel grew faster than Wegovy did. If I only looked at share, I’d miss that Wegovy’s prescription volume actually went up.

## How I built it

- **Real claims.** I use the published total for each brand. The annual figures let me compare full years. I show newer figures separately because they can be revised and may cover only part of a year. I calculate share only when all four brands have reported fills. Where I have enough history, I test whether a simple trend predicts the next year better than repeating the previous year. [Medicare methods and sources](docs/medicare.md)

- **Market data.** I generate monthly prescription counts, prices, and sales for the simulation. Months before a brand enters the simulated market count as zero for market share. I start training the forecast when the brand enters.
- **Forecast validation.** I use SARIMAX to forecast each brand from its own simulated history. I hide later months, make a forecast, and compare it with a simple guess that repeats the latest month. I check how far each guess was off, whether it tended to predict too high or too low, and how often the answer fell inside the forecast range. [Forecast methods](docs/methodology.md)
- **Commercial scenarios.** I separate changes in total prescriptions from shifts between manufacturers and changes in synthetic gross revenue per prescription. This lets a reader see how rising volume and falling revenue per prescription can pull in different directions. I choose how strongly simulated nutrition sales respond to a prescription change and how long that response takes.
- **Research boundaries.** The nutrition relationship was built into the simulation. Comparing levels with monthly changes helps explain why two upward trends can look related. Neither correlation establishes a real commercial effect. The model uses aggregate synthetic records and contains no patient data.

## Would I use this forecast?

At three months ahead, SARIMAX had **0.3% WAPE** for simulated Zepbound prescriptions, compared with **30.6%** for the last value baseline. At six months, the errors rose to **21.6%** and **39.5%**, respectively. WAPE measures absolute forecast error relative to observed volume. SARIMAX did better in both comparisons, but each comparison used just **one simulated month that the models hadn’t seen**. I’d keep it as a candidate and test it on more months before relying on it for planning.

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

The pipeline saves the interactive dashboard, the original static charts, and CSVs for the forecast scores, predictions, and scenarios. The Python package lives in [src/glp1_market](src/glp1_market), with the method and metric definitions in [docs](docs).


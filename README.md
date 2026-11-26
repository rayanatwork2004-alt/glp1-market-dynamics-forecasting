# GLP-1 Market Lab

**My first healthcare analytics project, exploring prescription trends for Ozempic, Wegovy, Mounjaro, and Zepbound.**

**[Open the interactive dashboard](https://rayanatwork2004-alt.github.io/glp1-market-dynamics-forecasting/?v=interaction-review)**

An obesity market brief got me interested in how new medicines, insurance coverage, and competition shape prescription demand. This project brings together what I learned in business school and my own research into the pharmaceutical industry.

## What the real data showed

**Mounjaro accounted for 49% of reported fills among the four brands in Medicare Part D from January to June 2026**, or about 7.1 million fills.

Medicare Part D is a U.S. prescription insurance program. These preliminary CMS figures may be revised. Fills include refills and can cover different treatment uses.

![Preliminary Medicare Part D fills across four brands from January to June 2026](docs/assets/medicare-fills.svg)

I also tested whether two simple methods could predict the next year of published Ozempic fills.

| Forecast method | Error score |
| --- | --- |
| Repeat the previous year's fills | 40.5% |
| Continue the earlier trend | 22.1% |

WAPE adds up the absolute forecast misses and divides by total actual fills. Lower is better. The trend method did better across three annual tests, which gives only limited evidence for planning.

[See the Medicare methods and sources](docs/medicare.md)

## Decisions behind the analysis

**Bringing in real data.** I started with simulated data, then wanted findings tied to published prescription counts. I added Medicare and Medicaid data and kept the synthetic examples for practising forecasts and scenarios.

**Keeping all four brands.** Gaps in the early Medicare data pushed me to investigate launch dates, coverage, and other sources. Adding Medicaid gave me another view of all four brands. Each program has its own section because coverage and populations differ.

**Leaving gaps visible.** Missing values raised questions I could investigate. I keep those counts blank and calculate share only when the required figures are available.

## Where to start in the dashboard

| View | What to look for |
| --- | --- |
| Medicare Part D | Reported fills, spending, and annual forecast checks |
| Medicaid | Quarterly counts for the four brands |
| Canada context | A safety advisory and questions for further research |
| U.S. market benchmarks | Published prescription, patient cost, and clinical figures |
| Simulated market | Synthetic volume and share |
| Forecast audit | Forecast checks using synthetic data |
| Scenario explorer | Synthetic coverage, competition, and pricing assumptions |

Start with Medicare and Medicaid, then explore the synthetic examples. Each source covers a particular population and period.

## Why I look at volume and share together

In the **synthetic example**, Wegovy fills rose from 972,443 in October 2025 to 992,972 in November. Its share fell from 28.4% to 26.1% because the combined volume of the four brands grew faster.

That is a useful business question to bring to real data. If a brand loses share, are its own prescriptions falling, or are competitors growing faster?

<details>
<summary>See the synthetic example chart</summary>

![Synthetic brand share over time](docs/assets/synthetic-brand-share.png)

</details>

## How I checked the synthetic forecast

SARIMAX is a time series model that uses earlier values and can account for recurring patterns. I compared it with repeating the latest month. Both methods predicted the same synthetic months using only earlier data.

Some newer brands have only one test month at a selected lead time. That gives little evidence about future reliability. The dashboard shows how many months were tested.

<details>
<summary>See the forecast scores and technical details</summary>

For synthetic Zepbound prescriptions, each row represents one test month for each method.

| Months ahead | SARIMAX WAPE | Repeat latest month WAPE |
| --- | --- | --- |
| 3 | 0.3% | 30.6% |
| 6 | 21.6% | 39.5% |

The audit also checks the size and direction of forecast misses, prediction ranges, and whether the model fitted successfully.

[Read the forecasting methods](docs/methodology.md)

</details>

## What would make the analysis stronger

- **More frequent real prescription data** to test forecasts on more periods.
- **Dates of insurance coverage changes** to investigate changes in fills alongside other events.
- **Independent nutrition sales data** to test the relationship assumed in the simulation.

The nutrition example uses an assumed response to prescription growth. It needs real sales data before it can support a commercial recommendation. The analysis uses public aggregate counts and synthetic records.

## Project files

The Python modules are in [src/glp1_market](src/glp1_market). The [methods](docs/methodology.md), [public data notes](docs/medicare.md), and [data dictionary](docs/data_dictionary.md) explain the calculations and sources.

GitHub checks the Python code and opens the generated dashboard in a browser to check its controls, downloads, keyboard input, and mobile layout before publishing.

<details>
<summary>Run the project locally</summary>

The default local build includes the simulation. The live dashboard also includes both public claims panels.

Clone the repository and create a Python environment.

```bash
git clone https://github.com/rayanatwork2004-alt/glp1-market-dynamics-forecasting.git
cd glp1-market-dynamics-forecasting
python -m venv .venv
```

Activate the environment with `.\.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on macOS or Linux.

Install the package, run the pipeline, and run the Python tests.

```bash
python -m pip install -e ".[dev]"
python run_pipeline.py
python -m pytest
```

Open `outputs/dashboard.html` in your browser. The pipeline also saves static charts and CSV files containing forecasts, scores, and scenario results.

To include the public claims panels locally, run these commands after installation. The environment variable commands below use Windows PowerShell.

```powershell
python -m glp1_market.medicare
python -m glp1_market.medicaid
$env:GLP1_MEDICARE_DATA = ".cache/medicare.json"
$env:GLP1_MEDICAID_DATA = ".cache/medicaid.json"
python run_pipeline.py
```

On macOS or Linux, use `export GLP1_MEDICARE_DATA=.cache/medicare.json` and `export GLP1_MEDICAID_DATA=.cache/medicaid.json` to set the same variables.

A successful **Portfolio checks** run in GitHub's **Actions** tab also provides a **glp1-market-lab** download. Extract it and open `dashboard.html` to view that build offline.

</details>

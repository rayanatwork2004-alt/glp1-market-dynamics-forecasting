# Medicare Part D methods

This analysis covers claims for Ozempic, Wegovy, Mounjaro and Zepbound in U.S. Medicare Part D. Claims include refills. Spending is gross Part D drug cost before manufacturer rebates. The dataset does not split fills by indication. I calculate each brand’s share by dividing its fills by the total for the four brands. I only show share when all four have reported fills for the same period.

The annual panel uses the 2024 annual CMS release, with fields for benefit years 2020–2024. The preliminary panel uses the current quarterly CMS API and keeps each reported period exactly as labeled. A preliminary period may cover several quarters. CMS can revise the figures as more claims come in. I use the published total for each brand and leave missing figures blank. I keep the annual and preliminary releases separate and use the periods as published.

The annual backtest uses only consecutive observations through the last finalized year. With five years of data, I start with two years to make the first forecast. I then move forward a year at a time and test three forecasts, each for the next year. The baseline repeats the latest annual count. The trend forecast adds the average annual change from the first to the last year of training. The smallest possible forecast is zero. I compare both forecasts against the same actual counts. WAPE is the sum of absolute misses divided by the sum of observed fills. A short history limits what the test says about future accuracy. The simulated SARIMAX analysis is a separate monthly exercise.

- [CMS annual data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug/)
- [CMS preliminary data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-quarterly-part-d-spending-by-drug)
- [Health Canada semaglutide advisory, November 25, 2026](https://recalls-rappels.canada.ca/en/alert-recall/health-canada-warns-very-rare-serious-risk-vision-loss-semaglutide-drugs)

The Canadian advisory is a regulatory event. Measuring any change in Canadian utilization would require comparable Canadian claims around the event and care in separating it from other changes.

## Why the early years look different

Ozempic and Mounjaro entered the U.S. market with type 2 diabetes indications. Wegovy and Zepbound initially entered with weight management indications, a use excluded by standard Part D. In 2024, Wegovy gained a cardiovascular indication and Zepbound gained a sleep apnea indication. Those uses are eligible for Part D coverage. The data do not identify which use generated a claim or why an individual field is missing.



- [FDA approval history](https://www.fda.gov/media/175358/download)
- [CMS background on Part D coverage for weight management drugs](https://public-inspection.federalregister.gov/2024-27939.pdf)
- [CMS examples of Part D coverage by indication](https://www.cms.gov/files/document/medicare-glp-1-bridge-expectations-faqs.pdf)

Medicaid’s [State Drug Utilization Data](https://www.medicaid.gov/medicaid/prescription-drugs/state-drug-utilization-data) provide a separate quarterly view of prescriptions paid by Medicaid. They could support a separate comparison, with attention to differences in state coverage and small counts that CMS hides.

## Other public evidence

The dashboard includes a separate retail benchmark from [the ISPOR research poster](https://www.ispor.org/docs/default-source/cti-meeting-21021-documents/6fe2eb97-d003-4dc0-b6d0-812e13795055.pdf). The poster reports shares across all four brands for January 2023 through October 2024 as a single study period. Those shares are not spliced into the Medicare series or used for forecasting. A [study of semaglutide fills by payment method](https://pmc.ncbi.nlm.nih.gov/articles/PMC11297375/) also documents early Wegovy retail fills, many of which were paid for by commercial insurance.

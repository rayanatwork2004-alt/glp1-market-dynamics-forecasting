# Medicare Part D methods

This analysis covers claims for Ozempic, Wegovy, Mounjaro and Zepbound in U.S. Medicare Part D. Claims include refills. Spending is gross Part D drug cost before manufacturer rebates. The dataset does not split fills by indication. I calculate each brand’s share by dividing its fills by the total for the four brands. I only show share when all four have reported fills for the same period.

The annual panel uses the 2024 annual CMS release, with fields for benefit years 2020–2024. The preliminary panel uses the current quarterly CMS API and keeps each reported period exactly as labeled. A preliminary period may cover several quarters. CMS can revise the figures as more claims come in. I use the published total for each brand and leave missing figures blank. I keep the annual and preliminary releases separate and use the periods as published.

The annual backtest uses only consecutive observations through the last finalized year. With five years of data, I start with two years to make the first forecast. I then move forward a year at a time and test three forecasts, each for the next year. The baseline repeats the latest annual count. The trend forecast adds the average annual change from the first to the last year of training. The smallest possible forecast is zero. I compare both forecasts against the same actual counts. WAPE is the sum of absolute misses divided by the sum of observed fills. A short history limits what the test says about future accuracy. The simulated SARIMAX analysis is a separate monthly exercise.

- [CMS annual data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug/)
- [CMS preliminary data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-quarterly-part-d-spending-by-drug)
- [Health Canada semaglutide advisory, November 25, 2026](https://recalls-rappels.canada.ca/en/alert-recall/health-canada-warns-very-rare-serious-risk-vision-loss-semaglutide-drugs)

The Canadian advisory is a regulatory event. Measuring any change in Canadian utilization would require comparable Canadian claims around the event and care in separating it from other changes.

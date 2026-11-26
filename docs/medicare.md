# Medicare Part D methods

The real-data panel covers claims for Ozempic, Wegovy, Mounjaro and Zepbound in U.S. Medicare Part D. Claims include refills. Spending is gross Part D drug cost before manufacturer rebates. The dataset does not split fills by indication. The share denominator is the four selected brands, and calculations require usable published fills for all four brands in the same window.

The annual panel uses the 2024 annual CMS release, with fields for benefit years 2020–2024. The preliminary panel uses the current quarterly CMS API and keeps each reported period exactly as labeled. A preliminary window may cover multiple quarters and counts can be revised after claims runout. We keep both releases separate, use the all-manufacturer rows, and display unavailable values as missing. We do not derive stand-alone quarters by subtracting totals from separate releases.

The annual backtest uses only consecutive observations through the last finalized year. With five usable years, there are three one-year-ahead tests starting with two training years. The baseline repeats the latest annual count. The trend alternative adds the average change per year from the first to the last training year, with a zero floor. The two models use the same targets. WAPE is the sum of absolute misses divided by the sum of observed fills. A short history limits what the test says about future accuracy. The simulated SARIMAX analysis is a separate monthly exercise.

- [CMS annual data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug/)
- [CMS preliminary data](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-quarterly-part-d-spending-by-drug)
- [Health Canada semaglutide advisory, November 25, 2026](https://recalls-rappels.canada.ca/en/alert-recall/health-canada-warns-very-rare-serious-risk-vision-loss-semaglutide-drugs)

The Canadian advisory is a regulatory event. Measuring any change in Canadian utilization would require comparable Canadian claims around the event and care in separating it from other changes.

# Methodology Notes

## Synthetic data design

The simulation uses a fixed random seed so the same settings produce the same numbers. Pharmaceutical volume combines monthly growth that varies by brand, slower growth as adoption increases, seasonal patterns, and random variation. NRx is sampled within a brand-specific 25%-35% range of TRx. Brands that enter later have zero prescriptions in the months before launch so every brand has the same calendar.

Companion nutrition demand is generated from lagged total GLP-1 TRx, cumulative class exposure, category-specific capture rates, organic category growth, seasonality, pricing inflation, and Gaussian noise. The default configuration deliberately places the strongest lead-lag signal at a two-month TRx lead.

## Timing of the nutrition response

I calculate two correlations at different time gaps:

- **Levels:** shows how the two series move together. If both grow over time, the correlation can look stronger.
- **First difference:** compares changes from one month to the next to see if the relationship still appears after removing much of the overall trend.

In the default simulation, both measures pick up the two month delay built into the data.

## Commercial metrics

Monthly and annual market share are calculated from TRx. HHI is the sum of squared percentage market shares and therefore uses the conventional 0-10,000 scale. CAGR uses the first and last positive annual observations for each segment so structural pre-launch zeroes do not create undefined or misleading growth rates. Annual YoY growth is included as a complementary metric.

## Forecasting

Segment forecasts use SARIMAX on `log1p` transformed values. Structural pre-launch zeroes are removed before model fitting. I try a small set of model settings because each series has only 26 to 48 months of data after launch. Among the models that fit successfully, I choose the one with the lowest AIC, a score that balances fit with model complexity. The pipeline exports 24 months of forecasts and prediction ranges. The dashboard displays the selected 1, 3, or 6 months ahead alongside the test results for that horizon.

To estimate gross revenue, I multiply each brand’s forecast prescriptions by its average simulated revenue per prescription over the previous 12 months. Companion nutrition revenue is forecast directly.

## Interpretation boundaries

The pipeline demonstrates healthcare commercial analytics methods; it does not estimate real prescription demand, causal nutrition effects, manufacturer net revenue, payer reimbursement, clinical outcomes, or investment value. A synthetic lead-lag relationship is not causal evidence.

## Forecast audit

For each brand or nutrition category, the backtest starts with at least 18 active months and moves through historical cutoffs three months apart. Each cutoff fits a fresh model using training data only. The historical months after the cutoff are used to score the 1, 3 and 6 month predictions. Each model is compared on the same dates within a segment and horizon. The newest brands have fewer cutoffs, and overlapping forecasts can produce dependent errors.

MAE is the typical absolute miss in the original units. RMSE gives more weight to large misses. WAPE divides the sum of absolute misses by the sum of absolute actuals. Bias averages prediction minus actual. The last value baseline has no prediction intervals. SARIMAX reports empirical interval coverage and the number of fits that did not converge. A model that did not converge is shown for transparency and should be interpreted cautiously. The final fit also reports lag 1 residual autocorrelation and a Ljung–Box p-value when degrees of freedom allow it. These are diagnostic signals, especially limited on short series.

The forecasts are inverse transformed from log1p. The point estimate is a back transformed log scale estimate without a mean bias adjustment. The prediction intervals are conditional on the model and exclude future commercial shocks. The 24 month forecast goes beyond the validated lead times.

## Competitive scenarios

The data use four named brands to make the example recognizable. TRx shares are panel shares. The scenario HHI uses **manufacturer** shares. The historical HHI CSV uses **brand** shares, a different unit of competition.

Broader access and tighter payer coverage apply illustrative changes in total TRx, the Lilly share of the panel, and synthetic gross revenue per TRx. The share transfer retains relative brand weights inside each manufacturer where both groups have positive baseline volume. The nutrition sensitivity adjusts only the incremental change from the prescription scenario after the configured lag. The percentages are assumptions, so the scenario outputs describe what follows if those assumptions hold.

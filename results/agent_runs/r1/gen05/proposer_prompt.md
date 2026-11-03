You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 5). Accuracy is the median of |ln(V_est / V)|
across firm-years, where V is the firm's actual enterprise value on June 30 after its fiscal year.
Lower is better. Recipes are scored only on exploration years FY2016-2019; the
best ones will later be tested ONCE on later years you will never see, so prefer rules with a
clear economic reason over fragile tweaks. Cover both multiples across your proposals.

RECIPE LANGUAGE
A recipe is one firm-agnostic peer-selection rule. For every target firm in every year the
engine (1) takes all other firms in the same fiscal year with a positive multiple (the target
itself is always excluded), (2) applies the hard screens in "filters", (3) if fewer than
"min_peers" survive, tries each "fallback" screen set in order, (4) ranks survivors by a
weighted distance on within-year z-scores of the "rank" features and keeps the "k" nearest,
(5) aggregates the peers' multiples with "agg" and multiplies by the target's own driver.

Fields
  multiple:   one of ['EV/EBITDA', 'EV/Sales']  (EV/EBITDA uses firms with positive EBITDA)
  filters:    list of screens, each either {"same": GROUP} or {"band": {"var": FEATURE, "width": number}}
              GROUP is one of ['industry_l2', 'industry_l3', 'industry_l4']  (2-, 3- and 4-digit SIC codes)
              a band keeps candidates whose feature is within ±width of the target's (raw units)
  rank:       {FEATURE: positive weight, ...}  (empty = no ranking; then k must be "all")
  k:          "all" or an integer 3-30
  agg:        one of ['harmonic_mean', 'mean', 'median', 'trimmed_mean']
  min_peers:  positive integer (default 3)
  fallback:   list of filter lists tried in order when too few peers survive

FEATURES (accounting only; ratio features are winsorized 1%/99% each year)
  - log_sales: log of sales (size)
  - log_assets: log of total assets (size)
  - sales_growth_1y: 1-year sales growth
  - sales_growth_3y: 3-year annualized sales growth (missing for FY2016-2017: not enough history)
  - gross_margin: gross profit / sales
  - ebitda_margin: EBITDA / sales
  - ebit_margin: EBIT / sales
  - net_margin: net income / sales
  - roic: EBIT x (1 - 25%) / (equity + debt - cash)
  - roe: net income / book equity
  - asset_turnover: sales / total assets
  - net_debt_to_ebitda: (debt - cash) / EBITDA
  - debt_to_assets: total debt / total assets
  - rnd_intensity: R&D / sales
  - capex_intensity: capital expenditure / sales

HARD RULES
  - No market-based inputs (price, market cap, EV) for the target: they are the answer.
  - Missing feature values: a target missing ALL rank features gets no estimate; candidates
    missing a used rank feature are dropped. Low coverage is penalized by the selection rule.

BASELINES (exploration years)
  EV/EBITDA: Industry median (L3, fallback L2) median 0.333, mean 0.513; Warranted multiple (Bhojraj-Lee regression) median 0.357, mean 0.492; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.380, mean 0.523
  EV/Sales: Industry median (L3, fallback L2) median 0.603, mean 0.945; Warranted multiple (Bhojraj-Lee regression) median 0.674, mean 0.837; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.691, mean 0.861

ARCHIVE: your earlier graded attempts, exploration scores only (21 graded)
  [g04-06] EV/EBITDA median 0.320 | mean 0.490 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.020
      EV/EBITDA | screen same industry_l2, band gross_margin±0.08 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band gross_margin±0.15] -> [same industry_l2]
      mechanism: Gross margin measures pricing power and product differentiation, which sets how long a firm can earn above its cost of capital (the competitive-advantage period). At equal near-term growth, a longer advantage period means a higher EV/EBITDA, and a broad 2-digit industry mixes branded and commodity producers. A gross-margin band inside the 2-digit industry keeps peers in the same competitive position, and ranking on growth, ROIC, net leverage and size matches the remaining drivers.
  [g01-01] EV/EBITDA median 0.322 | mean 0.484 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.030
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a Gordon-style valuation, EV/EBITDA rises with expected growth and with how efficiently growth is funded (ROIC), and falls with financial risk. Industry peers share the same business risk and accounting conventions, so ranking within the industry on growth, ROIC and net leverage should isolate peers with the same fundamental multiple drivers, closer than the industry as a whole.
  [g01-05] EV/EBITDA median 0.322 | mean 0.493 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.010
      EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Narrow 4-digit SIC peers share product markets, customers and cyclicality, so they face the same discount rate and the same long-run growth outlook. Within that narrow group, a small ranking on growth and ROIC refines the match, and the cascade to L3 and L2 keeps coverage when narrow industries are thin.
  [g04-04] EV/EBITDA median 0.324 | mean 0.493 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.018
      EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Because R&D is expensed, R&D-intensive firms report EBITDA that understates their pre-investment cash flow and carry growth options that the current EBITDA does not reflect, so they trade at systematically higher EV/EBITDA than low-R&D firms in the same broad industry. A hard band on R&D intensity inside the 2-digit industry keeps peers in the same expensing and growth-option regime, and ranking on growth, ROIC and net leverage matches the standard Gordon-model drivers; firms without R&D data fall back to plain industry peers.
  [g01-04] EV/EBITDA median 0.325 | mean 0.492 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.022
      EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA overstates distributable cash flow for capital-heavy firms, because capex absorbs part of it. So at equal growth, firms with higher capex intensity should trade at lower EBITDA multiples. Size, in turn, proxies for risk and liquidity premia. Matching on reinvestment needs, growth and margin within a 2-digit industry and a size band should capture both effects.
  [g02-02] EV/EBITDA median 0.326 | mean 0.486 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.028
      EV/EBITDA | screen same industry_l2, band log_sales±2 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA leaves out depreciation and amortization, but D&A stands for real asset-replacement costs. The gap between EBITDA margin and EBIT margin measures how much of EBITDA goes to maintaining the asset base, so firms with the same EBITDA but heavier D&A should trade at lower EBITDA multiples. Matching on both margins at once (plus growth and balance-sheet leverage), within a 2-digit industry and a size band, picks peers whose EBITDA converts into operating profit at the same rate.
  [g03-02] EV/EBITDA median 0.327 | mean 0.499 | coverage 98.3% | beats industry 4/4 yrs | gain vs industry +0.011
      EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
      mechanism: Expected growth is the single largest driver of an EBITDA multiple, and fast and slow growers in one industry are priced as different assets. A hard band on 1-year sales growth inside the 2-digit industry puts every peer in the same growth regime, and ranking on ROIC, capex intensity, net leverage and asset size then matches how cheaply that growth is funded and how risky the claim is.
  [g02-03] EV/EBITDA median 0.334 | mean 0.501 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.010
      EV/EBITDA | screen same industry_l3, band net_debt_to_ebitda±2 | rank ebitda_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±2] -> [same industry_l2]
      mechanism: Enterprise-value multiples of heavily indebted firms show distress costs, tax shields and covenant constraints that unlevered peers do not share. A hard band on net debt/EBITDA keeps every peer in the same capital-structure regime before the ranking. Within that band and the 3-digit industry, ranking on margin, growth and asset turnover matches profitability and capital efficiency, and a trimmed mean limits the influence of any one outlier peer.
  [g02-01] EV/EBITDA median 0.334 | mean 0.518 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry -0.003
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.75, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Multiples are ratios of value to earnings, so averaging them arithmetically overweights the high-multiple peers. The harmonic mean is equivalent to pooling peer values over pooled earnings, which is less biased upward. Within 3-digit industry peers, ranking on growth, ROIC and reinvestment needs (capex intensity) matches the three drivers of the value-to-EBITDA ratio in a steady-state model: g, the return on reinvested capital, and the part of EBITDA that is not free cash flow.
  [g03-03] EV/EBITDA median 0.342 | mean 0.496 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.018
      EV/EBITDA | screen band sales_growth_1y±0.1, band net_debt_to_ebitda±1.5 | rank roic 1, ebit_margin 1, ebitda_margin 1, capex_intensity 0.5, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.2] -> []
      mechanism: An EBITDA multiple equals value over a pre-reinvestment cash flow, so it depends on growth, on the return earned on reinvestment, on the share of EBITDA lost to D&A and capex, and on financial risk, none of which require a shared SIC code. Boxing candidates on growth and net leverage across the whole cross-section and ranking on ROIC, both margins (whose gap is the D&A burden), capex intensity and size finds fundamental twins that industry codes can miss.
  [g03-06] EV/Sales median 0.378 | mean 0.552 | coverage 92.0% | beats industry 4/4 yrs | gain vs industry +0.262
      EV/Sales | screen band ebitda_margin±0.03, band log_sales±1.5 | rank sales_growth_1y 1, gross_margin 1, debt_to_assets 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: With the cash margin held fixed, sales multiples still differ by the discount rate, which falls with firm size (liquidity, diversification, access to capital) and rises with balance-sheet distress risk. Hard bands on EBITDA margin and on log sales put peers at the same profitability and risk-premium level, and ranking on growth, gross margin and debt-to-assets matches duration, pricing power and leverage risk.
  [g04-02] EV/Sales median 0.381 | mean 0.568 | coverage 92.0% | beats industry 4/4 yrs | gain vs industry +0.249
      EV/Sales | screen band ebitda_margin±0.03, band asset_turnover±0.25 | rank sales_growth_1y 1, roic 1, debt_to_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: EV/Sales equals EV/Assets divided by asset turnover, and EBITDA margin times asset turnover is the pre-tax cash return on assets. Hard bands on both margin and turnover fix how much cash each dollar of sales produces and how much capital stands behind each dollar of sales, so peers share the same return on the asset base whatever their SIC code. Ranking on growth, ROIC and debt-to-assets then matches duration, value creation on new capital and financial risk.
  [g02-04] EV/Sales median 0.385 | mean 0.559 | coverage 93.2% | beats industry 4/4 yrs | gain vs industry +0.262
      EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_sales 1, capex_intensity 1, gross_margin 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.08]
      mechanism: EV/Sales is roughly cash margin times a duration factor that depends on growth. Hard bands on EBITDA margin and on sales growth together pin down both parts directly, whatever the SIC code. Inside that box, ranking on size, capital intensity and gross margin covers the remaining risk and reinvestment differences. The fallbacks drop the growth constraint first and then widen the margin band.
  [g01-06] EV/Sales median 0.385 | mean 0.564 | coverage 92.1% | beats industry 4/4 yrs | gain vs industry +0.252
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
      mechanism: A hard band on EBITDA margin makes sure every peer converts sales into cash flow at a similar rate, which is the main driver of EV/Sales. Within that band and the 3-digit industry, ranking on growth and size captures the remaining differences in duration and risk. The fallbacks relax the industry screen before they relax the margin match.
  [g02-05] EV/Sales median 0.389 | mean 0.594 | coverage 93.1% | beats industry 4/4 yrs | gain vs industry +0.229
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=10, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
      mechanism: Once a margin band fixes how much cash each dollar of sales produces, the rest of the EV/Sales spread comes from how much capital that growth needs, measured by ROIC and asset turnover. Within a 2-digit industry and an EBITDA-margin band, ranking on growth, ROIC and turnover matches value creation per dollar of sales. The harmonic mean then guards against the right-skew that sales multiples typically have.
  [g04-01] EV/Sales median 0.390 | mean 0.558 | coverage 92.0% | beats industry 4/4 yrs | gain vs industry +0.255
      EV/Sales | screen band ebitda_margin±0.03, band rnd_intensity±0.03 | rank sales_growth_1y 1, gross_margin 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: R&D is expensed, so two firms with the same reported EBITDA margin can have very different economic cash margins: the R&D-heavy firm is investing part of its margin in intangible capital that markets capitalize into value, which raises its EV/Sales. A hard band on R&D intensity next to the EBITDA-margin band puts peers at the same reported margin AND the same hidden investment rate, and ranking on growth, gross margin and size then matches duration, pricing power and the risk premium. Fallbacks drop the R&D constraint (for firms with no reported R&D) before widening the margin band.
  [g03-05] EV/Sales median 0.405 | mean 0.594 | coverage 93.0% | beats industry 4/4 yrs | gain vs industry +0.234
      EV/Sales | screen same industry_l2, band ebit_margin±0.03 | rank ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06]
      mechanism: EBIT margin is profit after the cost of replacing the asset base (D&A), so it is a better proxy than EBITDA margin for the sustainable operating cash a dollar of sales produces. A hard EBIT-margin band inside the 2-digit industry fixes that term, and ranking on EBITDA margin (which, given EBIT margin, measures D&A intensity), growth and size matches the remaining differences in asset intensity, duration and risk.
  [g03-04] EV/Sales median 0.410 | mean 0.581 | coverage 92.6% | beats industry 4/4 yrs | gain vs industry +0.238
      EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.04 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
      mechanism: EV/Sales scales with the free cash flow each dollar of sales produces, and pre-tax free cash margin is roughly EBITDA margin minus capex intensity. Hard bands on both put every peer at the same cash conversion whatever its SIC code, and ranking on growth, ROIC and size then matches duration, value creation on reinvestment and the risk premium.
  [g01-03] EV/Sales median 0.420 | mean 0.672 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.274
      EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
      mechanism: Once margins, growth and capital intensity are matched, firms produce similar free cash flow per dollar of sales, whatever their SIC code. Searching the whole cross-section for profitability twins gives a larger and closer-matched peer set than industry codes, which often group businesses with very different economics.
  [g01-02] EV/Sales median 0.478 | mean 0.781 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.164
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in profitability. Within a broad 2-digit industry, picking peers with the closest EBITDA and gross margins (plus growth) cancels out the margin term that a plain industry median ignores.
  [g02-06] EV/Sales median 0.565 | mean 0.910 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.034
      EV/Sales | screen same industry_l4 | rank ebitda_margin 2, ebit_margin 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: 4-digit SIC peers share product markets, pricing power and cyclicality, so their discount rates and long-run growth are similar. Inside that narrow group, ranking mainly on EBITDA and EBIT margins removes the profitability term that drives EV/Sales. The cascade widens the industry only as far as coverage needs, so the narrow industry match is kept whenever it is available.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g03-01] rejected: critic: This recombines components already tried without a new economic idea: the size-band-inside-industry discount-rate mechanism was tested in g01-04 (L2 + log_sales±1.5), and the L3 growth/ROIC/ca
  [g04-03] rejected: critic: This uses exactly the five features of g02-04 (EBITDA-margin band, growth, size, capex, gross margin) with screen and rank swapped, and g03-06 already ranked on gross margin at full weight ins
  [g04-05] rejected: critic: Margin-cycle position means a firm's margin compared with its own normal level, but a band on the raw EBITDA margin level cannot tell a structurally low-margin firm from one at a cyclical trou

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

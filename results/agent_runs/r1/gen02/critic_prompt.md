You are an independent referee for a valuation research project. A proposer has submitted
comps recipes. You decide which may be tested. You do NOT see any results, and you must not try
to find any: judge only the logic.

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

Approve a proposal only if ALL hold:
  1. The mechanism is a specific, economically sensible reason why the selected peers should
     trade at a similar multiple to the target.
  2. The recipe actually implements that mechanism (the screens and rank features match it).
  3. It is not a trivial variant of a recipe already tried (listed below): changing only k by a
     few, one weight slightly, or the aggregator alone is trivial; a new feature, screen or
     economic idea is not.
  4. The prediction is falsifiable.
Reject otherwise, with a one-sentence reason the proposer can learn from.

RECIPES ALREADY TRIED (no scores shown)
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-03] EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
  [g01-04] EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]

PROPOSALS
  (0) harmonic_l3_reinvestment_adjusted_ebitda
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.75, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Multiples are ratios of value to earnings, so averaging them arithmetically overweights the high-multiple peers. The harmonic mean is equivalent to pooling peer values over pooled earnings, which is less biased upward. Within 3-digit industry peers, ranking on growth, ROIC and reinvestment needs (capex intensity) matches the three drivers of the value-to-EBITDA ratio in a steady-state model: g, the return on reinvested capital, and the part of EBITDA that is not free cash flow.
      prediction: Median error at or below 0.325 and beats the L3/L2 industry median in at least 3 of 4 years, with a mean error below the industry baseline's 0.513.

  (1) da_burden_twins_ebitda
      recipe: EV/EBITDA | screen same industry_l2, band log_sales±2 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA leaves out depreciation and amortization, but D&A stands for real asset-replacement costs. The gap between EBITDA margin and EBIT margin measures how much of EBITDA goes to maintaining the asset base, so firms with the same EBITDA but heavier D&A should trade at lower EBITDA multiples. Matching on both margins at once (plus growth and balance-sheet leverage), within a 2-digit industry and a size band, picks peers whose EBITDA converts into operating profit at the same rate.
      prediction: Beats the L3/L2 industry median in at least 3 of 4 years, with a median error at or below 0.330.

  (2) leverage_banded_industry_ebitda
      recipe: EV/EBITDA | screen same industry_l3, band net_debt_to_ebitda±2 | rank ebitda_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±2] -> [same industry_l2]
      mechanism: Enterprise-value multiples of heavily indebted firms show distress costs, tax shields and covenant constraints that unlevered peers do not share. A hard band on net debt/EBITDA keeps every peer in the same capital-structure regime before the ranking. Within that band and the 3-digit industry, ranking on margin, growth and asset turnover matches profitability and capital efficiency, and a trimmed mean limits the influence of any one outlier peer.
      prediction: Beats the L3/L2 industry median in at least 3 of 4 years, with the largest gain among firms in the top tercile of net debt/EBITDA.

  (3) margin_growth_box_sales
      recipe: EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_sales 1, capex_intensity 1, gross_margin 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.08]
      mechanism: EV/Sales is roughly cash margin times a duration factor that depends on growth. Hard bands on EBITDA margin and on sales growth together pin down both parts directly, whatever the SIC code. Inside that box, ranking on size, capital intensity and gross margin covers the remaining risk and reinvestment differences. The fallbacks drop the growth constraint first and then widen the margin band.
      prediction: Median error at or below 0.40 and beats the L3/L2 industry median in all 4 years, with coverage of at least 95%.

  (4) harmonic_l2_margin_band_roic_sales
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=10, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
      mechanism: Once a margin band fixes how much cash each dollar of sales produces, the rest of the EV/Sales spread comes from how much capital that growth needs, measured by ROIC and asset turnover. Within a 2-digit industry and an EBITDA-margin band, ranking on growth, ROIC and turnover matches value creation per dollar of sales. The harmonic mean then guards against the right-skew that sales multiples typically have.
      prediction: Beats the L3/L2 industry median in at least 3 of 4 years, with a mean error below 0.60.

  (5) l4_cascade_profitability_twins_sales
      recipe: EV/Sales | screen same industry_l4 | rank ebitda_margin 2, ebit_margin 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: 4-digit SIC peers share product markets, pricing power and cyclicality, so their discount rates and long-run growth are similar. Inside that narrow group, ranking mainly on EBITDA and EBIT margins removes the profitability term that drives EV/Sales. The cascade widens the industry only as far as coverage needs, so the narrow industry match is kept whenever it is available.
      prediction: Beats the L3/L2 industry median in all 4 years, with a median error at or below 0.45.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

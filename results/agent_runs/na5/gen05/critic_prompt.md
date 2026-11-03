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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.5, sales_growth_1y 1, log_assets 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, capex_intensity 0.5, log_assets 0.5 | k=20, harmonic_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, sales_growth_1y 0.5, asset_turnover 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
  [g02-03] EV/EBITDA | screen same industry_l4 | rank log_sales 1, ebitda_margin 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, gross_margin 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g02-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, asset_turnover 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, ebitda_margin 1, net_debt_to_ebitda 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, capex_intensity 2, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | rank sales_growth_1y 2, roic 2, capex_intensity 1, net_debt_to_ebitda 1, ebitda_margin 1 | k=20, trimmed_mean, min_peers=3
  [g03-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g03-05] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=3
  [g03-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 2, log_sales 1, gross_margin 1 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
  [g04-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, roic 1.5, log_sales 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g04-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g04-03] EV/EBITDA | rank sales_growth_1y 1.5, roic 1.5, capex_intensity 1, ebitda_margin 0.5, debt_to_assets 0.5, log_sales 1 | k=15, median, min_peers=3
  [g04-05] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 0.5, log_sales 0.5 | k=12, median, min_peers=3
  [g04-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 1, ebitda_margin 1 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]

PROPOSALS
  (0) EBITDA_L2_growth_return_risk_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: In a DCF, EV/EBITDA is driven by expected growth, the return on reinvested capital (which sets how much cash flow growth costs), and risk. Within a broad 2-digit industry that shares cost of capital and business cycle, picking the firms closest on growth, ROIC, leverage and size should isolate peers with the same fundamental multiple, and the harmonic mean avoids being pulled up by a few richly priced peers.
      prediction: Median |ln error| below 0.333 (industry median L3) in at least 3 of 4 exploration years, and pooled median at or below 0.32.

  (1) EBITDA_L3_size_growth_median
      recipe: EV/EBITDA | screen same industry_l3 | rank log_assets 1, sales_growth_1y 1, ebitda_margin 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit industry peers share products, customers and regulation, and within that group size (log assets) proxies for diversification and lower risk while 1-year growth and EBITDA margin capture the growth and quality differences that justify a higher multiple. Keeping the 8 nearest refines the plain industry median without moving outside the industry.
      prediction: Beats the L3/L2 industry median on median |ln error| in at least 3 of 4 years, with a pooled improvement of at least 0.01.

  (2) EBITDA_crossindustry_fundamentals
      recipe: EV/EBITDA | rank sales_growth_1y 1, roic 1, rnd_intensity 1, capex_intensity 0.5, debt_to_assets 0.5 | k=20, harmonic_mean, min_peers=3
      mechanism: If multiples reflect fundamentals rather than industry labels, firms anywhere in the market with similar growth, returns on capital, R&D and capital intensity, and leverage should trade at similar EV/EBITDA. A larger peer set (k=20) and harmonic mean reduce noise from the loss of the industry anchor.
      prediction: Pooled median |ln error| within 0.03 of the industry median (below 0.36) and beats the Bhojraj-Lee warranted-multiple peers (0.380) in at least 3 of 4 years.

  (3) Sales_L2_margin_matched_harmonic
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so margin is the dominant driver of the sales multiple; matching on EBITDA and gross margin within a 2-digit industry, plus growth, should remove most of the dispersion that ruins a plain industry EV/Sales median. The harmonic mean guards against high-multiple outliers.
      prediction: Pooled median |ln error| below 0.55 and beats the industry median (0.603) in all 4 exploration years.

  (4) Sales_margin_band_crossindustry
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, rnd_intensity 0.5, log_sales 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales scales with profitability, a hard band on EBITDA margin across all industries groups firms that convert sales to cash at the same rate; ranking further on margin, growth, R&D intensity (future margins not yet in EBITDA) and size picks peers with similar value per dollar of sales.
      prediction: Beats the industry median EV/Sales (0.603) on pooled median |ln error| and in at least 3 of 4 years.

  (5) Sales_L3_margin_turnover_tight
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, firms with the same gross and EBITDA margins and asset turnover have the same economic model (pricing power and capital required per dollar of sales), so their sales multiples should converge. A small peer set (k=6) keeps only the closest business-model twins.
      prediction: Pooled median |ln error| below 0.58 and beats the industry median in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

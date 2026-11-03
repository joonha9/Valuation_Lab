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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g01-03] EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | rank ebitda_margin 2, sales_growth_1y 1, asset_turnover 0.5, gross_margin 0.5 | k=15, harmonic_mean, min_peers=3
  [g01-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, roic 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2]
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, ebitda_margin 1, log_sales 1 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback []
  [g02-03] EV/EBITDA | screen same industry_l4 | k=all, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g02-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1, sales_growth_1y 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, roic 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-02] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g03-03] EV/EBITDA | screen same industry_l3 | rank log_sales 1, capex_intensity 1 | k=12, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, capex_intensity 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g03-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
  [g04-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, net_debt_to_ebitda 0.75, log_sales 0.75 | k=8, median, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l3 | rank roic 1, sales_growth_1y 1, capex_intensity 1 | k=10, harmonic_mean, min_peers=6 | fallback [same industry_l2] -> []
  [g04-03] EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 1, gross_margin 0.75, roic 1, capex_intensity 0.75, log_assets 0.5 | k=12, median, min_peers=3
  [g04-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g04-05] EV/Sales | rank ebitda_margin 3, net_margin 1, gross_margin 1, sales_growth_1y 1 | k=15, harmonic_mean, min_peers=3
  [g04-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, asset_turnover 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [same industry_l2] -> []

PROPOSALS
  (0) EBITDA_L3_growth_reinvestment_risk
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a steady-state DCF, EV/EBITDA rises with expected growth and with the efficiency of reinvestment (ROIC), and falls with capital intensity and financial risk. Within a 3-digit industry, choosing the peers closest on growth, ROIC, capex intensity and leverage matches those value drivers more closely than taking the whole industry.
      prediction: Median |ln(V_est/V)| below the 0.333 L3 industry-median baseline in at least 3 of 4 exploration years.

  (1) EBITDA_L2_size_growth_margin_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank log_sales 1, sales_growth_1y 1, ebitda_margin 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: Larger, faster-growing, higher-margin firms in the same broad sector carry lower risk and more durable cash flows, so they trade at similar EBITDA multiples. The harmonic mean averages earnings yields instead of multiples, so a few richly priced peers have less pull and the upward bias of the arithmetic mean goes away.
      prediction: Pooled median error at or below 0.330 and mean error below 0.500 (both baselines beaten on the mean).

  (2) EBITDA_crossindustry_fundamentals
      recipe: EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, ebitda_margin 0.5, log_assets 0.5, debt_to_assets 0.5 | k=15, median, min_peers=3
      mechanism: Valuation theory says the multiple depends on growth, return on capital, reinvestment need and risk, not on the SIC label. Picking peers from all industries on those fundamentals alone tests whether matching fundamentals across industries does as well as the industry screen when an industry has few members or a mixed set of firms.
      prediction: Median error within 0.02 of the L3 industry median (0.333) and below the Bhojraj-Lee warranted-multiple peers (0.380) in all 4 years.

  (3) SALES_L2_margin_band
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.1 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.1] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times the EBITDA margin, so firms with very different margins cannot share a sales multiple even within one sector. A hard ±10-point EBITDA-margin band inside the 2-digit industry, followed by ranking on margins and growth, removes the biggest source of error in EV/Sales.
      prediction: Median error below 0.50 in every exploration year, beating the 0.603 industry-median baseline in 4 of 4 years.

  (4) SALES_crossindustry_profitability_harmonic
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, asset_turnover 1 | k=20, harmonic_mean, min_peers=3
      mechanism: A dollar of sales is worth what it turns into as cash flow: profitability (EBITDA and gross margin), growth and capital needs (asset turnover). Matching on these across all industries and taking the harmonic mean of the 20 nearest peers' sales multiples gives a stable, less skewed estimate that leans on economics more than SIC codes.
      prediction: Median error below 0.55 pooled and below the Bhojraj-Lee regression (0.674) in all 4 years.

  (5) SALES_L3_margin_growth_nearest
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, net_margin 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Inside a narrow 3-digit industry the business model is broadly shared, so what is left of the variation in sales multiples comes mostly from profitability and growth. Ranking same-industry peers on EBITDA margin, net margin and growth, and keeping a small nearest set, should capture this.
      prediction: Beats the L3 industry-median EV/Sales baseline (0.603) by at least 0.08 in median error in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

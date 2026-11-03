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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_assets 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank gross_margin 1, ebitda_margin 1, capex_intensity 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, roic 1, log_sales 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-03] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-05] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, roic 1, log_sales 0.5 | k=15, median, min_peers=3
  [g02-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03] -> [same industry_l2]
  [g03-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, ebit_margin 1, sales_growth_1y 0.75, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=5 | fallback []
  [g03-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g03-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 1.5, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
  [g03-06] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, capex_intensity 0.75, asset_turnover 0.75, log_sales 0.5 | k=20, median, min_peers=3

PROPOSALS
  (0) EBITDA_L2_growth_return_size
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_assets 0.75 | k=10, median, min_peers=5 | fallback []
      mechanism: In a constant-growth DCF, EV/EBITDA rises with expected growth and with how efficiently growth is funded (ROIC), and falls with risk, which shrinks with size. Within a broad 2-digit industry that shares the same macro exposure, the peers closest on growth, ROIC and size should have the most similar fundamental multiple.
      prediction: Median |ln error| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years, with pooled median at or below 0.32.

  (1) EBITDA_L3_leverage_size_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Among close product-market rivals, the EV/EBITDA multiple mostly differs by financial risk and scale: highly levered or small firms have higher cost of capital and lower multiples. The harmonic mean is the right average for price ratios because it averages the yield (EBITDA/EV) and is not pulled up by a few very high multiples.
      prediction: Pooled median error at or below 0.33 and a lower mean error than the L3 industry median (0.513) because the harmonic mean damps upward outliers.

  (2) EBITDA_L3_all_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | k=all, harmonic_mean, min_peers=3 | fallback [same industry_l2]
      mechanism: A minimal change to the industry-median benchmark: firms in the same 3-digit industry share demand, cost structure and risk, so their typical multiple is a good anchor. Aggregating with the harmonic mean averages earnings yields, which is the theoretically consistent and less outlier-sensitive way to combine multiples.
      prediction: Matches or beats the L3 industry-median baseline median error (0.333) in at least 3 of 4 years with a lower mean error.

  (3) Sales_margin_band_crossindustry
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales scales almost one-for-one with operating margin, firms with similar EBITDA margins, gross margins and growth should trade at similar sales multiples even across industry lines. A hard margin band ensures peers have comparable profitability before ranking on the remaining value drivers.
      prediction: Pooled median error below 0.55 and better than the L3 industry median in at least 3 of 4 years.

  (4) Sales_L3_margin_harmonic
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Close product-market rivals share technology and cost structure, and within that group the sales multiple varies chiefly with operating and gross margins. Selecting the nearest margin-matched rivals and averaging with the harmonic mean keeps the estimate from being inflated by a few richly valued peers.
      prediction: Pooled median error below 0.55 and mean error below the L3 industry median's 0.945.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

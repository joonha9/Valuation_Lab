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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1.5, net_debt_to_ebitda 1, log_sales 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, log_assets 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, net_debt_to_ebitda 1, ebitda_margin 0.5, log_sales 1 | k=15, harmonic_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, gross_margin 1, asset_turnover 0.5, roic 0.5 | k=15, median, min_peers=3
  [g01-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 1, ebitda_margin 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, gross_margin 0.75, debt_to_assets 0.5, log_sales 0.5 | k=15, median, min_peers=3
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, roic 0.75, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> [band ebitda_margin±0.15] -> []
  [g02-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 3, sales_growth_1y 1, asset_turnover 0.5, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) ebitda_l2_growth_return_risk
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 1, net_debt_to_ebitda 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: By DCF logic EV/EBITDA rises with expected growth and return on capital and falls with risk. Keeping peers in the same 2-digit industry holds business risk roughly constant, and ranking on 1-year growth, ROIC, EBITDA margin and leverage within that industry picks the peers whose value drivers match the target most closely.
      prediction: Median |ln error| below the L3/L2 industry-median baseline (0.333) in at least 3 of 4 exploration years, and below 0.320 pooled.

  (1) ebitda_l3_harmonic_fundamentals
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 0.5, roic 1, sales_growth_1y 1 | k=6, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit industry peers share technology, customers and cyclicality. Within that group, size, ROIC and growth separate mature cash cows from growth franchises. The harmonic mean is the right average for price ratios (it averages earnings yields) and limits the upward pull of peers with very high multiples.
      prediction: Pooled median error below 0.333 and mean error below 0.50; beats the industry median in at least 3 of 4 years.

  (2) ebitda_crossindustry_capex_profile
      recipe: EV/EBITDA | rank capex_intensity 1, ebitda_margin 1, sales_growth_1y 1, roic 1, gross_margin 0.5 | k=15, median, min_peers=3
      mechanism: EBITDA overstates free cash flow most for capital-intensive firms, so capex intensity should set EV/EBITDA together with growth and ROIC. Peers matched on capex intensity, margins, growth and returns across all industries capture the drivers directly, which helps targets in thin or mixed SIC codes.
      prediction: Pooled median error within 0.02 of the industry median (at most 0.353) and lower mean error than the industry median (below 0.513).

  (3) sales_l2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA, so differences in margin are the main reason EV/Sales varies within an industry. Matching on EBITDA and gross margin (weighted most heavily), plus growth, inside the 2-digit industry removes most of the variation that an unconditional industry median leaves in.
      prediction: Pooled median error below 0.50, clearly beating the industry median (0.603) in all 4 exploration years.

  (4) sales_margin_band_harmonic
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: A hard EBITDA-margin band makes every peer turn sales into cash flow at a similar rate. Ranking inside the band on margin, gross margin, growth and capex intensity then matches growth and reinvestment needs. The harmonic mean limits the influence of loss-making or hyper-growth peers with very high EV/Sales.
      prediction: Pooled median error below 0.55 and mean error below 0.837 (the warranted-multiple baseline); beats the industry median in at least 3 of 4 years.

  (5) sales_l3_margin_return_turnover
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow 3-digit industry, EV/Sales should rise with margin, return on capital and growth. Asset turnover separates asset-light from asset-heavy business models that have the same margin. Close industry peers matched on these drivers should share the target's sales multiple.
      prediction: Pooled median error below 0.52 and beats the industry median in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

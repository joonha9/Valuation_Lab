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

PROPOSALS
  (0) EBITDA_L3_growth_reinvestment
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, roic 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Under a DCF, EV/EBITDA is driven by expected growth, by how much of EBITDA must be reinvested (capex) and by the return on that reinvestment. Same-industry peers share risk and accounting conventions, and ranking within the industry on growth, capex intensity and ROIC picks the peers whose cash-conversion and growth profile match the target's.
      prediction: Median |ln error| below the L3/L2 industry median (0.333) when pooled over FY2016-2019, and lower than the industry median in at least 3 of 4 years.

  (1) EBITDA_L2_quality_leverage
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: A wider 2-digit industry pool gives enough candidates to match on drivers: margin quality and growth set the expected path of EBITDA, net leverage proxies financial risk, and size proxies diversification and liquidity. Firms alike on all four should be priced at similar EBITDA multiples.
      prediction: Pooled median |ln error| at or below 0.33 and below the Bhojraj-Lee warranted-multiple peers (0.380) in every exploration year.

  (2) EBITDA_L3_size_capex_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 1, capex_intensity 1 | k=12, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: The harmonic mean of multiples equals the ratio of aggregate value to aggregate EBITDA, so it is not pulled up by peers with temporarily low EBITDA, which is the main source of upward bias in EBITDA multiples. Matching peers within the 3-digit industry on size and capital intensity aligns scale economies and maintenance-capex burden.
      prediction: Pooled mean |ln error| below the industry-median baseline mean (0.513), with median |ln error| within 0.02 of 0.333 or better.

  (3) Sales_crossindustry_margin_band
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, capex_intensity 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales = EV/EBITDA x EBITDA margin and EV/EBITDA varies far less across industries than margins do, firms with near-identical EBITDA margins and similar growth and reinvestment needs should have similar sales multiples whatever their SIC code. A tight margin band followed by fundamental ranking uses the whole cross-section instead of small industry groups.
      prediction: Pooled median |ln error| below the Bhojraj-Lee warranted multiple (0.674) and below the industry median (0.603) in at least 3 of 4 years.

  (4) Sales_L3_margin_size
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow 3-digit industry, business models and cost structures are similar, so what is left of the variation in sales multiples comes mostly from profitability, growth and scale. Ranking close industry peers on EBITDA margin first, then growth and size, should cut the large errors of plain industry medians on EV/Sales.
      prediction: Pooled median |ln error| below 0.57 and lower than the industry median (0.603) in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

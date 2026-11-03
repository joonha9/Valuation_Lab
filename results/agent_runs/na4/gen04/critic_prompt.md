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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 0.5, roic 1, rnd_intensity 1, capex_intensity 1, debt_to_assets 0.5, log_sales 0.5 | k=20, harmonic_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, rnd_intensity 0.5 | k=15, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebit_margin 2, asset_turnover 1, sales_growth_1y 1, gross_margin 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, ebitda_margin 0.7, capex_intensity 0.7, net_debt_to_ebitda 0.5, log_sales 0.5 | k=15, median, min_peers=5
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.3 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04, same industry_l2 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g02-06] EV/Sales | screen same industry_l3 | rank ebit_margin 1.5, asset_turnover 0.7, roic 0.7, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-02] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback []
  [g03-03] EV/EBITDA | rank log_sales 1, ebitda_margin 1, roic 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=20, trimmed_mean, min_peers=3
  [g03-04] EV/Sales | screen same industry_l3 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g03-06] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, asset_turnover 1, capex_intensity 0.5, sales_growth_1y 1, debt_to_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []

PROPOSALS
  (0) EBITDA_L2_growth_roic_twins
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and with return on invested capital, because high-ROIC firms need less reinvestment to fund growth. Within a broad 2-digit industry (shared cost of capital and cyclicality), the peers closest on growth, ROIC and size should share the target's warranted multiple more closely than an unranked industry median.
      prediction: Median |ln error| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years, and pooled median at or below 0.320.

  (1) EBITDA_L3_reinvestment_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA overstates distributable cash for capital-intensive firms, so the market pays less per dollar of EBITDA when capex absorbs much of it; growth offsets this. Matching narrow-industry peers on capex intensity, growth and size, and aggregating with the harmonic mean (which equal-weights earnings yields and dampens high-multiple outliers), should give a less biased multiple.
      prediction: Pooled median |ln error| below 0.333 and pooled mean below 0.500 (the regression baseline's 0.492 mean is the target to approach).

  (2) EBITDA_crossindustry_fundamental_twins
      recipe: EV/EBITDA | rank gross_margin 1, capex_intensity 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=3
      mechanism: Industry codes are noisy proxies for economics; firms with similar gross margin (pricing power), capex intensity (reinvestment need), growth and ROIC should share risk-adjusted growth prospects and therefore EV/EBITDA regardless of SIC label. Searching the whole cross-section for nearest fundamental twins tests whether fundamentals beat classification.
      prediction: Beats the warranted-multiple peers baseline (0.380) in all 4 years; whether it beats the L3 industry median (0.333) is the open question, expected in at most 2 of 4 years.

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most cross-sectional dispersion in sales multiples comes from margins. Within a 2-digit industry, picking the peers nearest in EBITDA margin (weighted most), gross margin and growth should remove the main source of error in the industry-median EV/Sales.
      prediction: Pooled median |ln error| below 0.50, beating the L3 industry median (0.603) in all 4 exploration years.

  (4) Sales_crossindustry_margin_growth_twins
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1 | k=12, median, min_peers=3
      mechanism: If EV/Sales is mostly margin times a growth-adjusted EBITDA multiple, firms anywhere in the market with matching EBITDA margin, gross margin, growth and ROIC should have similar sales multiples. Dropping the industry screen lets the ranking reach close margin twins that a narrow industry may lack.
      prediction: Pooled median |ln error| below 0.55 and below the industry-median baseline in at least 3 of 4 years, but worse than the within-industry margin-matched recipe.

  (5) Sales_L3_margin_band_trimmed
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.08 | rank ebitda_margin 2, roic 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.08] -> [band ebitda_margin±0.05] -> []
      mechanism: Narrow-industry peers share product markets and cost of capital, and a hard band on EBITDA margin makes sure every peer has a similar profit conversion of sales; ranking then on ROIC and growth captures value-creation differences. Trimmed means are robust to the occasional extreme sales multiple while using more information than the median.
      prediction: Pooled median |ln error| below 0.52 and pooled mean below 0.80, beating the regression baseline mean (0.837).

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

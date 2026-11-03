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
  (none)

PROPOSALS
  (0) ebitda_l2_growth_roic_size
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1.5, roic 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and with the return on new investment (high ROIC means less reinvestment per unit of growth), and larger firms trade at lower risk premia. Restricting to the 2-digit industry keeps shared business risk while ranking on growth, ROIC and size picks peers with the same fundamental value drivers inside a deeper pool than L3.
      prediction: Median |ln(V_est/V)| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years.

  (1) ebitda_l3_capex_growth
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, ebitda_margin 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores the depreciation and capital spending needed to sustain it, so capital-heavy firms convert less EBITDA into free cash flow and deserve lower EV/EBITDA. Within the 3-digit industry, matching on capex intensity and growth aligns the EBITDA-to-FCF conversion and growth outlook that drive the multiple.
      prediction: Overall exploration median error at or below 0.325 and beats the L3 industry median in at least 3 of 4 years.

  (2) ebitda_l4_size_harmonic
      recipe: EV/EBITDA | screen same industry_l4 | rank log_assets 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The narrowest industry definition captures the most similar products, customers and cyclicality, and the harmonic mean is the theoretically consistent average of price ratios (it averages the yield EBITDA/EV) and damps high-multiple outliers. Ranking on size and asset turnover within the narrow industry further aligns scale-driven risk and business model.
      prediction: Lower median error than the L3 industry median in at least 3 of 4 years, with a lower mean error than 0.513.

  (3) sales_l2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times the EBITDA margin, so most cross-sectional dispersion in EV/Sales comes from profitability differences. Within a 2-digit industry, ranking peers primarily on EBITDA margin and secondarily on gross margin and growth removes the dominant source of error that plain industry medians ignore.
      prediction: Median error below 0.50, beating the EV/Sales L3 industry median (0.603) in all 4 exploration years.

  (4) sales_crossindustry_margin_band
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: If EV/Sales is mostly profitability times a growth- and risk-driven EBITDA multiple, then firms with near-identical EBITDA margins, growth and size should share EV/Sales even across industries. A hard band on EBITDA margin forces profitability equality, and ranking on growth, ROIC and size handles the remaining multiple drivers.
      prediction: Beats the EV/Sales L3 industry median in at least 3 of 4 years; median error below 0.55.

  (5) sales_l3_margin_growth_harmonic
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within the 3-digit industry, firms with the same EBITDA margin and growth have the same cash-flow-per-dollar-of-sales and similar duration, so their EV/Sales should coincide; the harmonic mean limits the upward pull of a few richly priced peers that commonly inflate EV/Sales averages.
      prediction: Median error below 0.52 overall and lower than the EV/Sales industry median in every exploration year.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

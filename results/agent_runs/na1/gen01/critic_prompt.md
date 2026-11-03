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
  (0) EBITDA_L3_growth_return_neighbors
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within an industry, EV/EBITDA is roughly a function of expected growth and the return earned on reinvestment (value driver formula: multiple rises with growth when ROIC exceeds the cost of capital). Selecting same-industry peers that are closest in recent growth and ROIC should match the fundamentals that the industry median averages away.
      prediction: Median |ln error| below the 0.333 industry-median baseline in at least 3 of 4 exploration years, with pooled median around 0.31.

  (1) EBITDA_L2_risk_growth_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: EV/EBITDA reflects growth, profitability of growth and risk; leverage (net debt/EBITDA) and size proxy for risk and cost of capital. Using a broader 2-digit pool gives more candidates so the distance ranking can find close fundamental matches, and the harmonic mean limits the upward bias from high-multiple outliers.
      prediction: Beats the industry median (0.333) and the Bhojraj-Lee warranted multiple (0.357) on pooled median error, and has a lower mean error than 0.513.

  (2) EBITDA_L4_size_peers
      recipe: EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Firms in the same narrow 4-digit SIC line share product markets, cyclicality and technology, and close size matches share scale-related risk and liquidity premia. This is a refined version of the traditional analyst comp set, falling back to coarser industries only when the narrow set is too thin.
      prediction: Pooled median error within 0.02 of the industry-median baseline or better, beating it in at least 2 of 4 years.

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so differences in margin dominate cross-sectional EV/Sales dispersion. Matching peers on EBITDA and gross margin within the same broad industry, plus growth, should remove most of the margin-driven error that plagues industry-median EV/Sales.
      prediction: Pooled median error well below the 0.603 industry-median baseline (target under 0.50), beating it in all 4 exploration years.

  (4) Sales_crossindustry_fundamental_twins
      recipe: EV/Sales | rank ebitda_margin 2, sales_growth_1y 1, asset_turnover 0.5, gross_margin 0.5 | k=15, harmonic_mean, min_peers=3
      mechanism: Valuation per dollar of sales is determined by how much of that sale becomes cash flow (margin), how fast it grows and capital needs (asset turnover); these economics can be matched across industry boundaries. Dropping the industry screen enlarges the pool so very close margin-growth twins can be found, with the harmonic mean controlling outlier peers.
      prediction: Beats the industry median EV/Sales (0.603) and the Bhojraj-Lee warranted multiple (0.674) on pooled median error in at least 3 of 4 years.

  (5) Sales_L2_margin_band_growth
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, roic 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: A hard band on EBITDA margin guarantees that peers convert sales into cash flow at a similar rate, which is the first-order determinant of EV/Sales; within that band, matching growth and returns captures the remaining value drivers. Industry membership adds shared risk and cyclicality.
      prediction: Pooled median error below 0.55 and below the industry-median EV/Sales baseline in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

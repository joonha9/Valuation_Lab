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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1.5, roic 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, ebitda_margin 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | screen same industry_l4 | rank log_assets 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) evs_l2_margin_band_hybrid
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: EV/Sales is the EBITDA margin times an EBITDA multiple. The margin band equalizes the margin, and the shared 2-digit industry equalizes the multiple's industry-level risk, cyclicality and growth. Requiring both conditions together should remove the profitability error that plain industry medians make, and also the business-risk mismatch that a pure cross-industry margin match allows. When the industry-plus-band pool is too thin, the rule falls back to the cross-industry margin band, so coverage stays complete.
      prediction: Beats the industry median in 4 of 4 years and reaches an exploration median error below 0.43 (at or better than the pure cross-industry margin-band recipe).

  (1) evs_margin_growth_double_band
      recipe: EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank ebitda_margin 2, capex_intensity 1, roic 1, log_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.1]
      mechanism: With the margin held fixed, what is left of the EV/Sales multiple depends mainly on expected growth and on how much reinvestment that growth needs. Hard bands on both EBITDA margin and 1-year growth fix the two largest drivers. Ranking on capital intensity and ROIC then lines up the free-cash-flow conversion of each sales dollar.
      prediction: Beats the industry median in at least 3 of 4 years, with a mean absolute log error below 0.65.

  (2) evs_cost_structure_band
      recipe: EV/Sales | screen band gross_margin±0.08, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: Two firms can have the same EBITDA margin while earning it through different cost structures. A high-gross-margin, high-opex firm, such as software, has more pricing power and operating leverage than a low-gross-margin, lean-opex firm, such as distribution. Banding on both gross margin and EBITDA margin matches pricing power and cost structure across industries. Ranking on growth, capital intensity and size then handles duration and risk, and a trimmed mean limits the effect of extreme peers.
      prediction: Beats the industry median in 4 of 4 years, with an exploration median error below 0.50.

  (3) eve_l2_da_burden_match
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA leaves out depreciation and amortization, so it overstates the cash earnings of firms with heavy asset bases. The gap between EBITDA margin and EBIT margin measures this D&A burden, and capex intensity measures the reinvestment needed going forward. Within the 2-digit industry, matching both margins together with capex and growth picks peers that turn EBITDA into free cash flow at the same rate.
      prediction: Beats the industry median in at least 3 of 4 years, with an exploration median error below 0.330.

  (4) eve_l2_growth_band
      recipe: EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a constant-growth valuation, EV/EBITDA depends most on expected growth, just as EV/Sales depends most on margin. A hard band on 1-year sales growth within the 2-digit industry forces peers to have similar growth. Ranking on capex intensity and ROIC then lines up how much reinvestment that growth costs.
      prediction: Beats the industry median in at least 3 of 4 years, with a mean absolute log error below 0.50.

  (5) eve_cross_industry_fundamentals
      recipe: EV/EBITDA | screen band ebitda_margin±0.05, band sales_growth_1y±0.1 | rank capex_intensity 1.5, roic 1, log_sales 1 | k=15, median, min_peers=5 | fallback [band sales_growth_1y±0.1] -> []
      mechanism: If EV/EBITDA is set by growth, reinvestment needs and risk rather than by industry labels, then firms with similar growth and EBITDA margins should share a multiple across industries. The margin band also stands in for competitive position. Ranking on capex intensity, ROIC and size then matches free-cash-flow conversion and the risk premium. This recipe tests whether the cross-industry fundamental matching that works for EV/Sales also works for EV/EBITDA.
      prediction: Reaches an exploration median error at or below the industry median's 0.333 and beats it in at least 2 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

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

PROPOSALS
  (0) L2 industry, profitability-growth-leverage nearest EBITDA peers
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, net_debt_to_ebitda 0.75, log_sales 0.75 | k=8, median, min_peers=5 | fallback []
      mechanism: Within a broad industry, EV/EBITDA is driven by expected growth, the quality and durability of margins, and risk. Picking the nearest neighbours on growth, EBITDA margin, leverage and size inside the 2-digit sector holds technology and cyclicality roughly fixed while matching the value drivers that differ across firms in the same sector.
      prediction: Median error below the L3/L2 industry median (0.333) in at least 3 of 4 exploration years, with pooled median at most 0.32.

  (1) L3 industry, ROIC-growth-reinvestment peers, harmonic mean
      recipe: EV/EBITDA | screen same industry_l3 | rank roic 1, sales_growth_1y 1, capex_intensity 1 | k=10, harmonic_mean, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: In a value-driver model, the EBITDA multiple rises with growth and with return on capital, and falls with how much of EBITDA has to be reinvested (capex). Peers in the same 3-digit industry that are close on ROIC, growth and capex intensity should share the firm's sustainable cash-conversion economics. The harmonic mean of multiples limits the pull from outlier peers with very high multiples.
      prediction: Pooled median error at least 0.015 below the industry median baseline, and mean error below 0.50.

  (2) Cross-industry fundamental twins for EV/EBITDA
      recipe: EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 1, gross_margin 0.75, roic 1, capex_intensity 0.75, log_assets 0.5 | k=12, median, min_peers=3
      mechanism: If multiples reflect fundamentals rather than industry labels, firms with matching growth, margins, capital intensity, returns and size should trade at similar EBITDA multiples whatever their SIC code. This avoids errors from SIC codes that are wrong or too coarse, and draws on a larger pool to find close matches.
      prediction: Beats the Bhojraj-Lee warranted-multiple peers (0.380) in all 4 years, and comes within 0.02 of the industry median on pooled median error.

  (3) L2 industry, margin-matched EV/Sales peers
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in margin. Matching peers closely on EBITDA margin (and gross margin), plus growth, inside the same sector should remove most of the error from using a plain industry median.
      prediction: Pooled median error below 0.52 (versus the 0.603 industry median), and beats the industry median in all 4 years.

  (4) Cross-industry margin-growth twins for EV/Sales, harmonic mean
      recipe: EV/Sales | rank ebitda_margin 3, net_margin 1, gross_margin 1, sales_growth_1y 1 | k=15, harmonic_mean, min_peers=3
      mechanism: Revenue multiples carry over across industries once you hold profitability per dollar of sales and growth constant. Ranking the whole cross-section on EBITDA margin, net margin, gross margin and growth finds firms whose sales turn into value at the same rate. The harmonic mean guards against peers with very large EV/Sales.
      prediction: Beats the Bhojraj-Lee warranted multiple (0.674) in at least 3 of 4 years, with pooled median error below 0.58.

  (5) L3 industry, margin-turnover-size EV/Sales peers
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, asset_turnover 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: In a narrow industry, sales multiples differ mainly with operating margin and with how much capital is needed per dollar of sales (asset turnover), while size stands in for risk and market position. Matching on these inside the 3-digit SIC group keeps the same business model and accounts for the firm's place on the margin-turnover trade-off.
      prediction: Pooled median error at least 0.06 below the industry median baseline (0.603), and mean error below 0.85.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

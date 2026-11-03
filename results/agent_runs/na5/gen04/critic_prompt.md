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

PROPOSALS
  (0) EBITDA_L3_value_drivers
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, roic 1.5, log_sales 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a Gordon-style model, EV/EBITDA rises with expected growth and with return on capital (less reinvestment needed per unit of growth) and falls with risk. Within the same 3-digit industry, peers matched on growth, ROIC, size and leverage should share the same discount rate and reinvestment economics, so their multiple transfers best.
      prediction: Median |ln error| below the L3 industry median baseline (0.333) pooled over FY2016-2019 and beats it in at least 3 of 4 years.

  (1) EBITDA_L2_cash_conversion
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: EBITDA ignores capital spending, so firms that must reinvest heavily convert less EBITDA into free cash flow and deserve lower multiples. Matching on capex intensity, ROIC and growth within a broad 2-digit industry captures how much of EBITDA is truly distributable, and the harmonic mean is the unbiased average of a price-scaled ratio.
      prediction: Beats the L3 industry median baseline on pooled median error and has lower mean error than 0.513.

  (2) EBITDA_fundamental_twins
      recipe: EV/EBITDA | rank sales_growth_1y 1.5, roic 1.5, capex_intensity 1, ebitda_margin 0.5, debt_to_assets 0.5, log_sales 1 | k=15, median, min_peers=3
      mechanism: Valuation theory says multiples are a function of growth, profitability, reinvestment and risk, not SIC labels. Ranking all firms on these fundamentals finds economic twins even across industries, which helps targets in thin or heterogeneous SIC codes.
      prediction: Comes within 0.02 of the L3 industry median baseline on pooled median error and beats the Bhojraj-Lee warranted-multiple peers baseline (0.380) in all 4 years.

  (3) Sales_crossindustry_profitability
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 0.5, log_sales 0.5 | k=12, median, min_peers=3
      mechanism: A dollar of sales is worth what it earns and how fast it grows, regardless of SIC code. Ranking the whole cross-section on EBITDA margin, gross margin, growth and ROIC finds firms whose sales carry the same value per dollar, which especially helps high-margin targets in low-margin industries.
      prediction: Beats the L3 industry median EV/Sales baseline on pooled median error by at least 0.05 and beats it in at least 3 of 4 years.

  (4) Sales_L3_margin_band
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 1, ebitda_margin 1 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]
      mechanism: Same-industry firms share demand and cost structures, but a sales multiple is only comparable when margins are similar. A hard band of plus or minus 5 points of EBITDA margin inside the 3-digit industry enforces margin comparability, then ranking on growth and size picks firms with similar scale and growth prospects.
      prediction: Pooled median error below the L3 industry median baseline (0.603) and below the warranted-multiple regression (0.674) in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

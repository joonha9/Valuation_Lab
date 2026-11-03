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
  [g03-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 1, net_debt_to_ebitda 0.5 | k=10, median, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank log_sales 0.5, roic 1, sales_growth_1y 1 | k=6, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | rank capex_intensity 1, ebitda_margin 1, sales_growth_1y 1, roic 1, gross_margin 0.5 | k=15, median, min_peers=3
  [g03-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g03-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g03-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
  [g04-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, roic 1, sales_growth_1y 0.75 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g04-03] EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 0.75, roic 1, sales_growth_1y 1, log_assets 0.5 | k=12, harmonic_mean, min_peers=5 | fallback []
  [g04-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 0.75, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
  [g04-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 1.5, sales_growth_1y 1, capex_intensity 0.5, gross_margin 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g04-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, roic 0.75, sales_growth_1y 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) L2 growth-reinvestment EBITDA peers
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, log_sales 0.75, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: Within a broad industry, EV/EBITDA differences are driven mainly by expected growth, by how much of EBITDA must be reinvested (capex intensity), and by scale-related risk. Picking same-sector peers that match on growth, capex intensity and size should line up those drivers better than taking the whole industry median.
      prediction: Median |ln error| below the L3/L2 industry-median baseline (0.333) in at least 3 of 4 exploration years.

  (1) L3 ROIC-growth harmonic peers
      recipe: EV/EBITDA | screen same industry_l3 | rank roic 1, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Value-driver theory says that at a given growth rate, firms with higher returns on invested capital convert growth into value more efficiently and so earn higher EBITDA multiples. Matching close industry peers on ROIC and growth, then using the harmonic mean (which weights cheap peers properly for a price-scaled ratio), should give an unbiased warranted multiple.
      prediction: Beats the industry-median baseline on both median and mean error in pooled FY2016-2019.

  (2) Cross-industry fundamental twins EBITDA
      recipe: EV/EBITDA | rank ebitda_margin 1, sales_growth_1y 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_sales 0.75, asset_turnover 0.5 | k=15, median, min_peers=5
      mechanism: SIC codes are noisy groupings, so firms with similar margins, growth, capital intensity, leverage and size may share risk and growth profiles across industry lines. Ranking all firms on these fundamentals finds economic twins whose EBITDA multiples reflect similar expected cash-flow paths.
      prediction: Median error within 0.02 of the industry-median baseline or better, and lower mean error than the Bhojraj-Lee warranted-multiple peers (0.523).

  (3) L2 size-banded leverage-aware EBITDA
      recipe: EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank sales_growth_1y 1, net_debt_to_ebitda 0.75, roic 0.75 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Firms of very different size have different risk and access to capital, and highly levered firms trade at different EV/EBITDA because of financial distress and tax effects. A size band within the sector, then ranking on growth, leverage and returns, should isolate peers with similar discount rates.
      prediction: Beats the industry-median baseline in at least 3 of 4 years, with the largest gains for small firms.

  (4) Cross-industry margin-growth sales twins
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5
      mechanism: A firm's revenue multiple is set by the margins it can earn on each dollar of sales and how fast those sales grow, whatever its SIC code. Ranking the whole cross-section on EBITDA margin, gross margin and growth, and using the harmonic mean to limit the pull of high-multiple outliers, should give a well-calibrated warranted EV/Sales.
      prediction: Beats both the EV/Sales industry median (0.603) and the Bhojraj-Lee regression (0.674) on pooled median error.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

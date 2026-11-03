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

PROPOSALS
  (0) EBITDA_L2_fundamental_twins
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, ebitda_margin 1, net_debt_to_ebitda 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA is driven by expected growth, reinvestment efficiency (ROIC) and risk; within a broad industry, firms that also match on growth, ROIC and leverage should share discount rates and growth expectations more closely than the full industry. Ranking within 2-digit SIC keeps sector-level cost of capital while letting fundamentals pick the closest economic twins.
      prediction: Median |ln error| below the L3 industry median baseline (0.333) in at least 3 of 4 exploration years.

  (1) EBITDA_L3_size_capex_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 1, capex_intensity 2, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow 3-digit industry, firms of similar size and capital intensity face similar maintenance-capex drags on EBITDA-to-free-cash-flow conversion, and size proxies for risk and liquidity. The harmonic mean is the theoretically correct average for price multiples and dampens high-multiple outliers.
      prediction: Median |ln error| at or below 0.33 overall and beats the L3 industry median in at least 3 of 4 years.

  (2) EBITDA_cross_industry_value_drivers
      recipe: EV/EBITDA | rank sales_growth_1y 2, roic 2, capex_intensity 1, net_debt_to_ebitda 1, ebitda_margin 1 | k=20, trimmed_mean, min_peers=3
      mechanism: Under a DCF, EV/EBITDA is a function of growth, ROIC (reinvestment needs), capex intensity and leverage-related risk regardless of SIC code; matching directly on these drivers across all industries finds firms with the same cash-flow economics. A larger k and trimmed mean reduce noise from imperfect matches.
      prediction: Median |ln error| below the Bhojraj-Lee warranted-multiple peers baseline (0.380) in all 4 years.

  (3) Sales_L2_margin_match
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant driver of a sales multiple is profitability; within a broad industry, peers with similar EBITDA and gross margins should convert a dollar of sales into similar value. Growth is a secondary driver.
      prediction: Median |ln error| below the L3 industry median EV/Sales baseline (0.603) in all 4 years, by at least 0.05 on average.

  (4) Sales_cross_industry_profitability
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=3
      mechanism: Value per dollar of sales is mechanically tied to margin and growth across all industries; matching on EBITDA margin, gross margin, growth and ROIC ignores SIC boundaries that group high- and low-margin businesses together. This should especially help diversified or misclassified firms.
      prediction: Median |ln error| below 0.60 overall and beats the Bhojraj-Lee warranted-multiple EV/Sales baseline (0.674) in at least 3 of 4 years.

  (5) Sales_margin_band_L2_harmonic
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 2, log_sales 1, gross_margin 1 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
      mechanism: A hard EBITDA-margin band guarantees peers have nearly the same EV/Sales-to-EV/EBITDA conversion factor, while sector membership controls for risk; ranking on growth and size then picks firms with similar expected expansion. Harmonic mean limits the influence of very high sales multiples.
      prediction: Beats the L3 industry median EV/Sales baseline in at least 3 of 4 years, with median |ln error| below 0.58 overall.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

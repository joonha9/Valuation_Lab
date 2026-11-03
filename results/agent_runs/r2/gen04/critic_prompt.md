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
  [g02-01] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g02-02] EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank ebitda_margin 2, capex_intensity 1, roic 1, log_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.1]
  [g02-03] EV/Sales | screen band gross_margin±0.08, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g02-04] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-06] EV/EBITDA | screen band ebitda_margin±0.05, band sales_growth_1y±0.1 | rank capex_intensity 1.5, roic 1, log_sales 1 | k=15, median, min_peers=5 | fallback [band sales_growth_1y±0.1] -> []
  [g03-01] EV/Sales | screen same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-02] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-03] EV/Sales | screen band ebitda_margin±0.05, band capex_intensity±0.03 | rank sales_growth_1y 1.5, gross_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-04] EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5
  [g03-05] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, net_debt_to_ebitda 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5
  [g03-06] EV/EBITDA | screen same industry_l2, band capex_intensity±0.04 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []

PROPOSALS
  (0) g04-01 R&D-inclusive reinvestment peers (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, rnd_intensity 1, gross_margin 1, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
      mechanism: R&D is expensed, so it lowers reported EBITDA even though it is an investment in future earnings, much like capex. R&D-heavy firms therefore show depressed EBITDA relative to their economic earnings and trade at higher EV/EBITDA. Within the 2-digit industry, matching on R&D intensity together with capex intensity, gross margin, EBIT margin and growth aligns total reinvestment (tangible plus intangible), pricing power and growth.
      prediction: Median error below 0.315 and beats the industry median in all 4 exploration years, with the largest gains in R&D-heavy industries (SIC 28, 35, 36, 38, 73); coverage of at least 90%.

  (1) g04-02 Moat, reinvestment, distress and ROIC with harmonic mean (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, net_debt_to_ebitda 1, roic 0.75, sales_growth_1y 1, log_assets 0.5 | k=15, harmonic_mean, min_peers=5 | fallback []
      mechanism: EV/EBITDA rises with earnings durability (gross margin), falls with the reinvestment burden (capex intensity) and with distress costs (net debt to EBITDA), and rises with ROIC because high-return firms need less reinvestment per unit of growth. Matching all four drivers plus growth inside the 2-digit industry gives a wider peer set (k=15). Aggregating with the harmonic mean averages the earnings yields EBITDA/EV, which are roughly linear in these drivers, so a few richly priced peers do not pull the estimate up.
      prediction: Beats the industry median in at least 3 of 4 years, with a mean error below 0.480 (lower than the median-aggregated archive recipes) because the harmonic mean controls overvaluation errors.

  (2) g04-03 Transitory-earnings matching (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, net_margin 1, roe 0.5, sales_growth_1y 1, log_assets 0.5 | k=12, trimmed_mean, min_peers=5 | fallback []
      mechanism: When EBITDA is temporarily depressed, EV/EBITDA is temporarily high, because the market values normalized earnings rather than the current year's. Firms whose net margin is far below their EBITDA margin, with weak 1-year growth and low ROE, are more likely to be at a cyclical trough or carrying heavy D&A, interest or one-off charges. Within the 2-digit industry, matching on EBITDA margin, net margin, ROE, growth and capex intensity picks peers in the same phase of earnings, and a trimmed mean removes trough-multiple outliers.
      prediction: Beats the industry median in at least 3 of 4 years, and median error below 0.325.

  (3) g04-04 EBIT-margin band within industry (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebit_margin±0.04 | rank ebit_margin 2, ebitda_margin 1, sales_growth_1y 1, gross_margin 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.04] -> [band ebit_margin±0.08] -> [band ebitda_margin±0.1]
      mechanism: Sales are worth what they convert into sustainable cash flow. EBIT margin, which subtracts D&A as a proxy for maintenance capex, is closer to that than EBITDA margin, because it does not overstate the cash margin of asset-heavy firms. A hard EBIT-margin band inside the 2-digit industry matches after-reinvestment profitability and business risk together. Ranking on EBIT and EBITDA margin (which also captures the D&A gap), growth, gross margin and size then sorts out the remaining differences.
      prediction: Median error below 0.380 and beats the industry median in all 4 years.

  (4) g04-05 Value-creating growth: ROIC x growth (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 1.5, sales_growth_1y 1.5, ebitda_margin 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: Once the margin is fixed, the EBITDA multiple embedded in EV/Sales depends on growth, but growth only adds value when ROIC exceeds the cost of capital. Growth at low ROIC can even destroy value. Inside the 2-digit industry plus an EBITDA-margin band, ranking with equal heavy weights on ROIC and 1-year growth picks peers whose growth creates value at the same rate.
      prediction: Beats the industry median in all 4 years, and median error below 0.385.

  (5) g04-06 Hierarchical cost-structure match (EV/Sales)
      recipe: EV/Sales | screen same industry_l3, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, ebitda_margin 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05] -> [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: The best peers share both the narrowest industry (product market, cyclicality) and the same cost structure (gross margin and EBITDA margin). The rule first requires the 3-digit industry with both margin bands. If that is too thin, it widens to the 2-digit industry with both bands, then to the cross-industry double band, then to a wide EBITDA band. This way each firm gets the most specific peer group that matches both pricing power and profitability. Ranking on growth, capex intensity, EBITDA margin and size handles the remaining duration and reinvestment differences.
      prediction: Median error below 0.370, beats the industry median in all 4 years, and coverage of at least 93%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

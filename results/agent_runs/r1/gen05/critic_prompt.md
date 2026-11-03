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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-03] EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
  [g01-04] EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.75, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2, band log_sales±2 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | screen same industry_l3, band net_debt_to_ebitda±2 | rank ebitda_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±2] -> [same industry_l2]
  [g02-04] EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_sales 1, capex_intensity 1, gross_margin 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.08]
  [g02-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=10, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g02-06] EV/Sales | screen same industry_l4 | rank ebitda_margin 2, ebit_margin 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band log_sales±1.5] -> [same industry_l3] -> [same industry_l2]
  [g03-02] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
  [g03-03] EV/EBITDA | screen band sales_growth_1y±0.1, band net_debt_to_ebitda±1.5 | rank roic 1, ebit_margin 1, ebitda_margin 1, capex_intensity 0.5, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.2] -> []
  [g03-04] EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.04 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g03-05] EV/Sales | screen same industry_l2, band ebit_margin±0.03 | rank ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06]
  [g03-06] EV/Sales | screen band ebitda_margin±0.03, band log_sales±1.5 | rank sales_growth_1y 1, gross_margin 1, debt_to_assets 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
  [g04-01] EV/Sales | screen band ebitda_margin±0.03, band rnd_intensity±0.03 | rank sales_growth_1y 1, gross_margin 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
  [g04-02] EV/Sales | screen band ebitda_margin±0.03, band asset_turnover±0.25 | rank sales_growth_1y 1, roic 1, debt_to_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
  [g04-03] EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.06 | rank sales_growth_1y 1, log_sales 1, capex_intensity 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03, band gross_margin±0.12] -> [band ebitda_margin±0.05]
  [g04-04] EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2]
  [g04-05] EV/EBITDA | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.05] -> [same industry_l2]
  [g04-06] EV/EBITDA | screen same industry_l2, band gross_margin±0.08 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band gross_margin±0.15] -> [same industry_l2]

PROPOSALS
  (0) ebitda_tax_burden_l3
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, ebit_margin 1, net_margin 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV is a claim on unlevered after-tax cash flow, so at equal EBITDA, growth and reinvestment a firm that pays a higher effective tax rate keeps less of each EBITDA dollar and should trade at a lower EV/EBITDA. Given EBIT margin and balance-sheet leverage (which pins down interest), the remaining gap between EBIT margin and net margin mostly reflects the tax burden and recurring non-operating items, so ranking 3-digit industry peers jointly on growth, EBIT margin, net margin and debt-to-assets matches peers that convert EBITDA into after-tax unlevered cash at the same rate.
      prediction: Beats the L3/L2 industry median EV/EBITDA in at least 3 of 4 exploration years, with a pooled median |ln error| at or below 0.328 and coverage above 97%.

  (1) ebitda_asset_turnover_business_model
      recipe: EV/EBITDA | screen same industry_l2, band asset_turnover±0.3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band asset_turnover±0.6] -> [same industry_l2]
      mechanism: Asset turnover is a stock measure of the business model (asset-light distributors and services versus asset-heavy manufacturers and utilities can share a 2-digit SIC code), and it determines how much capital must be added per dollar of future sales, i.e. how much of EBITDA growth is eaten by reinvestment. Unlike annual capex intensity, which is lumpy, turnover is stable year to year, so a hard turnover band inside the 2-digit industry keeps peers with the same capital needs per unit of growth, and ranking on growth, ROIC and net leverage matches the remaining Gordon-model drivers.
      prediction: Beats the industry median EV/EBITDA in at least 3 of 4 years, with pooled median |ln error| below 0.330 and coverage of at least 97%.

  (2) ebitda_expensed_investment_gap
      recipe: EV/EBITDA | screen same industry_l3 | rank gross_margin 1, ebitda_margin 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: The gap between gross margin and EBITDA margin is the operating expense base (SG&A, marketing, R&D) that is expensed even though much of it builds customer and brand capital, so firms with a large gap have depressed current EBITDA relative to their economic earnings and high operating leverage, and trade at higher EV/EBITDA. Matching 3-digit industry peers on both margins at once (rather than gross margin alone) equalizes this expensed-investment share and the scope for margin expansion, while growth and net leverage match duration and financial risk.
      prediction: Beats the industry median EV/EBITDA in at least 3 of 4 years with pooled median |ln error| at or below 0.326.

  (3) sales_operating_leverage_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.08 | rank sales_growth_1y 1, asset_turnover 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03, band gross_margin±0.15] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: EV/Sales capitalizes not only today's cash margin but the margin the firm can reach as it scales, and that potential depends on cost structure: a firm with a high gross margin but a modest EBITDA margin carries a large fixed, expensed operating base that will be leveraged as sales grow. Hard bands on both gross margin and EBITDA margin put peers at the same current cash margin and the same operating leverage regardless of SIC code, and ranking on growth, asset turnover and size then matches how fast that leverage is realized, the capital behind each sales dollar, and the risk premium.
      prediction: Beats the industry median EV/Sales in all 4 years with pooled median |ln error| at or below 0.385 and coverage above 90%.

  (4) sales_value_creation_regime
      recipe: EV/Sales | screen band ebitda_margin±0.03, band roic±0.06 | rank sales_growth_1y 1, log_sales 0.5, capex_intensity 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03, band roic±0.12] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: Growth raises value only when the return on new capital exceeds the cost of capital; for a firm with ROIC below WACC faster growth destroys value, so the sign and size of the growth effect on EV/Sales flips across ROIC regimes. Hard bands on EBITDA margin and on ROIC place peers in the same cash-margin and value-creation regime first, so that ranking on sales growth compares growth that is worth the same per dollar, with size added for the risk premium.
      prediction: Beats the industry median EV/Sales in all 4 years with pooled median |ln error| at or below 0.390 and coverage above 90%.

  (5) sales_leverage_distress_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band debt_to_assets±0.1 | rank sales_growth_1y 1, gross_margin 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03, band debt_to_assets±0.2] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: Enterprise value adds debt at roughly book value, but for highly levered firms equity behaves like an option and expected distress costs reduce the true value of the operating assets, so at the same cash margin high-leverage firms show a systematically different EV/Sales than unlevered ones. A hard debt-to-assets band next to the EBITDA-margin band keeps peers in the same capital-structure and distress regime, and ranking on growth, gross margin and size matches duration, pricing power and the size premium.
      prediction: Beats the industry median EV/Sales in all 4 years with pooled median |ln error| at or below 0.390 and coverage above 90%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

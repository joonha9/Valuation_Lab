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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-03] EV/EBITDA | rank roic 1, sales_growth_1y 1, capex_intensity 1, rnd_intensity 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=20, trimmed_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.03 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band ebitda_margin±0.06]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, rnd_intensity 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]
  [g02-01] EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, roic 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=6 | fallback []
  [g02-02] EV/EBITDA | screen band sales_growth_1y±0.08 | rank roic 1, capex_intensity 1, rnd_intensity 1, log_assets 0.5, ebitda_margin 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.16] -> []
  [g02-03] EV/EBITDA | screen same industry_l3 | rank ebitda_margin 1.5, net_margin 1, roe 0.5, sales_growth_1y 0.5 | k=7, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-04] EV/Sales | screen band ebitda_margin±0.04 | rank rnd_intensity 1.5, sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.08] -> []
  [g02-05] EV/Sales | rank ebitda_margin 4, ebit_margin 2, sales_growth_1y 1, capex_intensity 1, roic 1 | k=10, median, min_peers=3
  [g02-06] EV/Sales | screen band gross_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5, asset_turnover 0.5 | k=10, median, min_peers=6 | fallback [band gross_margin±0.1] -> []
  [g03-01] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank ebitda_margin 1, ebit_margin 1, roic 1, capex_intensity 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-02] EV/EBITDA | screen band net_debt_to_ebitda±1 | rank roic 1, sales_growth_1y 1, ebit_margin 1, log_assets 1, rnd_intensity 0.5 | k=15, median, min_peers=8 | fallback [band net_debt_to_ebitda±2] -> []
  [g03-03] EV/EBITDA | screen same industry_l3 | rank gross_margin 1, asset_turnover 1, ebit_margin 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-04] EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, roic 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g03-05] EV/Sales | screen band ebit_margin±0.03 | rank ebitda_margin 1, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=12, trimmed_mean, min_peers=6 | fallback [band ebit_margin±0.06] -> []
  [g03-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, debt_to_assets 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []

PROPOSALS
  (0) sector_rnd_matched_ebitda
      recipe: EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank ebitda_margin 1, ebit_margin 1, sales_growth_1y 1, roic 1 | k=12, trimmed_mean, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: R&D is expensed, so R&D-heavy firms report EBITDA that understates their economic (pre-investment) earnings and therefore carry systematically higher EV/EBITDA than low-R&D firms in the same sector. Hard-matching R&D intensity inside the 2-digit sector removes this accounting distortion while keeping shared macro risk, and ranking on EBITDA and EBIT margins (which jointly pin down D&A intensity), growth and ROIC matches the remaining value drivers.
      prediction: Beats the industry median (L3, fallback L2) in at least 3 of 4 years with median error at or below 0.325, and improves most for firms with R&D intensity above 5%.

  (1) size_band_driver_ebitda
      recipe: EV/EBITDA | screen band log_assets±0.75 | rank roic 1, sales_growth_1y 1, ebit_margin 1, capex_intensity 1, net_debt_to_ebitda 0.5 | k=15, median, min_peers=8 | fallback [band log_assets±1.5] -> []
      mechanism: Firm size is a robust accounting proxy for cost of capital: small firms face higher discount rates, illiquidity and less durable cash flows, so they trade at lower EV/EBITDA than large firms with identical operating drivers. Banding on total assets puts peers in the same size/discount-rate class across industries, and ranking on ROIC, growth, EBIT margin, capex intensity and leverage matches the numerator drivers of the capitalized cash-flow multiple.
      prediction: Beats the industry median in at least 3 of 4 years and has median error below 0.335, with the gain concentrated in the smallest size quintile.

  (2) yield_averaging_growth_peers_ebitda
      recipe: EV/EBITDA | rank sales_growth_1y 2, ebitda_margin 1, ebit_margin 1, roic 1, log_sales 0.5 | k=25, harmonic_mean, min_peers=3
      mechanism: In a growing-perpetuity model the EBITDA yield (EBITDA/EV) is approximately linear in (WACC - g)/(1 - reinvestment rate), whereas the multiple is convex in growth, so averaging peers' yields (the harmonic mean of multiples) is the less biased aggregator when peers differ slightly in growth. Selecting a broad set of cross-industry neighbours weighted most heavily on growth, and then on EBITDA/EBIT margins and ROIC (which pin down reinvestment needs), gives a large, driver-matched sample on which this yield averaging is effective.
      prediction: Beats the industry median in at least 3 of 4 years with a lower mean error than g01-03 (below 0.469), because harmonic averaging suppresses peers with temporarily depressed EBITDA.

  (3) roic_turnover_decomposition_sales
      recipe: EV/Sales | screen band roic±0.04 | rank asset_turnover 2, sales_growth_1y 1, ebit_margin 1 | k=12, median, min_peers=6 | fallback [band roic±0.08] -> []
      mechanism: EV/Sales factors exactly into EV/Invested capital times Invested capital/Sales; the first factor is set by ROIC relative to the cost of capital and by growth, the second by capital intensity (inverse asset turnover). Banding on ROIC fixes the value-creation spread across industries, and ranking on asset turnover, growth and EBIT margin matches the capital-intensity and growth terms, so peers share both factors of the sales multiple.
      prediction: Beats the EV/Sales industry median in all 4 years with median error below 0.45.

  (4) gross_and_ebitda_margin_box_sales
      recipe: EV/Sales | screen band gross_margin±0.06, band ebitda_margin±0.04 | rank sales_growth_1y 1, rnd_intensity 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: The gap between gross margin and EBITDA margin is operating-expense intensity (SG&A plus R&D), which separates firms that are scaling toward a high margin ceiling (high gross, low EBITDA margin, valued on future margins) from mature firms already at their ceiling. A joint band on gross and EBITDA margin matches both the business-model ceiling and the current cash conversion of sales, and ranking on growth, R&D and capex intensity matches the speed and cost of moving toward that ceiling.
      prediction: Beats the industry median in all 4 years and achieves median error at or below 0.38, improving on g02-06 by matching current margin directly.

  (5) size_adjusted_margin_sales
      recipe: EV/Sales | screen band ebitda_margin±0.03, band log_sales±1 | rank sales_growth_1y 1, gross_margin 1, rnd_intensity 1 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: A dollar of EBITDA margin is capitalized at a rate that depends on its durability and the firm's discount rate, and large firms have more stable margins, better access to capital and lower required returns, so they trade at higher EV/Sales than small firms with the same margin. Jointly banding on EBITDA margin and sales size makes peers share both the cash margin and its capitalization rate, while ranking on growth, gross margin and R&D intensity matches pricing power and expensed intangible investment.
      prediction: Beats the industry median in all 4 years with median error below 0.40, and lowers error relative to g01-05 mainly for firms in the bottom size quintile.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

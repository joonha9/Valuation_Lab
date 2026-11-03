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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 0.5, roic 1, rnd_intensity 1, capex_intensity 1, debt_to_assets 0.5, log_sales 0.5 | k=20, harmonic_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, rnd_intensity 0.5 | k=15, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebit_margin 2, asset_turnover 1, sales_growth_1y 1, gross_margin 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []

PROPOSALS
  (0) EBITDA_L2_growth_profit_nearest
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA is, in a DCF sense, driven by expected growth, reinvestment needs (via ROIC) and risk. Within a broad 2-digit industry (shared risk and cyclicality), the peers closest in growth, ROIC and size should share the firm's capitalization rate on EBITDA better than the full industry median.
      prediction: Median |ln error| below the L3/L2 industry median baseline (0.333) in at least 3 of 4 exploration years.

  (1) EBITDA_L3_leverage_capex_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Capital intensity and leverage determine how much of EBITDA converts to free cash flow and how risky the equity cushion is, so firms with similar capex intensity and net debt/EBITDA inside a narrow industry should carry similar EBITDA multiples. The harmonic mean dampens the influence of peers with temporarily depressed EBITDA and inflated multiples.
      prediction: Lower mean |ln error| than the industry median baseline (0.513) and median error at or below 0.33 overall.

  (2) EBITDA_crossindustry_fundamentals
      recipe: EV/EBITDA | rank sales_growth_1y 1, roic 1, ebitda_margin 0.7, capex_intensity 0.7, net_debt_to_ebitda 0.5, log_sales 0.5 | k=15, median, min_peers=5
      mechanism: Valuation theory says multiples depend on growth, return on capital and risk, not on SIC codes per se; matching on these fundamentals across the whole market can find better economic twins than coarse industry labels, especially for firms in thin or heterogeneous SIC groups.
      prediction: Beats the Bhojraj-Lee warranted-multiple peers baseline (median 0.380) in all 4 years, and comes within 0.03 of the industry median baseline.

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.3 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant source of EV/Sales dispersion within an industry is profitability. Ranking 2-digit industry peers primarily on EBITDA margin (and secondarily growth) should remove most of the margin-driven error that plagues an industry median.
      prediction: Median |ln error| at least 0.08 below the EV/Sales industry median baseline (0.603) in every exploration year.

  (4) Sales_margin_band_harmonic
      recipe: EV/Sales | screen band ebitda_margin±0.04, same industry_l2 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
      mechanism: A hard band on EBITDA margin guarantees peers have comparable profitability per dollar of sales, the main determinant of EV/Sales; within that band, firms with similar growth and capital intensity should command similar revenue multiples regardless of exact industry. Harmonic averaging limits upward bias from high-multiple outliers.
      prediction: Beats the EV/Sales industry median baseline (0.603) and the Bhojraj-Lee regression (0.674) in at least 3 of 4 years.

  (5) Sales_L3_profit_return_trimmed
      recipe: EV/Sales | screen same industry_l3 | rank ebit_margin 1.5, asset_turnover 0.7, roic 0.7, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow 3-digit industry, firms with similar EBIT margins, asset turnover and ROIC share both the cash-generating power per dollar of sales and the reinvestment burden of growth, so their revenue multiples should converge. A trimmed mean balances the efficiency of the mean with robustness to outliers.
      prediction: Median |ln error| below 0.55 overall and below the industry median baseline in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

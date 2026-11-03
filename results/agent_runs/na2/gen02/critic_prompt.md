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

PROPOSALS
  (0) EBITDA_L2_growth_roic_leverage
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: In a DCF view, EV/EBITDA is driven by expected growth, return on invested capital (which sets how much EBITDA must be reinvested to grow), and risk. Within a broad 2-digit industry that shares macro exposure, the nearest neighbours on growth, ROIC, leverage and size should share the target's justified multiple more closely than an unconditioned industry median.
      prediction: Median |ln(V_est/V)| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years, and pooled median below 0.325.

  (1) EBITDA_L3_capex_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores capital expenditure, so two firms with the same EBITDA but different capex needs generate different free cash flow and deserve different EV/EBITDA multiples. Matching on capex intensity and growth within a 3-digit industry, and averaging with the harmonic mean (which is the unbiased averaging of price ratios), should correct the main bias of plain industry medians.
      prediction: Pooled median error below 0.333 and mean error below 0.50 (beating the L3 industry-median mean of 0.513).

  (2) EBITDA_fundamental_neighbours_crossindustry
      recipe: EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, gross_margin 0.75, debt_to_assets 0.5, log_sales 0.5 | k=15, median, min_peers=3
      mechanism: Valuation multiples are ultimately functions of growth, profitability, reinvestment needs and risk rather than SIC labels, and SIC codes misclassify many diversified or new-economy firms. Nearest neighbours on these fundamentals across the whole cross-section, with a larger k to stabilise the estimate, should capture the multiple's determinants without industry-code noise.
      prediction: Pooled median error within 0.02 of the L3 industry-median baseline (0.313-0.353) and lower mean error than the Bhojraj-Lee warranted multiple (0.492).

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant source of cross-firm dispersion in sales multiples is profitability. Within a 2-digit industry, peers matched primarily on EBITDA margin and secondarily on gross margin and growth should share the target's sales multiple far more closely than an industry median that mixes high- and low-margin firms.
      prediction: Beats the EV/Sales L3 industry-median baseline (0.603) in all 4 exploration years, with pooled median below 0.52.

  (4) Sales_margin_band_crossindustry
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, roic 0.75, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> [band ebitda_margin±0.15] -> []
      mechanism: A hard band on EBITDA margin guarantees that peers convert sales into cash flow at a similar rate, which is the economic bridge from sales to value; ranking within that band on growth, gross margin and ROIC then matches the remaining multiple drivers regardless of SIC label. Fallback to wider bands keeps coverage for extreme-margin firms.
      prediction: Pooled median error below 0.55 and beats the EV/Sales industry-median baseline in at least 3 of 4 years.

  (5) Sales_L3_margin_harmonic
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 3, sales_growth_1y 1, asset_turnover 0.5, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit industries share business models, cost structures and growth opportunities, and within them EBITDA margin explains most remaining variation in EV/Sales. A small, margin-matched peer set combined with the harmonic mean (robust to a few very richly valued peers) should give tight sales-multiple estimates.
      prediction: Pooled median error below 0.55 and mean error below 0.85, beating the L3 industry median on both statistics.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

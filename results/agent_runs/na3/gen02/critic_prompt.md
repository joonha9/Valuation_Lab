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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_assets 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank gross_margin 1, ebitda_margin 1, capex_intensity 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, roic 1, log_sales 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) L3 growth-profitability twins, harmonic EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, firms share risk and business model, but EV/EBITDA still varies with expected growth and with how efficiently capital earns returns (value = EBITDA x f(growth, ROIC)). Picking the industry peers closest in sales growth, ROIC and size isolates firms whose cash-flow outlook matches the target, and the harmonic mean limits the pull of extreme high multiples.
      prediction: Median |ln error| below the L3/L2 industry-median baseline (0.333) in at least 3 of 4 exploration years, with pooled median at or below 0.32.

  (1) L2 capex-adjusted EV/EBITDA peers
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=6 | fallback []
      mechanism: EBITDA ignores reinvestment needs, so two firms with equal EBITDA are worth less if one must spend much more on capex to sustain it; capital intensity should therefore lower EV/EBITDA. Matching within a 2-digit industry on capex intensity, growth, and margin captures the free-cash-flow conversion and growth that drive the multiple, while the broader L2 pool gives enough close matches.
      prediction: Pooled median |ln error| below 0.333 and beats the industry-median baseline in at least 3 of 4 years; error should be lower than baseline especially for high-capex firms.

  (2) Nested-industry nearest-size EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The finest industry definition (4-digit SIC) best matches products, customers and cost structure, which drive common risk and growth; falling back to coarser codes only when needed keeps peers as close as possible. Within that group, nearest growth and size refine the match, since larger, faster-growing firms command different multiples.
      prediction: Beats the L3/L2 industry-median baseline median (0.333) in at least 3 of 4 years and has lower mean error than 0.513.

  (3) L2 margin-matched EV/Sales
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.5 | k=10, median, min_peers=6 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so firms with different margins should have very different sales multiples even in the same industry. Choosing industry peers closest on EBITDA margin (heavily weighted), gross margin and growth removes the main source of EV/Sales dispersion.
      prediction: Pooled median |ln error| at least 0.08 below the EV/Sales industry-median baseline (0.603) and better in all 4 exploration years.

  (4) Cross-industry fundamentals twins EV/Sales
      recipe: EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, roic 1, log_sales 0.5 | k=15, median, min_peers=3
      mechanism: A sales multiple is mechanically driven by profit margin, growth, and returns on capital regardless of industry label, so firms matched on these fundamentals across the whole market should share the multiple. Dropping the industry screen lets the engine find much closer margin matches, which matter more for EV/Sales than industry membership.
      prediction: Beats the EV/Sales industry-median baseline (0.603) in at least 3 of 4 years; if it does not beat the L2 margin-matched recipe, industry still carries information beyond fundamentals.

  (5) L3 margin-band EV/Sales with nearest growth
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03] -> [same industry_l2]
      mechanism: Within a 3-digit industry, restricting peers to firms with EBITDA margin within 5 points of the target forces comparable profitability, the main link between sales and value; nearest growth and size then refine the set. Fallbacks widen the industry definition before abandoning the margin constraint, preserving the economically most important match.
      prediction: Pooled median |ln error| below 0.55 and beats the EV/Sales industry-median baseline in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

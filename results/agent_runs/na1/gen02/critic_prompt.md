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

PROPOSALS
  (0) EBITDA_industry_fundamental_neighbors
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, ebitda_margin 1, log_sales 1 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, EV/EBITDA differences are driven mainly by expected growth, profitability persistence and size-related risk. Choosing the industry peers closest in sales growth, EBITDA margin and scale should isolate firms with similar discount rates and growth paths, removing the noise from dissimilar members of the same industry.
      prediction: Median |ln(V_est/V)| below the L3/L2 industry median baseline (0.333) in at least 3 of 4 exploration years, and pooled median at or below 0.32.

  (1) EBITDA_reinvestment_adjusted
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores the capital needed to sustain it, so firms with heavy capex convert less EBITDA into free cash flow and deserve lower EV/EBITDA. Matching on capex intensity and return on capital, alongside growth, within a broad 2-digit industry pairs firms whose EBITDA has similar cash-flow value per dollar.
      prediction: Beats the L3/L2 industry median baseline in at least 3 of 4 years; improvement concentrated in capital-intensive 2-digit sectors.

  (2) EBITDA_narrow_industry_harmonic
      recipe: EV/EBITDA | screen same industry_l4 | k=all, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The finest industry definition shares the most similar business models, cost structures and investor clienteles, so its members should trade at similar EBITDA multiples. The harmonic mean is the theoretically consistent average for price-scaled ratios and damps the influence of peers with inflated multiples from temporarily depressed EBITDA.
      prediction: Median error within 0.02 of or below the industry median baseline (0.333), and a lower mean error than that baseline (below 0.513) in at least 3 of 4 years.

  (3) Sales_margin_matched_industry
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so a firm's sales multiple is driven chiefly by how much profit each dollar of sales generates. Ranking 2-digit industry peers mainly on EBITDA margin, then growth and size, should remove the largest source of dispersion in sales multiples.
      prediction: Median error below 0.50 pooled, beating the L3/L2 industry median baseline (0.603) in all 4 exploration years.

  (4) Sales_cross_industry_margin_band
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because margin and growth explain most of the variation in EV/Sales, firms with near-identical economics can be good comparables even across industries. A band on EBITDA margin followed by ranking on margin, gross margin, growth and size builds a peer group of economic twins without relying on SIC codes, which are coarse for diversified firms.
      prediction: Beats the industry median EV/Sales baseline (0.603) in at least 3 of 4 years, with pooled median error below 0.55.

  (5) Sales_industry_profitability_efficiency
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1, sales_growth_1y 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, firms with higher gross and EBITDA margins and lower asset intensity earn more value per dollar of sales. Matching on margins and asset turnover captures both pricing power and capital requirements, which together determine how much enterprise value a dollar of revenue supports.
      prediction: Beats the industry median EV/Sales baseline (0.603) in at least 3 of 4 years and beats the Bhojraj-Lee warranted multiple (0.674) in all 4.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

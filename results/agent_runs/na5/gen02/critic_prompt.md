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

PROPOSALS
  (0) L3 fundamentals-matched EBITDA peers (harmonic)
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1.5, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, EV/EBITDA differences are driven mainly by expected growth, return on capital (reinvestment efficiency) and risk/leverage. Ranking same-industry peers on these drivers and averaging with a harmonic mean (which weights by the earnings yield and damps high-multiple outliers) should give a less biased multiple than the plain industry median.
      prediction: Median error below 0.333 (industry median L3/L2) on pooled FY2016-2019 and beats the industry median in at least 3 of 4 years.

  (1) L2 capex-adjusted EBITDA peers
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores reinvestment needs, so firms with heavy capex should trade at lower EV/EBITDA than asset-light firms with the same growth. Matching within the 2-digit industry on capex intensity, growth, ROIC and size captures how much of EBITDA is truly free cash flow and how durable it is.
      prediction: Median error at most 0.33 and lower mean error than the industry median (0.513) on FY2016-2019.

  (2) L4-first EBITDA peers, size and margin tie-break
      recipe: EV/EBITDA | screen same industry_l4 | rank log_sales 1, ebitda_margin 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: The narrowest industry definition best matches business model, cyclicality and risk, which are the dominant determinants of EV/EBITDA; within that, size (liquidity, diversification) and EBITDA margin (pricing power) refine the match. Falling back to coarser industries only when the 4-digit group is thin keeps peers economically close.
      prediction: Beats the industry median (L3, fallback L2) median error in at least 3 of 4 exploration years.

  (3) L2 margin-matched EV/Sales peers
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales mechanically equals EV/EBITDA times EBITDA margin, so the profitability of each sales dollar is the first-order driver of the sales multiple. Ranking same-sector peers heavily on EBITDA margin, then growth and gross margin, aligns peers' value per dollar of revenue with the target's.
      prediction: Median error below 0.55, beating the EV/Sales industry median (0.603) in all 4 exploration years.

  (4) Cross-industry margin-band EV/Sales peers
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, gross_margin 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales is dominated by margin and growth rather than industry labels, firms with nearly identical EBITDA margins should carry similar sales multiples even across sectors. A hard band on EBITDA margin plus ranking on margin, growth and ROIC uses the whole cross-section to find economically equivalent revenue streams.
      prediction: Median error below 0.603 (industry median) on pooled FY2016-2019 and beats it in at least 3 of 4 years.

  (5) L3 margin-and-growth EV/Sales peers (harmonic)
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, asset_turnover 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, the residual dispersion of EV/Sales comes from profitability, growth and capital intensity (asset turnover). Ranking on these and using a harmonic mean, which avoids being pulled up by a few richly valued high-margin peers, should reduce the large errors typical of sales multiples.
      prediction: Lower mean error than the EV/Sales industry median (0.945) and median error below 0.60 on FY2016-2019.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

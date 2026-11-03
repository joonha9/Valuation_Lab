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
  (none)

PROPOSALS
  (0) EBITDA_L2_growth_return_reinvestment
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: In a DCF, EV/EBITDA = (1 - reinvestment share) x f(growth, discount rate), so firms with similar growth, return on capital and capex burden should share the multiple. Restricting to the same 2-digit industry holds systematic risk roughly fixed, while ranking on growth, ROIC and capex intensity picks the peers whose cash conversion and growth outlook match the target's.
      prediction: Median |ln error| below the L3 industry median baseline (0.333) in at least 3 of 4 exploration years, with pooled median <= 0.32.

  (1) EBITDA_L3_size_leverage_harmonic
      recipe: EV/EBITDA | screen same industry_l3 | rank log_assets 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow industry, larger and less levered firms carry lower risk and so command higher EV/EBITDA, while recent growth captures near-term expectations. The harmonic mean of peer multiples corresponds to averaging earnings yields, which is less biased upward by a few high-multiple peers than an arithmetic mean.
      prediction: Beats the L3 industry median baseline on pooled median error, and has a lower mean error than 0.513 in every exploration year.

  (2) EBITDA_crossindustry_business_model
      recipe: EV/EBITDA | rank gross_margin 1, ebitda_margin 1, capex_intensity 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=3
      mechanism: Business-model fundamentals such as gross margin, EBITDA margin, capital intensity and growth summarize competitive position and reinvestment needs better than coarse SIC codes, which mix very different firms. Peers that look alike on these economics should face similar growth-adjusted valuations wherever they are classified.
      prediction: Pooled median error within 0.02 of the L3 industry median baseline, and beats it in at least 2 of 4 years, showing that fundamentals alone can stand in for industry membership.

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the cross-sectional spread in sales multiples comes from profitability differences. Matching peers mainly on EBITDA margin, plus gross margin and growth, within the same 2-digit industry removes the main source of error in a plain industry EV/Sales.
      prediction: Pooled median error at least 0.10 below the EV/Sales L3 industry median baseline (0.603), and better in all 4 exploration years.

  (4) Sales_margin_band_crossindustry_harmonic
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Firms with nearly the same EBITDA margin turn a dollar of sales into similar cash flow, so their EV/Sales should be close once growth and capital intensity are also matched, whatever their industry. A hard margin band keeps peers with very different profitability out, and harmonic aggregation limits the upward pull from high-multiple growth names.
      prediction: Beats the EV/Sales L3 industry median baseline on pooled median error in at least 3 of 4 years, with mean error below 0.837 (the Bhojraj-Lee warranted baseline).

  (5) Sales_L3_margin_roic_trimmed
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, roic 1, log_sales 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow industry, value per dollar of sales depends on how profitably sales are produced (margin) and how efficiently capital is used (ROIC), since these set free cash flow for a given amount of growth. A trimmed mean over a small, closely matched peer set keeps the information in the central peers while discarding outliers.
      prediction: Pooled median error below 0.50 and better than the EV/Sales L3 industry median baseline in all 4 exploration years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

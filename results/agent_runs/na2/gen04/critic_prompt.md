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
  [g02-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, gross_margin 0.75, debt_to_assets 0.5, log_sales 0.5 | k=15, median, min_peers=3
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, roic 0.75, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> [band ebitda_margin±0.15] -> []
  [g02-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 3, sales_growth_1y 1, asset_turnover 0.5, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 1, net_debt_to_ebitda 0.5 | k=10, median, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank log_sales 0.5, roic 1, sales_growth_1y 1 | k=6, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | rank capex_intensity 1, ebitda_margin 1, sales_growth_1y 1, roic 1, gross_margin 0.5 | k=15, median, min_peers=3
  [g03-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g03-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g03-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) EBITDA_L2_growth_margin_size
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: Within a broad industry, EV/EBITDA is driven mainly by expected growth and the durability of profits; firms with similar recent growth, similar EBITDA margins and similar scale face similar risk and reinvestment needs. Ranking same-sector peers on these fundamentals should isolate firms whose market multiples embed the same growth-risk tradeoff.
      prediction: Median |ln(V_est/V)| below the 0.333 industry-median baseline in at least 3 of 4 exploration years.

  (1) EBITDA_L3_capex_conversion
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, roic 1, sales_growth_1y 0.75 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores capital expenditure, so capex-heavy firms convert less EBITDA to free cash flow and deserve lower EV/EBITDA; firms with high ROIC create more value per dollar reinvested. Matching on capex intensity, ROIC and growth within a narrow industry captures the cash-conversion and value-creation determinants of the multiple.
      prediction: Beats the L3/L2 industry median in at least 3 of 4 years and has a lower pooled mean error than 0.513.

  (2) EBITDA_L2_harmonic_leverage_risk
      recipe: EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 0.75, roic 1, sales_growth_1y 1, log_assets 0.5 | k=12, harmonic_mean, min_peers=5 | fallback []
      mechanism: Leverage and profitability proxy for equity risk and distress, which compress enterprise multiples; the harmonic mean is the theoretically consistent average for price-scaled ratios and damps peers with inflated multiples from temporarily depressed EBITDA. Peers in the same sector with similar net leverage, ROIC and size should share discount rates and hence multiples.
      prediction: Median error at or below 0.33 pooled across FY2016-2019 and beats the warranted-multiple regression (0.357) in every year.

  (3) Sales_L2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 0.75, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant source of cross-firm dispersion in sales multiples is profitability. Selecting same-sector peers with nearly identical EBITDA margins and similar growth removes most of that dispersion, leaving peers whose sales are worth the same to investors.
      prediction: Median error below 0.50, beating the 0.603 industry-median baseline in all 4 exploration years.

  (4) Sales_crossindustry_margin_band
      recipe: EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 1.5, sales_growth_1y 1, capex_intensity 0.5, gross_margin 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales scales almost mechanically with margins, firms with the same EBITDA margin and growth across industries may be better comparables than same-industry firms with very different profitability. A tight margin band followed by ranking on margin, growth and capital intensity builds an economic rather than SIC-based peer group.
      prediction: Beats the industry-median baseline (0.603) in at least 3 of 4 years, with median error below 0.55 pooled.

  (5) Sales_L3_margin_roic_harmonic
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, roic 0.75, sales_growth_1y 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within a narrow industry, firms with similar margins and ROIC earn similar economic profits per dollar of sales, and similar growth implies similar duration of those profits, so the value of a dollar of sales should match. The harmonic mean guards against a few richly valued peers inflating the estimate.
      prediction: Median error below the 0.603 industry median in at least 3 of 4 years and below the warranted-multiple peers baseline (0.691) in all years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

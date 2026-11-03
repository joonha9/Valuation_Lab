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
  [g01-01] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-02] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5
  [g01-03] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-04] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
  [g01-06] EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 1, log_assets 1, roic 1 | k=10, harmonic_mean, min_peers=5 | fallback []

PROPOSALS
  (0) ebitda_cross_industry_cash_conversion
      recipe: EV/EBITDA | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, ebitda_margin 0.5 | k=20, median, min_peers=5
      mechanism: In a steady-state DCF, EV/EBITDA equals (1 - reinvestment share of EBITDA) / (WACC - g), and the reinvestment share depends on capital intensity and on the return earned on new capital, not on the industry label. Firms from any industry with similar capex intensity, ROIC, growth and EBITDA margin convert EBITDA into free cash flow at similar rates, and a large cross-industry pool of such firms gives a steadier median than a thin industry group.
      prediction: Median error below the EV/EBITDA industry-median baseline (0.333) in at least 3 of 4 exploration years, with full coverage.

  (1) ebitda_da_share_size_band
      recipe: EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: The gap between EBITDA margin and EBIT margin is depreciation as a share of sales, which measures how much capital the business uses up each year that EBITDA ignores. Peers in the same 3-digit industry and of similar size (a proxy for risk and discount rate) that match on both margins and on growth consume capital at a similar rate, so they should share the target's EV/EBITDA. The harmonic mean damps the few richly valued peers that skew multiples upward.
      prediction: Beats the EV/EBITDA industry median in at least 3 of 4 years, with a lower mean error than the industry baseline (0.513).

  (2) ebitda_business_model_intangibles
      recipe: EV/EBITDA | screen same industry_l3 | rank rnd_intensity 1, asset_turnover 1, gross_margin 1, sales_growth_1y 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Because R&D is expensed, EBITDA understates the cash-generating capacity of R&D-heavy firms and they trade at higher EV/EBITDA, while asset turnover and gross margin capture whether a firm earns its profits through pricing power or volume on heavy assets. Within a 3-digit industry, peers that match on R&D intensity, asset turnover, gross margin and growth share the same business model and the same bias in reported EBITDA, so their multiple carries over. The trimmed mean removes extreme peers without discarding the middle of the distribution.
      prediction: Beats the EV/EBITDA industry median in at least 3 of 4 years; the gain is largest in years with many technology and healthcare firms.

  (3) sales_margin_with_rnd_adjustment
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, rnd_intensity 1, gross_margin 1 | k=8, harmonic_mean, min_peers=4 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, but for firms that expense large R&D budgets the reported EBITDA margin understates their economic margin, so two firms with the same EBITDA margin can deserve different sales multiples. Matching peers in the same 2-digit industry on EBITDA margin, R&D intensity and gross margin lines up the true pre-investment profitability per dollar of sales, and the harmonic mean damps upward skew in sales multiples.
      prediction: Median error below the EV/Sales industry-median baseline (0.603) in all 4 years, and below 0.55 on average.

  (4) sales_hard_margin_band_cross_industry
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
      mechanism: Profitability is the dominant driver of sales multiples, so a hard screen holding EBITDA margin within a few points of the target's guarantees that every peer has the same margin term, instead of trading margin off against other features in a distance ranking. Within that margin band, firms from any industry that also match on growth, gross margin, capital intensity and size should be priced similarly per dollar of sales.
      prediction: Beats the EV/Sales industry median in all 4 years with a mean error below the industry baseline (0.945).

  (5) sales_fcf_margin_proxy
      recipe: EV/Sales | screen same industry_l3 | rank ebit_margin 2, capex_intensity 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: In a DCF, EV/Sales is approximately the free-cash-flow margin divided by (WACC - g), and the free-cash-flow margin is roughly after-tax EBIT margin minus capital spending as a share of sales. Peers in the same 3-digit industry that match on EBIT margin, capex intensity and growth therefore share both the cash margin and the growth term that set the sales multiple; using EBIT rather than EBITDA already charges for depreciation.
      prediction: Beats the EV/Sales industry median in at least 3 of 4 years, with median error below 0.56.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

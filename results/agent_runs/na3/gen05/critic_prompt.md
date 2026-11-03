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
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-03] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-05] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, roic 1, log_sales 0.5 | k=15, median, min_peers=3
  [g02-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03] -> [same industry_l2]
  [g03-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, ebit_margin 1, sales_growth_1y 0.75, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=5 | fallback []
  [g03-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g03-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 1.5, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
  [g03-06] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, capex_intensity 0.75, asset_turnover 0.75, log_sales 0.5 | k=20, median, min_peers=3
  [g04-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_assets 0.75 | k=10, median, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g04-03] EV/EBITDA | screen same industry_l3 | k=all, harmonic_mean, min_peers=3 | fallback [same industry_l2]
  [g04-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g04-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) EBITDA_L3_value_drivers
      recipe: EV/EBITDA | screen same industry_l3 | rank roic 1, sales_growth_1y 1, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a DCF, EV/EBITDA rises with growth and with return on capital (less reinvestment is needed per unit of growth), and falls as more EBITDA goes to capex. Peers in the same 3-digit industry that are closest on ROIC, growth and capex intensity should share the target's warranted multiple better than the industry as a whole.
      prediction: Median |ln error| below 0.333 (L3/L2 industry median) on the pooled FY2016-2019 sample, and beats the industry median in at least 3 of 4 years.

  (1) EBITDA_L2_harmonic_quality
      recipe: EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, sales_growth_1y 1, log_sales 1, capex_intensity 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: Firms with similar margins, growth and size face similar risk and reinvestment needs, so they are priced at similar EBITDA multiples. Using the wider 2-digit pool gives more fundamentally close peers. The harmonic mean is the right way to average price ratios because it averages the earnings yields and limits the pull of very high multiples.
      prediction: Median |ln error| below 0.333 overall and a mean error below 0.513 (industry median), with lower mean error than the median-aggregated version.

  (2) EBITDA_L3_leverage_growth_trimmed
      recipe: EV/EBITDA | screen same industry_l3 | rank net_debt_to_ebitda 1, sales_growth_1y 1, roic 1 | k=12, trimmed_mean, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: Leverage changes how EV is split between debt and equity holders and is a sign of how mature and stable a firm's cash flows are. High-net-debt firms are usually mature and trade at lower EBITDA multiples. Matching on net debt/EBITDA, growth and ROIC inside the 3-digit industry captures both risk and growth, and a trimmed mean keeps stable averaging while cutting outliers.
      prediction: Median |ln error| at or below 0.333 overall and better than the Bhojraj-Lee warranted multiple (0.357) in every exploration year.

  (3) Sales_L3_margin_matched
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 3, sales_growth_1y 1, gross_margin 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so differences in profitability within an industry drive most of the spread in sales multiples. Choosing 3-digit industry peers mostly by EBITDA margin, then by growth and gross margin, removes the largest source of error the plain industry median leaves in.
      prediction: Median |ln error| below 0.50, beating the industry median (0.603) by at least 0.08 in each of the 4 years.

  (4) Sales_crossindustry_margin_growth
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1.5, sales_growth_1y 1, asset_turnover 1 | k=15, median, min_peers=3
      mechanism: A dollar of sales is worth about the same anywhere if it comes with the same margin, growth and capital intensity, whatever the SIC code. Ranking across all firms on EBITDA margin, gross margin, growth and asset turnover finds economically close peers that industry codes miss, especially for firms whose industry is a mix of different business models.
      prediction: Median |ln error| below 0.55, beating the industry median (0.603) in at least 3 of 4 years and the warranted multiple (0.674) in all 4.

  (5) Sales_L2_margin_band_harmonic
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.1] -> [band ebitda_margin±0.05] -> []
      mechanism: A hard band on EBITDA margin ensures every peer turns sales into cash flow at a similar rate, which is the main driver of the sales multiple. Within that band, matching on growth and ROIC inside the 2-digit industry adds the next value drivers, and the harmonic mean limits the upward pull of richly valued peers.
      prediction: Median |ln error| below 0.52 overall and mean |ln error| below 0.837 (the warranted multiple's mean).

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

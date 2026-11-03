You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 2). Accuracy is the median of |ln(V_est / V)|
across firm-years, where V is the firm's actual enterprise value on June 30 after its fiscal year.
Lower is better. Recipes are scored only on exploration years FY2016-2019; the
best ones will later be tested ONCE on later years you will never see, so prefer rules with a
clear economic reason over fragile tweaks. Cover both multiples across your proposals.

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

BASELINES (exploration years)
  EV/EBITDA: Industry median (L3, fallback L2) median 0.333, mean 0.513; Warranted multiple (Bhojraj-Lee regression) median 0.357, mean 0.492; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.380, mean 0.523
  EV/Sales: Industry median (L3, fallback L2) median 0.603, mean 0.945; Warranted multiple (Bhojraj-Lee regression) median 0.674, mean 0.837; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.691, mean 0.861

ARCHIVE: your earlier graded attempts, exploration scores only (6 graded)
  [g01-04] EV/EBITDA median 0.322 | mean 0.490 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, net_debt_to_ebitda 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
      mechanism: A Gordon-style decomposition implies EV/EBITDA rises with growth and with return on invested capital (less reinvestment needed per unit of growth) and falls with risk. Within a 2-digit sector, peers closest in sales growth, ROIC and leverage should therefore share the target's EBITDA multiple more closely than the full industry median.
  [g01-05] EV/EBITDA median 0.332 | mean 0.506 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.007
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 2, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores capital expenditure, so firms that must reinvest heavily to sustain EBITDA convert less of it into free cash flow and trade at lower EV/EBITDA. Matching on capex intensity and EBITDA margin within a 3-digit industry aligns the cash conversion of EBITDA, and the harmonic mean is the unbiased average for price-scaled ratios.
  [g01-06] EV/EBITDA median 0.339 | mean 0.515 | coverage 100.0% | beats industry 1/4 yrs | gain vs industry -0.001
      EV/EBITDA | screen same industry_l4 | rank log_sales 1, log_assets 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: The narrowest industry definition captures shared products, customers and regulatory risk, and among those close competitors firm size proxies for diversification, market power and lower risk, which raises the multiple. Cascading from 4-digit to 2-digit SIC keeps peers as close as the data allow while size ranking removes the scale mismatch inside small industries.
  [g01-03] EV/Sales median 0.407 | mean 0.607 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.339
      EV/Sales | screen same industry_l3, band ebitda_margin±0.06 | rank sales_growth_1y 1, log_sales 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.06] -> [band ebitda_margin±0.04] -> []
      mechanism: A hard band on EBITDA margin forces peers to share the profitability that converts sales into value, while the 3-digit industry screen holds business model and risk roughly constant. Remaining peers are ordered by growth and size, the next most important drivers of the multiple after margin.
  [g01-02] EV/Sales median 0.419 | mean 0.659 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.287
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, asset_turnover 1 | k=15, median, min_peers=3
      mechanism: With no industry screen, peers are chosen purely on the economic drivers of the sales multiple: profitability (EBITDA and gross margin), growth, and capital intensity (asset turnover, which proxies reinvestment needs). Firms with the same margin, growth and asset-intensity profile should command similar EV/Sales regardless of SIC label, and a larger pool lets the nearest matches be closer.
  [g01-01] EV/Sales median 0.552 | mean 0.806 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.139
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales is approximately EV/EBITDA times EBITDA margin, so most of the cross-sectional spread in sales multiples comes from differences in profitability. Within a 2-digit sector (similar cost structure and risk), peers with the closest EBITDA margin and growth should have the closest sales multiple.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

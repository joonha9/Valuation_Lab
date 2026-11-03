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
  [g01-05] EV/EBITDA median 0.318 | mean 0.467 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.047
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5 | k=20, median, min_peers=3
      mechanism: Firms with similar growth, ROIC, reinvestment needs, intangible intensity and leverage have similar cash-flow profiles and risk, so they should capitalize EBITDA at similar rates whatever their SIC code. Using more peers (k=20) cuts noise from any single mispriced comparable.
  [g01-04] EV/EBITDA median 0.329 | mean 0.511 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.003
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Close industry peers share technology, cyclicality and risk, and within that group growth and return on capital separate high- from low-multiple firms. The harmonic mean averages earnings yields rather than multiples, so a few very high-multiple peers do not pull the estimate up.
  [g01-01] EV/EBITDA median 0.330 | mean 0.499 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.014
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: In a constant-growth model EV/EBITDA rises with expected growth and with the share of EBITDA that turns into free cash flow (high ROIC, low reinvestment). Peers in the same 2-digit industry that match on growth, ROIC and capex intensity should share discount-rate exposure and cash conversion, so they should trade at similar EBITDA multiples.
  [g01-06] EV/Sales median 0.391 | mean 0.672 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.272
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: A hard band on EBITDA margin makes sure every peer has nearly the same profit per dollar of sales, so the target's sales multiple is not inferred from firms with a different margin. Ranking those peers on gross margin, growth and size then picks firms with a similar cost structure and growth outlook.
  [g01-02] EV/Sales median 0.474 | mean 0.771 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.174
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most cross-sectional variation in sales multiples comes from profitability. Within a 2-digit industry, peers with nearly the same EBITDA and gross margins (and similar growth) should carry similar sales multiples.
  [g01-03] EV/Sales median 0.540 | mean 0.761 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.185
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=15, median, min_peers=3
      mechanism: Sales multiples are driven by margin, growth and intangible intensity more than by SIC labels, which are coarse and often stale. Matching on EBITDA margin, gross margin, growth and R&D intensity across the whole market should find economically similar firms even where the industry is thin.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

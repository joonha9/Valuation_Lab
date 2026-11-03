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
  [g01-03] EV/EBITDA median 0.330 | mean 0.505 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.009
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 2, sales_growth_1y 1, roic 1, debt_to_assets 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores capital spending, so two firms with equal EBITDA but different capex intensity convert very different shares of it into free cash flow; capital-heavy firms should trade at lower EV/EBITDA. Matching peers within the 2-digit industry on capex intensity, growth and leverage aligns the cash-conversion and risk profile that the multiple prices.
  [g01-02] EV/EBITDA median 0.335 | mean 0.511 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.002
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, ebitda_margin 1, log_sales 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: In a DCF, EV/EBITDA rises with expected growth and with return on invested capital (less reinvestment needed per unit of growth), and falls with risk. Within a broad industry, picking the nearest peers on growth, ROIC, margin and size targets firms with the same value drivers rather than just the same SIC label.
  [g01-01] EV/EBITDA median 0.341 | mean 0.532 | coverage 100.0% | beats industry 0/4 yrs | gain vs industry -0.018
      EV/EBITDA | screen same industry_l3 | k=all, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share demand cycles, risk and reinvestment needs, so their EV/EBITDA multiples cluster. The harmonic mean averages the inverse multiple (an earnings yield), which is less sensitive to a few peers with very high multiples from temporarily low EBITDA, and is known to reduce upward bias relative to the arithmetic mean.
  [g01-05] EV/Sales median 0.409 | mean 0.654 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.292
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1, asset_turnover 1 | k=15, median, min_peers=5
      mechanism: If value per dollar of sales is driven by margin, growth and capital efficiency, firms with the same fundamentals should carry similar EV/Sales regardless of SIC code; SIC codes are coarse and often misclassify diversified firms. Dropping the industry screen enlarges the pool so the nearest neighbours match much more tightly on the actual value drivers.
  [g01-06] EV/Sales median 0.412 | mean 0.625 | coverage 94.0% | beats industry 4/4 yrs | gain vs industry +0.201
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | k=all, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [same industry_l2, band ebitda_margin±0.1] -> [band ebitda_margin±0.03]
      mechanism: A sales multiple is only comparable among firms with similar profitability; within the same industry, restricting peers to those whose EBITDA margin is within 5 points of the target's removes the main source of dispersion in EV/Sales. The harmonic mean then damps the influence of high-multiple peers in the band.
  [g01-04] EV/Sales median 0.477 | mean 0.779 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.166
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the main driver of a sales multiple is profitability. Within the same 2-digit industry, peers with similar EBITDA and gross margins and similar growth should share the target's EV/Sales much more closely than the industry as a whole.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

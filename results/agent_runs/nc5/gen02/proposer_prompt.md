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
  [g01-03] EV/EBITDA median 0.325 | mean 0.489 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank ebitda_margin 1, roic 0.8, sales_growth_1y 0.6 | k=8, median, min_peers=4 | fallback [same industry_l2] -> [band log_sales±1]
      mechanism: Size proxies for risk, diversification and liquidity premia, so similar-size peers in the same broad industry share discount rates. Within that size band, matching on EBITDA margin and ROIC aligns profitability durability and competitive position, which drive the persistence of EBITDA.
  [g01-02] EV/EBITDA median 0.325 | mean 0.491 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 0.7, log_assets 0.4 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores capital intensity, so firms that must reinvest more of EBITDA in capex deserve lower EV/EBITDA; leverage proxies for risk and financial distress. Matching within a 2-digit industry on capex intensity, net debt/EBITDA and growth captures the conversion of EBITDA to free cash flow and its risk.
  [g01-01] EV/EBITDA median 0.333 | mean 0.512 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.002
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and with return on capital (lower reinvestment needed per unit of growth). Within a 3-digit industry, peers closest on recent growth and ROIC should share discount rates and value-driver economics, and the harmonic mean limits the upward bias of averaging ratios with a price numerator.
  [g01-05] EV/Sales median 0.401 | mean 0.664 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.281
      EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.7, asset_turnover 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales scales almost linearly with operating margin, firms with similar EBITDA margins and growth should trade at similar sales multiples even across industries. A tight margin band plus ranking on margin, growth and asset turnover selects economically similar cash-flow generators from the full cross-section, giving larger and closer peer sets than industry codes.
  [g01-04] EV/Sales median 0.474 | mean 0.774 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.171
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.8 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant cross-sectional driver of EV/Sales is profitability. Ranking 2-digit industry peers primarily on EBITDA margin, then gross margin and growth, should remove most of the margin-driven dispersion that plagues industry-median EV/Sales.
  [g01-06] EV/Sales median 0.507 | mean 0.826 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.117
      EV/Sales | screen same industry_l3 | rank ebitda_margin 2, asset_turnover 0.8, roic 0.6, sales_growth_1y 0.6 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> [band ebitda_margin±0.07]
      mechanism: Within a narrow 3-digit industry, business models are similar, but margin and capital intensity still vary; EV/Sales rises with margin and falls with the capital (low asset turnover) needed to support sales. Matching on EBITDA margin, asset turnover and ROIC with a trimmed mean captures both levers while limiting outlier peers.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

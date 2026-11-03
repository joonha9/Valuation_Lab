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
  [g01-01] EV/EBITDA median 0.322 | mean 0.484 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.030
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a Gordon-style valuation, EV/EBITDA rises with expected growth and with how efficiently growth is funded (ROIC), and falls with financial risk. Industry peers share the same business risk and accounting conventions, so ranking within the industry on growth, ROIC and net leverage should isolate peers with the same fundamental multiple drivers, closer than the industry as a whole.
  [g01-05] EV/EBITDA median 0.322 | mean 0.493 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.010
      EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Narrow 4-digit SIC peers share product markets, customers and cyclicality, so they face the same discount rate and the same long-run growth outlook. Within that narrow group, a small ranking on growth and ROIC refines the match, and the cascade to L3 and L2 keeps coverage when narrow industries are thin.
  [g01-04] EV/EBITDA median 0.325 | mean 0.492 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.022
      EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA overstates distributable cash flow for capital-heavy firms, because capex absorbs part of it. So at equal growth, firms with higher capex intensity should trade at lower EBITDA multiples. Size, in turn, proxies for risk and liquidity premia. Matching on reinvestment needs, growth and margin within a 2-digit industry and a size band should capture both effects.
  [g01-06] EV/Sales median 0.385 | mean 0.564 | coverage 92.1% | beats industry 4/4 yrs | gain vs industry +0.252
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
      mechanism: A hard band on EBITDA margin makes sure every peer converts sales into cash flow at a similar rate, which is the main driver of EV/Sales. Within that band and the 3-digit industry, ranking on growth and size captures the remaining differences in duration and risk. The fallbacks relax the industry screen before they relax the margin match.
  [g01-03] EV/Sales median 0.420 | mean 0.672 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.274
      EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
      mechanism: Once margins, growth and capital intensity are matched, firms produce similar free cash flow per dollar of sales, whatever their SIC code. Searching the whole cross-section for profitability twins gives a larger and closer-matched peer set than industry codes, which often group businesses with very different economics.
  [g01-02] EV/Sales median 0.478 | mean 0.781 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.164
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in profitability. Within a broad 2-digit industry, picking peers with the closest EBITDA and gross margins (plus growth) cancels out the margin term that a plain industry median ignores.

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

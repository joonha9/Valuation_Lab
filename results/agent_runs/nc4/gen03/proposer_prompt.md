You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 3). Accuracy is the median of |ln(V_est / V)|
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

ARCHIVE: your earlier graded attempts, exploration scores only (12 graded)
  [g01-01] EV/EBITDA median 0.327 | mean 0.488 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.025
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
      mechanism: In a steady-state model EV/EBITDA depends on expected growth, the return on reinvested capital (which sets how much cash flow growth costs) and risk. Within a broad 2-digit industry that shares macro exposure, the peers closest on sales growth, ROIC and leverage should have the most similar warranted EV/EBITDA, and the median makes it robust to outliers.
  [g02-01] EV/EBITDA median 0.327 | mean 0.489 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.025
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA ignores capital expenditure, so two firms with identical growth and ROIC but different capex needs convert EBITDA to free cash flow at very different rates and deserve different multiples. Adding capex intensity to the growth, ROIC, leverage and size match of the best generation-1 recipe, inside a 2-digit industry that shares macro risk, should pick peers whose free-cash-flow conversion and therefore warranted EV/EBITDA most closely match the target.
  [g01-02] EV/EBITDA median 0.329 | mean 0.508 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.006
      EV/EBITDA | screen same industry_l3 | rank log_sales 1, sales_growth_1y 1, ebitda_margin 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Narrow-industry peers share technology, cyclicality and cost structure; within that set, size proxies for risk and diversification while recent growth proxies for expected growth, the two main determinants of EV/EBITDA beyond industry. The harmonic mean is the unbiased aggregator for price-scaled multiples and dampens high-multiple outliers.
  [g02-03] EV/EBITDA median 0.330 | mean 0.499 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.014
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, roic 0.5, log_sales 0.5 | k=8, median, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit industry peers share technology and demand shocks, and within that set the remaining dispersion in EV/EBITDA comes mostly from growth expectations and how much capex is needed to sustain them. A larger minimum peer count with cascading fallbacks keeps the median stable when the narrow industry is thin.
  [g02-02] EV/EBITDA median 0.331 | mean 0.478 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.036
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=12, median, min_peers=3
      mechanism: A steady-state DCF ties EV/EBITDA to growth, the reinvestment rate needed to fund it (capex intensity and ROIC), and risk (leverage and size), not to the SIC code itself. Taking nearest neighbours on these drivers from the whole cross-section lets the peers be much closer on fundamentals than an industry list allows, the same effect that made cross-industry matching work for EV/Sales.
  [g01-03] EV/EBITDA median 0.335 | mean 0.510 | coverage 98.3% | beats industry 3/4 yrs | gain vs industry +0.001
      EV/EBITDA | screen same industry_l4 | k=all, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Four-digit SIC peers are the closest economic substitutes, sharing product markets and demand shocks, so their EV/EBITDA should embed the most similar growth and risk expectations. A cascading fallback to L3 and L2 preserves coverage when the narrow industry is thin.
  [g02-05] EV/Sales median 0.391 | mean 0.639 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.307
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> []
      mechanism: Within a 2-digit industry, firms share risk and business model, and a hard EBITDA-margin band guarantees comparable profitability, the main driver of EV/Sales. The broader L2 pool (rather than L3) leaves more candidates inside the band, and ranking on margin and growth with a median aggregator gives a stable estimate.
  [g02-04] EV/Sales median 0.404 | mean 0.615 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.331
      EV/Sales | screen band ebitda_margin±0.03 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.06] -> []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so a tight hard band on EBITDA margin removes the dominant source of error, and EV/EBITDA in turn depends on growth and capex needs. Drawing peers from all industries inside the margin band, then ranking on margin, gross margin, growth and capex intensity, matches both factors of the identity.
  [g01-06] EV/Sales median 0.412 | mean 0.625 | coverage 94.0% | beats industry 4/4 yrs | gain vs industry +0.201
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, ebitda_margin 1 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.08] -> [band ebitda_margin±0.05]
      mechanism: A hard band on EBITDA margin guarantees that peers have comparable profitability, the dominant driver of EV/Sales, while the industry screen holds business model and risk roughly constant. Ranking the survivors on gross margin and growth refines the match, and the harmonic mean limits the influence of richly valued peers.
  [g01-05] EV/Sales median 0.418 | mean 0.609 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.336
      EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, asset_turnover 0.5, log_sales 0.5 | k=10, median, min_peers=3
      mechanism: If EV/Sales is determined by margins, growth and capital intensity, then fundamental twins from any industry should share the multiple, and a larger cross-industry pool lets the nearest neighbours be much closer on these drivers than an industry list allows. Asset turnover and capex intensity capture the reinvestment needed to sustain growth.
  [g01-04] EV/Sales median 0.476 | mean 0.774 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.171
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most cross-sectional dispersion in EV/Sales is driven by profitability. Matching peers on EBITDA and gross margin within a 2-digit industry, with growth as a secondary driver, should neutralize the main source of error that plagues industry-median EV/Sales.
  [g02-06] EV/Sales median 0.490 | mean 0.722 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.225
      EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, gross_margin 1, capex_intensity 1, net_debt_to_ebitda 0.5 | k=15, trimmed_mean, min_peers=3
      mechanism: Because EV/Sales is EBITDA margin times EV/EBITDA, the margin match should dominate, with growth, capex intensity and leverage acting as secondary determinants of the EV/EBITDA factor. A larger peer set aggregated by trimmed mean averages out idiosyncratic valuation noise while discarding extreme multiples.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

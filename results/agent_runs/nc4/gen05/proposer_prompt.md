You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 5). Accuracy is the median of |ln(V_est / V)|
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

ARCHIVE: your earlier graded attempts, exploration scores only (24 graded)
  [g04-03] EV/EBITDA median 0.307 | mean 0.472 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.041
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, gross_margin 0.5, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: Gross margin captures intangible investment expensed above EBITDA, while EBITDA margin captures operating leverage and earnings risk per dollar of EBITDA; each one improved the L2 base recipe separately. Matching both, with a slightly larger peer set of 10 to reduce noise in the median, should pair firms with similar cost structures on both sides of SG&A.
  [g03-01] EV/EBITDA median 0.308 | mean 0.472 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.039
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, gross_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5
      mechanism: Firms with high gross margins typically expense large amounts of brand, sales and R&D investment through SG&A, which depresses reported EBITDA relative to economic earnings and so raises EV/EBITDA. Adding gross margin to the growth, ROIC, leverage and size match of the best L2 recipe should pair firms with similar hidden intangible investment, removing a systematic source of EV/EBITDA error.
  [g04-02] EV/EBITDA median 0.311 | mean 0.475 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.039
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, gross_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=10 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit peers share product markets and demand shocks, and earlier tests showed that using them only when at least 10 candidates exist gave a small gain over plain L2. Combining that depth-gated L3 pool with the gross-margin intangible match should add both effects: closer product-market twins where the industry is deep, and the L2 pool otherwise.
  [g04-01] EV/EBITDA median 0.313 | mean 0.476 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.037
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, gross_margin 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback []
      mechanism: Gross margin was the only addition that moved the L2 growth/ROIC/leverage/size recipe from 0.327 to 0.308, consistent with high-gross-margin firms expensing brand, sales and R&D investment through SG&A and so carrying depressed EBITDA and higher EV/EBITDA. If that intangible-investment channel is real, matching on it as strongly as on growth and ROIC should remove more of the systematic error.
  [g03-03] EV/EBITDA median 0.316 | mean 0.486 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.028
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=12, median, min_peers=6 | fallback []
      mechanism: EV/EBITDA peer medians are noisy with only 8 peers; within a 2-digit industry a larger set of 12 fundamental neighbours should reduce idiosyncratic valuation noise. Adding EBITDA margin as a light ranking term matches operating leverage, since low-margin firms carry more earnings risk per dollar of EBITDA and warrant lower multiples.
  [g03-02] EV/EBITDA median 0.324 | mean 0.486 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.027
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=10 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit peers share product markets and demand shocks, but only help when the industry is deep enough that fundamental ranking can still find close twins. Requiring at least 10 L3 candidates before using them, and otherwise falling back to L2 and then the whole cross-section, uses the narrow industry only where it adds information while ranking on growth, ROIC, leverage and size.
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
  [g03-04] EV/Sales median 0.359 | mean 0.547 | coverage 91.6% | beats industry 4/4 yrs | gain vs industry +0.257
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, roic 0.5 | k=8, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA, so a tighter ±3pp margin band inside a 2-digit industry pins down the first factor more precisely. Ranking on ROIC alongside growth matches the reinvestment efficiency that drives the EV/EBITDA factor, and cascading fallbacks to cross-industry bands keep coverage.
  [g04-04] EV/Sales median 0.384 | mean 0.640 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.305
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, roic 1 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.06] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA; the ±3pp margin band in a 2-digit industry pins the first factor, and ROIC, which sets how much reinvestment growth requires, is the main fundamental driver of the second. Raising ROIC to equal weight with growth and adding a cascade that ends in an unrestricted pool should keep the accuracy of g03-04 while restoring full coverage.
  [g03-06] EV/Sales median 0.388 | mean 0.633 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.313
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> []
      mechanism: After margin, expected growth is the second factor of EV/Sales through its effect on EV/EBITDA, and a hard growth band prevents a few fast-growing or shrinking firms from entering the peer set purely on margin similarity. Requiring both EBITDA margin within ±4pp and one-year growth within ±15pp in a 2-digit industry, with fallbacks that relax the growth band first, should match both factors of the identity.
  [g04-05] EV/Sales median 0.389 | mean 0.613 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.332
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, roic 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: Once margin is pinned by a ±3pp band, the remaining EV/Sales dispersion is the EV/EBITDA factor, which depends on growth, reinvestment efficiency and risk. Adding leverage and size, the two risk proxies that helped EV/EBITDA matching, to the margin/growth/gross-margin/ROIC ranking should match the discount-rate component that the current EV/Sales recipes ignore.
  [g02-05] EV/Sales median 0.391 | mean 0.639 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.307
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> []
      mechanism: Within a 2-digit industry, firms share risk and business model, and a hard EBITDA-margin band guarantees comparable profitability, the main driver of EV/Sales. The broader L2 pool (rather than L3) leaves more candidates inside the band, and ranking on margin and growth with a median aggregator gives a stable estimate.
  [g04-06] EV/Sales median 0.397 | mean 0.650 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.296
      EV/Sales | screen same industry_l2, band ebitda_margin±0.02 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, roic 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.02] -> [band ebitda_margin±0.04] -> []
      mechanism: Narrowing the margin band from ±4pp to ±3pp cut EV/Sales error noticeably, which shows that residual margin mismatch is still a first-order error source because it enters the multiple one-for-one. A ±2pp band within a 2-digit industry, cascading to ±4pp in L2 and then cross-industry bands, should pin the margin factor further while keeping enough peers for a stable median.
  [g03-05] EV/Sales median 0.398 | mean 0.645 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.301
      EV/Sales | screen same industry_l3, band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> []
      mechanism: Within a margin band, the residual EV/Sales dispersion comes from growth and risk, which narrow 3-digit industries hold more constant than 2-digit ones. Using L3 peers inside the ±4pp margin band when at least 5 exist, and otherwise cascading to L2 and then all industries with the same band, combines the closest business models with guaranteed profitability comparability.
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

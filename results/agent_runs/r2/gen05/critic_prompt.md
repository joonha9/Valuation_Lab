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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1.5, roic 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, ebitda_margin 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | screen same industry_l4 | rank log_assets 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-01] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g02-02] EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank ebitda_margin 2, capex_intensity 1, roic 1, log_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.1]
  [g02-03] EV/Sales | screen band gross_margin±0.08, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g02-04] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-06] EV/EBITDA | screen band ebitda_margin±0.05, band sales_growth_1y±0.1 | rank capex_intensity 1.5, roic 1, log_sales 1 | k=15, median, min_peers=5 | fallback [band sales_growth_1y±0.1] -> []
  [g03-01] EV/Sales | screen same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-02] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-03] EV/Sales | screen band ebitda_margin±0.05, band capex_intensity±0.03 | rank sales_growth_1y 1.5, gross_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g03-04] EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5
  [g03-05] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, net_debt_to_ebitda 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5
  [g03-06] EV/EBITDA | screen same industry_l2, band capex_intensity±0.04 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g04-01] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, rnd_intensity 1, gross_margin 1, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, net_debt_to_ebitda 1, roic 0.75, sales_growth_1y 1, log_assets 0.5 | k=15, harmonic_mean, min_peers=5 | fallback []
  [g04-03] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, net_margin 1, roe 0.5, sales_growth_1y 1, log_assets 0.5 | k=12, trimmed_mean, min_peers=5 | fallback []
  [g04-04] EV/Sales | screen same industry_l2, band ebit_margin±0.04 | rank ebit_margin 2, ebitda_margin 1, sales_growth_1y 1, gross_margin 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.04] -> [band ebit_margin±0.08] -> [band ebitda_margin±0.1]
  [g04-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 1.5, sales_growth_1y 1.5, ebitda_margin 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
  [g04-06] EV/Sales | screen same industry_l3, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, ebitda_margin 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05] -> [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]

PROPOSALS
  (0) g05-01 size-banded discount rate peers (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2, band log_sales±1 | rank capex_intensity 1.5, ebit_margin 1, gross_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Small firms carry higher discount rates (size, illiquidity and survival risk), so at the same cash conversion and growth they trade at systematically lower EV/EBITDA. Soft size weights in earlier recipes let a tiny firm be priced off giants whenever margins and capex matched. A hard log-sales band within the 2-digit industry makes size-driven risk a precondition, and ranking on capex intensity, EBIT margin, gross margin and growth then matches cash conversion and durability among similarly sized peers.
      prediction: Beats the industry median in all 4 years and achieves median error at or below 0.315; the gain should be largest for the smallest size quintile of targets.

  (1) g05-02 capital base and return on capital (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank asset_turnover 1.5, roic 1, capex_intensity 1.5, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
      mechanism: Capex intensity measures only the current flow of reinvestment, while asset turnover captures the whole capital base a business needs per dollar of sales, including working capital and acquired intangibles. EV/EBITDA rises when growth can be financed with little capital at a high ROIC. Ranking 2-digit industry peers on asset turnover, ROIC, capex intensity and growth matches the stock and flow of required capital and the return earned on it.
      prediction: Beats the industry median in at least 3 of 4 years with median error below 0.325.

  (2) g05-03 earnings waterfall shape (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, net_margin 1, capex_intensity 1.5, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: How EBITDA flows down to net income (through D&A, interest, taxes and recurring special charges) shows how much of it reaches capital providers as sustainable earnings. Two firms with the same EBITDA margin but very different net margins differ in D&A burden, leverage or recurring write-offs, all of which lower the multiple investors pay per dollar of EBITDA. Matching the whole margin waterfall (EBITDA, EBIT and net margin) plus capex intensity and growth within the 2-digit industry picks peers whose EBITDA is of similar quality.
      prediction: Beats the industry median in all 4 years; median error below 0.320 and mean error below 0.485.

  (3) g05-04 R&D-adjusted economic margin (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank rnd_intensity 1.5, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: R&D is expensed, so among firms with the same reported EBITDA margin, the R&D-heavy ones have higher economic margins and longer-lived growth options, and their sales are worth more. Inside the 2-digit industry plus an EBITDA-margin band, ranking on R&D intensity matches the share of the margin that is hidden investment. Gross margin and growth then line up pricing power and duration.
      prediction: Beats the industry median in all 4 years with median error at or below 0.385; gains concentrated in R&D-intensive industries (SIC 28, 35, 36, 38, 73).

  (4) g05-05 leverage distress discount at fixed margin (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank net_debt_to_ebitda 1.5, sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: With profitability fixed by an EBITDA-margin band, highly levered firms suffer expected distress costs, underinvestment and lost flexibility that lower enterprise value per dollar of sales. Firms with net cash are often priced as having optionality. Ranking margin-matched 2-digit industry peers on net debt to EBITDA, together with growth and capex intensity, aligns the distress discount and the reinvestment burden that the margin alone does not capture.
      prediction: Beats the industry median in all 4 years with median error below 0.390; improvement over g02-01 shows up mainly among targets with net debt/EBITDA above 3.

  (5) g05-06 capital-turnover decomposition (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band asset_turnover±0.3 | rank roic 2, ebitda_margin 1.5, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band asset_turnover±0.3, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: EV/Sales equals EV/invested capital divided by sales/invested capital. The first term is set by ROIC relative to the cost of capital, and the second by capital turnover. A hard asset-turnover band within the 2-digit industry fixes the capital needed per dollar of sales. Ranking on ROIC, then EBITDA margin and growth, fixes the value created per dollar of capital, so the recipe matches both factors of the decomposition rather than margin alone.
      prediction: Beats the industry median in all 4 years; median error below 0.40, testing whether turnover-plus-ROIC matching can rival the EBITDA-margin band approach.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

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

PROPOSALS
  (0) g03-01 industry-plus-cost-structure EV/Sales
      recipe: EV/Sales | screen same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: EV/Sales equals EBITDA margin times an EBITDA multiple. The multiple itself depends on industry risk and on pricing power, which shows up in gross margin. Requiring the same 2-digit industry together with matching gross and EBITDA margins equalizes profitability, cost structure and business risk all at once. Ranking on growth, capex intensity and size then lines up duration and reinvestment needs. Fallbacks to the cross-industry double band and then a wide EBITDA band keep coverage high.
      prediction: Median |ln error| below 0.391, the best archived EV/Sales recipe, and beats the industry median in all 4 exploration years.

  (1) g03-02 nested industry hierarchy with margin band EV/Sales
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: The narrowest industry that still has enough margin-matched peers gives the closest business risk and growth outlook. Starting from the 3-digit industry inside an EBITDA-margin band and widening step by step (2-digit plus band, then band alone, then a wider band) uses the most specific valid peer group for each firm. Ranking on EBITDA margin, gross margin and growth handles any profitability gap left inside the band.
      prediction: Beats the industry median in 4 of 4 years, with median |ln error| at or below 0.40.

  (2) g03-03 free-cash-flow margin match EV/Sales
      recipe: EV/Sales | screen band ebitda_margin±0.05, band capex_intensity±0.03 | rank sales_growth_1y 1.5, gross_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: What sales are worth depends on the free cash flow each dollar of sales produces, which is roughly EBITDA margin minus capex intensity. Two firms with the same EBITDA margin but very different capex needs convert sales to cash at very different rates. Hard bands on both EBITDA margin and capex intensity match FCF margin across industries. Ranking on growth, gross margin (pricing power) and size then handles duration and risk.
      prediction: Median |ln error| below 0.429 (the plain cross-industry EBITDA-margin band) and beats the industry median in all 4 years.

  (3) g03-04 pricing-power and reinvestment EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5
      mechanism: Inside an industry, firms with high gross margins tend to have durable moats and pricing power. Their EBITDA is more persistent and earns a higher multiple. Capex intensity and EBIT margin measure how much of EBITDA is used up by reinvestment and depreciation. Ranking 2-digit industry peers on gross margin, capex, EBIT margin and growth matches both how durable the earnings are and how much of them turns into cash.
      prediction: Median |ln error| at or below 0.320 and beats the industry median in at least 3 of 4 years.

  (4) g03-05 distress-adjusted EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, net_debt_to_ebitda 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5
      mechanism: EV is unlevered in theory, but heavily indebted firms carry expected distress costs and less financial flexibility, which pushes down their EV/EBITDA. Within the 2-digit industry, matching on net debt to EBITDA together with capex intensity, EBIT margin and growth aligns the distress discount, cash conversion and growth outlook. A trimmed mean limits the influence of distressed or richly priced outliers.
      prediction: Beats the industry median in at least 3 of 4 years, with a mean |ln error| below 0.49.

  (5) g03-06 hard capex screen EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l2, band capex_intensity±0.04 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Capex intensity has been the strongest ranking signal for EV/EBITDA, because it sets how much EBITDA must be reinvested to sustain the business. Turning it into a hard band within the 2-digit industry means no peer has a very different reinvestment burden. Ranking on EBIT and EBITDA margins (the D&A gap) plus growth and size then sorts out the remaining differences in value drivers.
      prediction: Median |ln error| below 0.333 (industry median) in at least 3 of 4 years and overall median at or below 0.320.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

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
  [g01-01] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, asset_turnover 1 | k=15, median, min_peers=3
  [g01-03] EV/Sales | screen same industry_l3, band ebitda_margin±0.06 | rank sales_growth_1y 1, log_sales 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.06] -> [band ebitda_margin±0.04] -> []
  [g01-04] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, net_debt_to_ebitda 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
  [g01-05] EV/EBITDA | screen same industry_l3 | rank capex_intensity 2, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-06] EV/EBITDA | screen same industry_l4 | rank log_sales 1, log_assets 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []

PROPOSALS
  (0) g02-sales-margin-band-business-model
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank gross_margin 2, sales_growth_1y 1, rnd_intensity 1 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so a tight margin band removes the main source of dispersion without needing an SIC label. Among firms with the same margin, gross margin and R&D intensity show the business model (asset-light or intangible-heavy versus commodity), which affects how durable and how fast-growing the margin is. These traits describe the economics more directly than the SIC code does.
      prediction: Beats the industry median (L3, fallback L2) EV/Sales in all 4 exploration years, with median |ln error| below 0.45.

  (1) g02-sales-invested-capital-decomposition
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 2, asset_turnover 2, sales_growth_1y 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: EV/Sales can be written as (EV / invested capital) x (invested capital / sales). The first term rises with ROIC relative to the cost of capital, and the second is roughly the inverse of asset turnover. Within a 2-digit sector and an EBITDA-margin band, peers matched on ROIC and asset turnover should line up both terms of this identity, with growth as the remaining value driver.
      prediction: Beats the industry median EV/Sales in at least 3 of 4 years, with median |ln error| below 0.45.

  (2) g02-ebitda-cross-industry-value-drivers
      recipe: EV/EBITDA | rank sales_growth_1y 2, roic 2, capex_intensity 1, net_debt_to_ebitda 1 | k=20, median, min_peers=3
      mechanism: In a steady-state DCF, EV/EBITDA depends on growth, on how much EBITDA must be reinvested (capex intensity, and ROIC as reinvestment efficiency), and on risk (leverage). Firms with the same growth, return, reinvestment and leverage should have similar EBITDA multiples whatever their SIC label. Dropping the industry screen gives a larger pool, so the nearest matches on these drivers can be closer.
      prediction: Median |ln error| at or below 0.333 (industry median) and beats the industry median in at least 2 of 4 years.

  (3) g02-ebitda-growth-band-l3
      recipe: EV/EBITDA | screen same industry_l3, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band sales_growth_1y±0.1] -> [same industry_l2] -> []
      mechanism: Growth is the first-order driver of EV/EBITDA in a Gordon-style model, and soft ranking can still let in peers with very different growth. A hard band on 1-year sales growth inside the 3-digit industry ensures every peer is on a similar growth path. Ranking on ROIC and capex intensity then matches how much of that growth turns into free cash flow.
      prediction: Beats the industry median EV/EBITDA in at least 3 of 4 years, with median |ln error| below 0.330.

  (4) g02-ebitda-intangible-intensity
      recipe: EV/EBITDA | screen same industry_l2 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Under US GAAP, R&D is expensed, so EBITDA understates the economic earnings of intangible-heavy firms and inflates their EV/EBITDA compared with tangible-asset peers in the same sector. Matching on R&D intensity and gross margin within a 2-digit sector aligns this accounting distortion, and growth and ROIC capture the remaining value drivers.
      prediction: Beats the industry median EV/EBITDA in at least 3 of 4 years, with the largest gains in R&D-intensive sectors.

  (5) g02-sales-margin-growth-double-band
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank log_sales 1, capex_intensity 1 | k=6, median, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04, band sales_growth_1y±0.15] -> []
      mechanism: The two first-order drivers of the sales multiple are profitability (margin) and growth, so both are set as hard bands inside the 2-digit sector rather than traded off in a distance metric. Among the survivors, size and capex intensity proxy for risk and reinvestment needs. The cascade loosens the growth band first, because margin explains more of EV/Sales.
      prediction: Beats the industry median EV/Sales in all 4 years, with median |ln error| below 0.42.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

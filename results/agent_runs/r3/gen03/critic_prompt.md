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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-03] EV/EBITDA | rank roic 1, sales_growth_1y 1, capex_intensity 1, rnd_intensity 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=20, trimmed_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.03 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band ebitda_margin±0.06]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, rnd_intensity 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]
  [g02-01] EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, roic 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=6 | fallback []
  [g02-02] EV/EBITDA | screen band sales_growth_1y±0.08 | rank roic 1, capex_intensity 1, rnd_intensity 1, log_assets 0.5, ebitda_margin 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.16] -> []
  [g02-03] EV/EBITDA | screen same industry_l3 | rank ebitda_margin 1.5, net_margin 1, roe 0.5, sales_growth_1y 0.5 | k=7, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-04] EV/Sales | screen band ebitda_margin±0.04 | rank rnd_intensity 1.5, sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.08] -> []
  [g02-05] EV/Sales | rank ebitda_margin 4, ebit_margin 2, sales_growth_1y 1, capex_intensity 1, roic 1 | k=10, median, min_peers=3
  [g02-06] EV/Sales | screen band gross_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5, asset_turnover 0.5 | k=10, median, min_peers=6 | fallback [band gross_margin±0.1] -> []

PROPOSALS
  (0) ebitda_sector_growth_regime
      recipe: EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank ebitda_margin 1, ebit_margin 1, roic 1, capex_intensity 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a growing-perpetuity view EV/EBITDA is roughly (1 - reinvestment rate)/(WACC - g), so peers need both the same discount rate and the same growth regime. A 2-digit sector screen anchors cost of capital and cyclicality, a hard growth band puts peers in the same growth regime, and ranking on EBITDA and EBIT margins, ROIC and capex intensity matches how much of EBITDA must be reinvested to deliver that growth.
      prediction: EV/EBITDA median error below the industry-median baseline (0.333) in at least 3 of 4 exploration years, with pooled median at or below 0.325.

  (1) ebitda_leverage_capacity_band
      recipe: EV/EBITDA | screen band net_debt_to_ebitda±1 | rank roic 1, sales_growth_1y 1, ebit_margin 1, log_assets 1, rnd_intensity 0.5 | k=15, median, min_peers=8 | fallback [band net_debt_to_ebitda±2] -> []
      mechanism: Lenders extend debt as a multiple of EBITDA in proportion to how stable and durable they judge that EBITDA to be, so a firm's net debt/EBITDA is an accounting-based revealed signal of the risk of its cash flows, which is the denominator of the EV/EBITDA multiple. Banding on net debt/EBITDA groups firms with similar perceived cash-flow risk and capital structure across industries, and ranking on ROIC, growth, EBIT margin, size and R&D matches the remaining value drivers.
      prediction: Beats the industry-median EV/EBITDA baseline in at least 3 of 4 exploration years with full or near-full coverage (>95%).

  (2) ebitda_value_chain_position
      recipe: EV/EBITDA | screen same industry_l3 | rank gross_margin 1, asset_turnover 1, ebit_margin 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, firms differ in where they sit on the value chain: branded or proprietary producers have high gross margins and low asset turnover, while commodity processors and distributors have thin margins and fast turnover, and these positions carry different durability of EBITDA and hence different multiples. Matching gross margin, asset turnover and EBIT margin inside the industry, plus growth, picks peers with the same business model rather than just the same product code.
      prediction: EV/EBITDA pooled median error below 0.333 and beats the industry-median baseline in at least 3 of 4 exploration years.

  (3) sales_margin_growth_grid
      recipe: EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, roic 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales is approximately the cash margin of a dollar of sales times a growth-dependent capitalization factor, so the two first-order drivers are margin and growth. A joint hard band on EBITDA margin and sales growth matches both factors directly across industries, and ranking on capex intensity, R&D intensity, ROIC and size matches reinvestment needs and risk, with fallbacks that relax growth first because margin matters most for the sales multiple.
      prediction: EV/Sales pooled median error below 0.40 and beats the industry-median baseline (0.603) in 4 of 4 exploration years.

  (4) sales_ebit_margin_band
      recipe: EV/Sales | screen band ebit_margin±0.03 | rank ebitda_margin 1, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=12, trimmed_mean, min_peers=6 | fallback [band ebit_margin±0.06] -> []
      mechanism: Depreciation and amortization approximate the reinvestment needed to sustain the asset base, so EBIT margin is closer than EBITDA margin to the sustainable free-cash margin per dollar of sales that the sales multiple capitalizes. Banding on EBIT margin and then ranking on EBITDA margin (which jointly pins down D&A intensity), gross margin, growth and R&D intensity matches cash conversion, pricing power and expensed intangible investment.
      prediction: EV/Sales beats the industry-median baseline in 4 of 4 exploration years with pooled median error below 0.42.

  (5) sales_sector_risk_margin_band
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, debt_to_assets 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: A cross-industry EBITDA-margin band matches the cash conversion of sales, but leftover error comes from different discount rates and cyclicality across sectors, which change the multiple applied to that margin. Requiring the same broad 2-digit sector inside the margin band anchors the discount rate while keeping enough candidates, ranking on growth, gross margin, capex intensity and debt-to-assets matches the remaining drivers, and falling back to the pure margin band keeps coverage when the sector is thin.
      prediction: EV/Sales pooled median error below 0.39 and beats the industry-median baseline in 4 of 4 exploration years, with coverage above 90%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

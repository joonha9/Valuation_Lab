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

PROPOSALS
  (0) g02-01 EBITDA sector drivers with D&A wedge
      recipe: EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, roic 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=6 | fallback []
      mechanism: EBITDA ignores depreciation, so two firms with the same EBITDA margin but different EBIT margins differ in how much of EBITDA is consumed by asset replacement and how much is taxable; matching both ebitda_margin and ebit_margin implicitly matches D&A intensity. Doing this inside the 2-digit sector (shared macro risk and cost of capital) while also matching ROIC, growth and leverage combines the industry anchor with the driver-based nearest-neighbour idea, and a trimmed mean limits outlier peers.
      prediction: Median error below the L3 industry median (0.333) and beats it in at least 3 of 4 years, with mean error below 0.50.

  (1) g02-02 EBITDA growth band cross-industry
      recipe: EV/EBITDA | screen band sales_growth_1y±0.08 | rank roic 1, capex_intensity 1, rnd_intensity 1, log_assets 0.5, ebitda_margin 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.16] -> []
      mechanism: In a growing-perpetuity view the EV/EBITDA multiple is most sensitive to expected growth, so a hard band on recent sales growth forces peers into the same growth regime regardless of SIC code. Within that band, ROIC, capex intensity and R&D intensity determine how much of EBITDA must be reinvested to deliver the growth, and size proxies for risk, so the nearest firms on these should share the multiple.
      prediction: Median error at or below 0.335 and beats the industry median in at least 3 of 4 years with coverage above 95%.

  (2) g02-03 EBITDA transitory-margin peers in L3
      recipe: EV/EBITDA | screen same industry_l3 | rank ebitda_margin 1.5, net_margin 1, roe 0.5, sales_growth_1y 0.5 | k=7, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: A large part of cross-sectional EV/EBITDA variation within an industry comes from transitory EBITDA: firms with temporarily depressed margins trade at high multiples because the market capitalizes normalized, not current, earnings. Matching within the 3-digit industry on EBITDA margin, net margin and ROE identifies firms at a similar point relative to normal profitability, so their multiples embed similar mean-reversion expectations.
      prediction: Beats the industry median in at least 3 of 4 years, with the largest gain among firms whose EBITDA margin is far from their industry's typical level.

  (3) g02-04 Sales economic-margin band (R&D add-back)
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank rnd_intensity 1.5, sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.08] -> []
      mechanism: Expensed R&D depresses reported EBITDA margin even though it is an investment, so R&D-heavy firms carry higher EV/Sales than their EBITDA margin suggests. Banding on EBITDA margin and then ranking on R&D intensity matches the economic (pre-R&D) margin, while growth, ROIC and capex intensity match the remaining capitalization and reinvestment drivers of the sales multiple.
      prediction: Median error below 0.40 and beats the industry median in 4 of 4 years, with the biggest improvement over g01-05 in R&D-intensive firms.

  (4) g02-05 Sales soft-margin neighbours full coverage
      recipe: EV/Sales | rank ebitda_margin 4, ebit_margin 2, sales_growth_1y 1, capex_intensity 1, roic 1 | k=10, median, min_peers=3
      mechanism: EV/Sales is approximately EBITDA margin times EV/EBITDA, so the dominant matching variable is margin, but a hard band loses firms; a heavily weighted soft distance on EBITDA and EBIT margin keeps full coverage while still forcing close margin matches. Secondary weights on growth, capex intensity and ROIC match the EV/EBITDA component (growth and reinvestment efficiency), across all industries.
      prediction: Median error below 0.42 with coverage at least 99%, beating the industry median in 4 of 4 years.

  (5) g02-06 Sales gross-margin band with operating leverage
      recipe: EV/Sales | screen band gross_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5, asset_turnover 0.5 | k=10, median, min_peers=6 | fallback [band gross_margin±0.1] -> []
      mechanism: Gross margin reflects pricing power and business model (software vs. distribution), which sets the long-run attainable operating margin; firms in the same gross-margin band but with lower current EBITDA margin are often scaling and are valued on future margins. Banding on gross margin and ranking on EBITDA margin, growth and size matches both the business-model ceiling and the current position toward it.
      prediction: Beats the industry median in at least 3 of 4 years with median error below 0.45 and coverage above 90%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

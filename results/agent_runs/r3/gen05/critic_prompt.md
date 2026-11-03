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
  [g03-01] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank ebitda_margin 1, ebit_margin 1, roic 1, capex_intensity 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-02] EV/EBITDA | screen band net_debt_to_ebitda±1 | rank roic 1, sales_growth_1y 1, ebit_margin 1, log_assets 1, rnd_intensity 0.5 | k=15, median, min_peers=8 | fallback [band net_debt_to_ebitda±2] -> []
  [g03-03] EV/EBITDA | screen same industry_l3 | rank gross_margin 1, asset_turnover 1, ebit_margin 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-04] EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, roic 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g03-05] EV/Sales | screen band ebit_margin±0.03 | rank ebitda_margin 1, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=12, trimmed_mean, min_peers=6 | fallback [band ebit_margin±0.06] -> []
  [g03-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, debt_to_assets 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g04-01] EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank ebitda_margin 1, ebit_margin 1, sales_growth_1y 1, roic 1 | k=12, trimmed_mean, min_peers=6 | fallback [same industry_l2] -> []
  [g04-02] EV/EBITDA | screen band log_assets±0.75 | rank roic 1, sales_growth_1y 1, ebit_margin 1, capex_intensity 1, net_debt_to_ebitda 0.5 | k=15, median, min_peers=8 | fallback [band log_assets±1.5] -> []
  [g04-03] EV/EBITDA | rank sales_growth_1y 2, ebitda_margin 1, ebit_margin 1, roic 1, log_sales 0.5 | k=25, harmonic_mean, min_peers=3
  [g04-04] EV/Sales | screen band roic±0.04 | rank asset_turnover 2, sales_growth_1y 1, ebit_margin 1 | k=12, median, min_peers=6 | fallback [band roic±0.08] -> []
  [g04-05] EV/Sales | screen band gross_margin±0.06, band ebitda_margin±0.04 | rank sales_growth_1y 1, rnd_intensity 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g04-06] EV/Sales | screen band ebitda_margin±0.03, band log_sales±1 | rank sales_growth_1y 1, gross_margin 1, rnd_intensity 1 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []

PROPOSALS
  (0) g05-01 EBITDA operating-leverage band
      recipe: EV/EBITDA | screen band ebitda_margin±0.05 | rank ebit_margin 1, roic 1, sales_growth_1y 1, rnd_intensity 0.5, log_assets 0.5 | k=15, trimmed_mean, min_peers=8 | fallback [band ebitda_margin±0.1] -> []
      mechanism: A firm's EBITDA margin measures its operating leverage: at a 5% margin a 1% change in sales moves EBITDA by many percent, so its EBITDA is a noisy, often temporarily depressed denominator and the market capitalizes it at a higher, more volatile multiple than a 40%-margin firm's stable EBITDA. A hard EBITDA-margin band across industries groups firms whose denominators share the same noise and mean-reversion profile, and ranking on EBIT margin (D&A intensity), ROIC, growth, R&D and size matches the remaining numerator drivers.
      prediction: EV/EBITDA median error below the industry median baseline (0.333) and beats the industry median in at least 3 of 4 years, with coverage of at least 99%.

  (1) g05-02 Sector plus lender-revealed durability
      recipe: EV/EBITDA | screen same industry_l2, band net_debt_to_ebitda±1.5 | rank ebitda_margin 1, ebit_margin 1, roic 1, sales_growth_1y 1 | k=10, trimmed_mean, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: The 2-digit sector sets the base cost of capital and cyclicality, but within a sector lenders still distinguish firms with contracted or recurring EBITDA (which they lend 4-5x against) from firms with fragile EBITDA (lent 1-2x or nothing), so net debt/EBITDA is an accounting-revealed measure of within-sector cash-flow durability. Requiring peers from the same sector AND a similar leverage multiple matches both the sector discount rate and the within-sector durability of the denominator, and ranking on EBITDA and EBIT margins, ROIC and growth matches the remaining drivers.
      prediction: EV/EBITDA median error at or below 0.325 and beats the industry median in all 4 years.

  (2) g05-03 Sector plus capital-structure (trade-off theory)
      recipe: EV/EBITDA | screen same industry_l2, band debt_to_assets±0.1 | rank ebitda_margin 1, ebit_margin 1, net_margin 1, sales_growth_1y 1 | k=12, median, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: Enterprise value includes the capitalized value of debt tax shields minus expected distress costs, both of which scale with book leverage, so two firms with identical operating drivers but different debt/assets carry different EV/EBITDA. Banding on debt/assets inside the 2-digit sector matches the tax-shield and distress component, and ranking on net margin alongside EBITDA and EBIT margins captures the interest-and-tax wedge between operating and bottom-line profit that signals how close a firm is to financial distress.
      prediction: Beats the industry median in at least 3 of 4 years with EV/EBITDA median error below 0.333 and mean error below 0.50.

  (3) g05-04 Sales multiple = margin x lender-revealed durability
      recipe: EV/Sales | screen band ebitda_margin±0.04, band net_debt_to_ebitda±1.5 | rank sales_growth_1y 1, gross_margin 1, rnd_intensity 0.5, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales factors into EBITDA margin times EV/EBITDA; the margin band fixes the first factor, and the second factor depends on how durable that EBITDA is, which lenders reveal through how many turns of EBITDA they are willing to lend (net debt/EBITDA). Jointly banding on both matches the two factors across industries, with growth, gross margin, R&D and size matching remaining capitalization drivers, and fallbacks that relax the leverage screen first because margin matters most.
      prediction: EV/Sales median error below 0.40 with 100% coverage and beats the industry median in all 4 years.

  (4) g05-05 Asset-turnover class with Tobin's-Q drivers
      recipe: EV/Sales | screen band asset_turnover±0.2 | rank ebitda_margin 3, sales_growth_1y 1, rnd_intensity 1 | k=12, median, min_peers=6 | fallback [band asset_turnover±0.4] -> []
      mechanism: EV/Sales factors exactly into EV/Assets times Assets/Sales; a hard band on asset turnover fixes the second factor (the business model's asset intensity, e.g. distributor vs. manufacturer vs. software). The first factor, a Tobin's-Q-like ratio, is driven by the return earned on assets (EBITDA margin given turnover), growth, and unrecorded intangible assets proxied by R&D intensity, so ranking heavily on margin plus growth and R&D matches it.
      prediction: EV/Sales median error below 0.45 with 100% coverage and beats the industry median in all 4 years.

  (5) g05-06 Pre-tax free-cash margin match
      recipe: EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.03 | rank sales_growth_1y 1, rnd_intensity 1, roic 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: What a dollar of sales is worth is the free cash it produces, and before working capital and taxes that is EBITDA margin minus capex intensity; two firms with the same EBITDA margin but different capex needs convert very different shares of sales into distributable cash. Jointly banding EBITDA margin and capex intensity pins down this pre-tax free-cash margin across industries, and ranking on growth, R&D intensity and ROIC matches the growth-dependent capitalization factor and expensed intangible investment.
      prediction: EV/Sales median error below 0.42 with 100% coverage and beats the industry median in all 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

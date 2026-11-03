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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-03] EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
  [g01-04] EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.75, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2, band log_sales±2 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | screen same industry_l3, band net_debt_to_ebitda±2 | rank ebitda_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±2] -> [same industry_l2]
  [g02-04] EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_sales 1, capex_intensity 1, gross_margin 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.08]
  [g02-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=10, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g02-06] EV/Sales | screen same industry_l4 | rank ebitda_margin 2, ebit_margin 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []

PROPOSALS
  (0) ebitda_l3_size_band_growth_roic
      recipe: EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band log_sales±1.5] -> [same industry_l3] -> [same industry_l2]
      mechanism: Discount rates differ systematically with firm size: small firms carry liquidity and risk premia, so they trade at lower EBITDA multiples than large firms in the same industry with the same growth. A hard size band inside the 3-digit industry fixes this risk-premium dimension before ranking on growth, ROIC and reinvestment needs, which are the remaining Gordon-model drivers of value per unit of EBITDA.
      prediction: Median error below the L3/L2 industry median (0.333) in at least 3 of 4 exploration years, with coverage of at least 98%.

  (1) ebitda_l2_growth_regime_band
      recipe: EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
      mechanism: Expected growth is the single largest driver of an EBITDA multiple, and fast and slow growers in one industry are priced as different assets. A hard band on 1-year sales growth inside the 2-digit industry puts every peer in the same growth regime, and ranking on ROIC, capex intensity, net leverage and asset size then matches how cheaply that growth is funded and how risky the claim is.
      prediction: Beats the industry median in at least 3 of 4 years, with median error at or below 0.330.

  (2) ebitda_crosssection_conversion_twins
      recipe: EV/EBITDA | screen band sales_growth_1y±0.1, band net_debt_to_ebitda±1.5 | rank roic 1, ebit_margin 1, ebitda_margin 1, capex_intensity 0.5, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.2] -> []
      mechanism: An EBITDA multiple equals value over a pre-reinvestment cash flow, so it depends on growth, on the return earned on reinvestment, on the share of EBITDA lost to D&A and capex, and on financial risk, none of which require a shared SIC code. Boxing candidates on growth and net leverage across the whole cross-section and ranking on ROIC, both margins (whose gap is the D&A burden), capex intensity and size finds fundamental twins that industry codes can miss.
      prediction: Median error below 0.345 with coverage above 95%; if it does not beat the industry median in at least 2 of 4 years, industry membership carries EV/EBITDA information beyond these fundamentals.

  (3) sales_free_cash_margin_box
      recipe: EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.04 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
      mechanism: EV/Sales scales with the free cash flow each dollar of sales produces, and pre-tax free cash margin is roughly EBITDA margin minus capex intensity. Hard bands on both put every peer at the same cash conversion whatever its SIC code, and ranking on growth, ROIC and size then matches duration, value creation on reinvestment and the risk premium.
      prediction: Median error at or below 0.390 and beats the industry median in 4 of 4 years, with coverage of at least 90%.

  (4) sales_l2_ebit_margin_band
      recipe: EV/Sales | screen same industry_l2, band ebit_margin±0.03 | rank ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06]
      mechanism: EBIT margin is profit after the cost of replacing the asset base (D&A), so it is a better proxy than EBITDA margin for the sustainable operating cash a dollar of sales produces. A hard EBIT-margin band inside the 2-digit industry fixes that term, and ranking on EBITDA margin (which, given EBIT margin, measures D&A intensity), growth and size matches the remaining differences in asset intensity, duration and risk.
      prediction: Beats the industry median in 4 of 4 years, with median error below 0.410.

  (5) sales_size_matched_margin_twins
      recipe: EV/Sales | screen band ebitda_margin±0.03, band log_sales±1.5 | rank sales_growth_1y 1, gross_margin 1, debt_to_assets 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: With the cash margin held fixed, sales multiples still differ by the discount rate, which falls with firm size (liquidity, diversification, access to capital) and rises with balance-sheet distress risk. Hard bands on EBITDA margin and on log sales put peers at the same profitability and risk-premium level, and ranking on growth, gross margin and debt-to-assets matches duration, pricing power and leverage risk.
      prediction: Median error at or below 0.395 and beats the industry median in 4 of 4 years, with coverage of at least 90%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

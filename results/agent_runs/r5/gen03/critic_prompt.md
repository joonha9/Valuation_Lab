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
  [g01-01] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-02] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5
  [g01-03] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-04] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
  [g01-06] EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 1, log_assets 1, roic 1 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g02-01] EV/EBITDA | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, ebitda_margin 0.5 | k=20, median, min_peers=5
  [g02-02] EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
  [g02-03] EV/EBITDA | screen same industry_l3 | rank rnd_intensity 1, asset_turnover 1, gross_margin 1, sales_growth_1y 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, rnd_intensity 1, gross_margin 1 | k=8, harmonic_mean, min_peers=4 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
  [g02-06] EV/Sales | screen same industry_l3 | rank ebit_margin 2, capex_intensity 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []

PROPOSALS
  (0) ebitda_l2_growth_band
      recipe: EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
      mechanism: In a constant-growth DCF, EV/EBITDA is proportional to (1 - reinvestment rate) / (WACC - g), so expected growth enters the denominator and is the most powerful single driver of the multiple. A hard screen holding 1-year sales growth within 10 points of the target's inside the same 2-digit industry fixes the growth term outright, and ranking the survivors on capex intensity and ROIC (how much of EBITDA must be reinvested to sustain that growth), EBITDA margin and size (a discount-rate proxy) lines up the remaining terms.
      prediction: Beats the industry median (L3, fallback L2) on median |ln error| in at least 3 of 4 exploration years, with pooled median below 0.330.

  (1) ebitda_l2_capex_band
      recipe: EV/EBITDA | screen same industry_l2, band capex_intensity±0.03 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band capex_intensity±0.06] -> [same industry_l2]
      mechanism: EBITDA ignores capital spending, so the share of EBITDA that becomes free cash flow falls one-for-one with capex intensity; two firms with the same EBITDA but different capex needs deserve different EV/EBITDA. Screening peers in the same 2-digit industry to within 3 points of the target's capex-to-sales fixes this reinvestment burden as a hard constraint rather than a trade-off in a distance, and ranking on growth, ROIC and size then matches the growth, reinvestment efficiency and discount-rate terms of the DCF multiple.
      prediction: Beats the industry median in at least 3 of 4 exploration years, and its pooled median error is no worse than 0.335.

  (2) ebitda_l3_dcf_triad_leverage
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA depends on three DCF terms: growth, the reinvestment needed to fund it, and the discount rate. Within a 3-digit industry, recent sales growth measures the first, capex intensity the second, and net debt to EBITDA plus asset size proxy the third, since heavily levered and small firms carry higher distress and financing risk and are priced at lower multiples of the same EBITDA. The harmonic mean damps the upward skew from a few richly valued peers.
      prediction: Beats the industry median in at least 3 of 4 exploration years with a lower pooled mean |ln error| than the industry median (below 0.513).

  (3) sales_l2_margin_band
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA, so a tight EBITDA-margin band fixes the margin term, while the shared 2-digit industry adds common cyclicality, customers and risk that move the hidden EV/EBITDA term. Ranking the survivors on growth, capital intensity and size then matches the remaining drivers of EV/EBITDA, and falling back to a cross-industry margin band keeps coverage when the industry is thin; the harmonic mean damps upward skew in sales multiples.
      prediction: Beats the industry median in all 4 exploration years and achieves a pooled median |ln error| below 0.470.

  (4) sales_margin_growth_double_band
      recipe: EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.06, band sales_growth_1y±0.2] -> [band ebitda_margin±0.06] -> []
      mechanism: The two dominant drivers of a sales multiple are profitability (the EBITDA margin term) and growth (which sets the EV/EBITDA term through WACC - g), so hard-screening both, within 3 points of margin and 10 points of growth, guarantees every peer shares the target's two largest value drivers regardless of industry label. Ranking survivors on capex intensity and R&D intensity then matches how much of the margin is consumed by reinvestment or understated by expensed R&D, and size proxies for risk.
      prediction: Beats the industry median in all 4 exploration years with pooled median |ln error| below 0.500.

  (5) sales_ebit_margin_band
      recipe: EV/Sales | screen band ebit_margin±0.04 | rank ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5, log_assets 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebit_margin±0.08] -> []
      mechanism: EBIT margin charges depreciation and so is closer to the cash profit per dollar of sales that a buyer of the whole firm receives than EBITDA margin is; screening on EBIT margin within 4 points and ranking on EBITDA margin pins both the operating margin and the D&A share of sales, i.e. the capital the business consumes. Matching growth, leverage and asset size then aligns the growth and discount-rate terms, so cross-industry peers with the same after-depreciation economics should trade at similar sales multiples.
      prediction: Beats the industry median in all 4 exploration years with pooled median |ln error| below 0.520.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

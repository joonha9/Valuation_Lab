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
  [g03-01] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
  [g03-02] EV/EBITDA | screen same industry_l2, band capex_intensity±0.03 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band capex_intensity±0.06] -> [same industry_l2]
  [g03-03] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-04] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g03-05] EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.06, band sales_growth_1y±0.2] -> [band ebitda_margin±0.06] -> []
  [g03-06] EV/Sales | screen band ebit_margin±0.04 | rank ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5, log_assets 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebit_margin±0.08] -> []

PROPOSALS
  (0) L2 two-sided EBITDA bias (capex and R&D)
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, rnd_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=12, harmonic_mean, min_peers=5 | fallback []
      mechanism: EBITDA is a biased proxy for cash flow in two opposite directions: capital spending is ignored, so capex-heavy firms convert less EBITDA into free cash flow and deserve lower EV/EBITDA, while R&D is expensed, so R&D-heavy firms have depressed EBITDA relative to their economic earnings and trade at higher EV/EBITDA. Within the same 2-digit industry, matching peers on both capex intensity and R&D intensity, plus growth and EBITDA margin, lines up the full gap between reported EBITDA and economic cash generation; the harmonic mean damps the upward skew of a few richly priced peers.
      prediction: Beats the industry-median EV/EBITDA baseline (0.333) in at least 3 of 4 exploration years with an overall median absolute log error at or below 0.330.

  (1) L2 size-banded growth and reinvestment
      recipe: EV/EBITDA | screen same industry_l2, band log_sales±1 | rank sales_growth_1y 1, capex_intensity 1, ebit_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band log_sales±2] -> [same industry_l2]
      mechanism: Small firms carry higher discount rates (illiquidity, higher failure risk, less diversified revenue), so the WACC term in EV/EBITDA = (1 - reinvestment share) / (WACC - g) varies systematically with scale. Hard-screening peers in the same 2-digit industry to within one log unit of the target's sales fixes the discount-rate term as a constraint rather than a trade-off, and ranking the survivors on growth, capex intensity and EBIT margin matches the growth and reinvestment terms.
      prediction: Beats the industry-median EV/EBITDA baseline in at least 3 of 4 exploration years, with the largest gains among the smallest-size firms.

  (2) L2 leverage-banded distress match
      recipe: EV/EBITDA | screen same industry_l2, band net_debt_to_ebitda±1.5 | rank capex_intensity 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±3] -> [same industry_l2]
      mechanism: Enterprise value is theoretically independent of capital structure, but in practice highly levered firms bear expected distress and financing-constraint costs that lower the value placed on each dollar of EBITDA, while lightly levered firms do not. Screening peers in the same 2-digit industry to within 1.5 turns of the target's net debt to EBITDA holds this distress discount fixed, and ranking on capex intensity, growth and ROIC then aligns the reinvestment and growth-efficiency terms of the DCF multiple.
      prediction: Beats the industry-median EV/EBITDA baseline in at least 3 of 4 exploration years, with mean absolute log error below 0.505.

  (3) L3 margin band with nested widening
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.04 | rank sales_growth_1y 1, rnd_intensity 1, gross_margin 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA; a tight EBITDA-margin band fixes the margin term, and a 3-digit industry shares technology, customers and cyclicality that drive the hidden EV/EBITDA term more closely than a 2-digit group. Ranking survivors on growth, R&D intensity and gross margin matches the growth term and the portion of the margin suppressed by expensed R&D, and the fallback ladder widens from narrow industry to broad industry to cross-industry margin bands only when peers are too few.
      prediction: Beats the industry-median EV/Sales baseline (0.603) in all 4 exploration years with an overall median absolute log error below 0.45.

  (4) Pre-tax cash margin double band
      recipe: EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.03 | rank sales_growth_1y 1, rnd_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.06, band capex_intensity±0.06] -> [band ebitda_margin±0.06] -> []
      mechanism: A buyer of the whole firm is paid roughly EBITDA minus capital spending (pre-tax operating cash flow before working capital) per dollar of sales, so two firms with the same EBITDA margin but different capex intensity deliver different cash per dollar of sales. Hard-screening both EBITDA margin and capex intensity pins this pre-tax cash margin across industries, and ranking survivors on growth, R&D intensity and size aligns the growth, hidden-investment and discount-rate terms.
      prediction: Beats the industry-median EV/Sales baseline in all 4 exploration years and beats the industry-free margin-band recipe g02-05 (median 0.448).

  (5) L2 margin band, value-of-growth match
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: Growth adds value only when the return on new capital exceeds the cost of capital, so a sales multiple depends on growth and ROIC jointly rather than on growth alone. Within the same 2-digit industry and a tight EBITDA-margin band (which fixes the margin term of EV/Sales), ranking peers on growth and ROIC matches the value created by growth, and net debt to EBITDA matches financial risk; the harmonic mean damps upward skew in sales multiples.
      prediction: Beats the industry-median EV/Sales baseline in all 4 exploration years with an overall median absolute log error below 0.45.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

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
  [g04-01] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, rnd_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=12, harmonic_mean, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l2, band log_sales±1 | rank sales_growth_1y 1, capex_intensity 1, ebit_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band log_sales±2] -> [same industry_l2]
  [g04-03] EV/EBITDA | screen same industry_l2, band net_debt_to_ebitda±1.5 | rank capex_intensity 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±3] -> [same industry_l2]
  [g04-04] EV/Sales | screen same industry_l3, band ebitda_margin±0.04 | rank sales_growth_1y 1, rnd_intensity 1, gross_margin 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
  [g04-05] EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.03 | rank sales_growth_1y 1, rnd_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.06, band capex_intensity±0.06] -> [band ebitda_margin±0.06] -> []
  [g04-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []

PROPOSALS
  (0) ebitda_l4_ladder_capex_growth
      recipe: EV/EBITDA | screen same industry_l4 | rank capex_intensity 1.5, sales_growth_1y 1, ebitda_margin 1 | k=8, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: Firms in the same 4-digit SIC code share the same product, customers, cost structure and regulatory exposure, so their discount rates and long-run growth prospects (the WACC - g denominator of EV/EBITDA) are closer than in a 2- or 3-digit group. Inside that narrow group, ranking on capex intensity, growth and EBITDA margin aligns the share of EBITDA that must be reinvested, and the ladder widens to 3-digit, then 2-digit, then all firms only when the narrow group is too thin to give a stable median.
      prediction: Median error below 0.330 and beats the industry median in at least 3 of 4 exploration years with coverage above 99%.

  (1) ebitda_l2_marginband_moat
      recipe: EV/EBITDA | screen same industry_l2, band ebitda_margin±0.05 | rank capex_intensity 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.1] -> [same industry_l2]
      mechanism: A persistently high EBITDA margin within an industry signals pricing power or a cost advantage that competition erodes slowly, so high-margin firms earn excess returns for longer and the market capitalizes each dollar of their EBITDA at a higher multiple than low-margin rivals whose profits are expected to mean-revert. Hard-screening peers in the same 2-digit industry to within 5 points of the target's EBITDA margin holds this competitive-durability term fixed, and ranking on capex intensity, growth and size matches the reinvestment, growth and discount-rate terms.
      prediction: Beats the industry median in at least 3 of 4 years, with median error at or below 0.330 and coverage above 97%.

  (2) ebitda_l2_maintenance_vs_growth_capex
      recipe: EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, capex_intensity 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: The gap between EBITDA margin and EBIT margin is depreciation per dollar of sales, a proxy for maintenance capital spending, while capex intensity is total current investment; capex well above depreciation means the firm is spending to grow, which markets reward, whereas capex near depreciation is pure upkeep that only drains EBITDA. Ranking peers in the same 2-digit industry jointly on EBITDA margin, EBIT margin and capex intensity separates maintenance from growth investment, and adding realized sales growth checks whether that growth spending is paying off, so matched peers share both the cash conversion and the growth term of EV/EBITDA.
      prediction: Median error below 0.330 and beats the industry median in all 4 exploration years.

  (3) sales_l3_margin_growth_double_band
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank rnd_intensity 1, gross_margin 0.5, log_sales 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l3, band ebitda_margin±0.04] -> [same industry_l2, band ebitda_margin±0.04, band sales_growth_1y±0.15] -> [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA, and EV/EBITDA is driven mainly by growth relative to the discount rate; hard-banding both EBITDA margin (within 4 points) and 1-year growth (within 15 points) inside a 3-digit industry fixes the two largest value drivers while the shared industry fixes cyclicality and risk. Ranking survivors on R&D intensity, gross margin and size matches the margin suppressed by expensed R&D and the remaining discount-rate gap, and a ladder drops the growth band first, then the industry, so coverage is kept without loosening the margin term.
      prediction: Median error below 0.410 (better than the best archived EV/Sales recipe) and beats the industry median in all 4 years.

  (4) sales_l4_ladder_marginband_capex
      recipe: EV/Sales | screen same industry_l4, band ebitda_margin±0.05 | rank sales_growth_1y 1, capex_intensity 1, rnd_intensity 0.5 | k=5, harmonic_mean, min_peers=3 | fallback [same industry_l3, band ebitda_margin±0.05] -> [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: Within a 4-digit SIC code firms sell close substitutes, so the hidden EV/EBITDA term of EV/Sales (driven by shared demand outlook, cyclicality and risk) is most nearly common there, while a 5-point EBITDA-margin band fixes the margin term. Ranking on growth, capex intensity and R&D intensity matches how much of the margin is reinvested or understated by expensed R&D, and the ladder steps from 4-digit to 3-digit to 2-digit industry and then to cross-industry margin bands only when the narrower group cannot supply peers.
      prediction: Median error at or below 0.420 and beats the industry median in all 4 years with full coverage.

  (5) sales_l2_ebitband_da_share
      recipe: EV/Sales | screen same industry_l2, band ebit_margin±0.04 | rank ebitda_margin 1, sales_growth_1y 1, rnd_intensity 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebit_margin±0.04] -> [band ebit_margin±0.08] -> []
      mechanism: EBIT margin charges depreciation and so measures the operating profit per dollar of sales that survives the cost of maintaining the asset base, which is closer to the cash a whole-firm buyer receives than EBITDA margin; banding EBIT margin within 4 points inside the same 2-digit industry fixes this after-depreciation margin and the industry's shared risk. Ranking survivors on EBITDA margin (which, given the band, pins depreciation's share of sales), growth and R&D intensity matches capital consumption, the growth term and margin hidden by expensed R&D.
      prediction: Beats the industry median in all 4 years with median error below 0.440.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

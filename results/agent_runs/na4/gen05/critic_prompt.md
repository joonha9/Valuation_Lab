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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 0.5, roic 1, rnd_intensity 1, capex_intensity 1, debt_to_assets 0.5, log_sales 0.5 | k=20, harmonic_mean, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, rnd_intensity 0.5 | k=15, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebit_margin 2, asset_turnover 1, sales_growth_1y 1, gross_margin 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback []
  [g02-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | rank sales_growth_1y 1, roic 1, ebitda_margin 0.7, capex_intensity 0.7, net_debt_to_ebitda 0.5, log_sales 0.5 | k=15, median, min_peers=5
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.3 | k=10, median, min_peers=5 | fallback []
  [g02-05] EV/Sales | screen band ebitda_margin±0.04, same industry_l2 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g02-06] EV/Sales | screen same industry_l3 | rank ebit_margin 1.5, asset_turnover 0.7, roic 0.7, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-02] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback []
  [g03-03] EV/EBITDA | rank log_sales 1, ebitda_margin 1, roic 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=20, trimmed_mean, min_peers=3
  [g03-04] EV/Sales | screen same industry_l3 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g03-05] EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g03-06] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, asset_turnover 1, capex_intensity 0.5, sales_growth_1y 1, debt_to_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
  [g04-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g04-02] EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g04-03] EV/EBITDA | rank gross_margin 1, capex_intensity 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=3
  [g04-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g04-05] EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1 | k=12, median, min_peers=3
  [g04-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.08 | rank ebitda_margin 2, roic 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.08] -> [band ebitda_margin±0.05] -> []

PROPOSALS
  (0) EBITDA_L2_growth_margin_k10
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, ebitda_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and falls with risk, while the reinvestment needed for growth depends on business model. Matching broad-industry (2-digit SIC) peers on recent growth and EBITDA margin captures growth and profitability-quality differences that a plain industry median ignores, while the wider industry pool leaves enough candidates to choose close matches.
      prediction: Median |ln(V_est/V)| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years, with a pooled median at or below 0.32.

  (1) EBITDA_L3_roic_growth_leverage
      recipe: EV/EBITDA | screen same industry_l3 | rank roic 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Value per dollar of EBITDA depends on how much growth the firm achieves per dollar reinvested (ROIC) and on how fast it is growing; leverage changes risk and the debt tax shield. Close-industry peers with similar ROIC, growth and net leverage should have similar value-driver profiles and so similar EV/EBITDA.
      prediction: Pooled median error below 0.333 and beats the Bhojraj-Lee warranted multiple (0.357) in all 4 exploration years.

  (2) EBITDA_crossindustry_fundamentals_harmonic
      recipe: EV/EBITDA | rank capex_intensity 1, gross_margin 1, roic 1, sales_growth_1y 1 | k=15, harmonic_mean, min_peers=3
      mechanism: Firms with the same capital intensity, gross margin, ROIC and growth share the same economics of converting EBITDA into free cash flow, whatever their SIC code; capex intensity matters most because EBITDA leaves out reinvestment. The harmonic mean is the right average for price ratios and damps the effect of peers with unusually high multiples.
      prediction: Pooled median error within 0.02 of the industry-median baseline (at or below 0.35) and a lower mean error than the industry median (below 0.513).

  (3) Sales_L2_margin_dominant
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so differences in profitability drive most of the spread in sales multiples within an industry. Ranking broad-industry peers mainly on EBITDA margin, then on growth and gross margin, removes the largest source of error in a plain industry-median EV/Sales.
      prediction: Pooled median error below 0.50, beating the L3 industry median (0.603) by at least 0.08 in every exploration year.

  (4) Sales_margin_band_L2_growth_harmonic
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: A hard band on EBITDA margin ensures every peer turns sales into cash flow at a similar rate, which is the main condition for sales multiples to be comparable. Within that band, same-industry peers with similar growth and size share risk and growth expectations, and the harmonic mean limits the pull from high-multiple outliers.
      prediction: Pooled median error below 0.52 and beats the L3 industry median in at least 3 of 4 exploration years.

  (5) Sales_crossindustry_profitability_twins
      recipe: EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=15, median, min_peers=3
      mechanism: Across the whole market, firms with matching EBITDA margin, gross margin, growth and asset turnover have similar cash-flow conversion and capital needs per dollar of sales, so their EV/Sales should line up even across SIC codes. Asset turnover separates capital-light from capital-heavy models that look alike on margin alone.
      prediction: Pooled median error below 0.55, beating the Bhojraj-Lee warranted EV/Sales multiple (0.674) in all 4 exploration years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

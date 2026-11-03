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
  [g02-01] EV/Sales | screen band ebitda_margin±0.04 | rank gross_margin 2, sales_growth_1y 1, rnd_intensity 1 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
  [g02-02] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 2, asset_turnover 2, sales_growth_1y 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
  [g02-03] EV/EBITDA | rank sales_growth_1y 2, roic 2, capex_intensity 1, net_debt_to_ebitda 1 | k=20, median, min_peers=3
  [g02-04] EV/EBITDA | screen same industry_l3, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band sales_growth_1y±0.1] -> [same industry_l2] -> []
  [g02-05] EV/EBITDA | screen same industry_l2 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback []
  [g02-06] EV/Sales | screen same industry_l2, band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank log_sales 1, capex_intensity 1 | k=6, median, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04, band sales_growth_1y±0.15] -> []
  [g03-01] EV/EBITDA | screen same industry_l2 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 2, roic 1, net_debt_to_ebitda 1 | k=12, median, min_peers=5 | fallback []
  [g03-02] EV/EBITDA | screen same industry_l3 | rank rnd_intensity 2, ebit_margin 1, ebitda_margin 1, capex_intensity 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g03-03] EV/EBITDA | screen same industry_l2, band gross_margin±0.1 | rank rnd_intensity 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
  [g03-04] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
  [g03-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank capex_intensity 2, sales_growth_1y 2, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
  [g03-06] EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank gross_margin 1, rnd_intensity 1, asset_turnover 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []

PROPOSALS
  (0) ebitda_growth_roic_box_crosssector
      recipe: EV/EBITDA | screen band sales_growth_1y±0.1, band roic±0.05 | rank rnd_intensity 1, capex_intensity 1, gross_margin 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.1] -> [same industry_l2] -> []
      mechanism: In a steady-state value-driver model, EV/EBITDA is set by growth and by the return earned on the reinvestment that funds it (ROIC), and those two inputs mean the same thing in any sector. A hard two-way box on 1-year sales growth and ROIC, drawn across all sectors, finds peers with the same growth and return from a much larger pool than any SIC group. Inside the box, R&D intensity, capex intensity and gross margin describe how much of reported EBITDA is real free cash flow (expensed intangibles versus capital spending), so these replace the industry label.
      prediction: Median error below 0.330 and beats the L3/L2 industry median in at least 3 of 4 exploration years with coverage above 95%.

  (1) ebitda_l2_rnd_band
      recipe: EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank sales_growth_1y 1, roic 1, capex_intensity 1 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Because US GAAP expenses R&D, EBITDA understates economic earnings by roughly the R&D add-back, so firms with different R&D intensity in the same sector have mechanically different EV/EBITDA. Turning R&D intensity from a soft ranking weight into a hard band within the 2-digit sector removes this accounting distortion outright for every peer. Ranking the survivors on growth, ROIC and capex intensity then matches the growth, reinvestment efficiency and cash conversion of the remaining EBITDA.
      prediction: Beats the industry median in at least 3 of 4 years, with median error at or below 0.325.

  (2) ebitda_business_model_box_crosssector
      recipe: EV/EBITDA | screen band gross_margin±0.08, band rnd_intensity±0.02 | rank sales_growth_1y 2, roic 1, capex_intensity 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band gross_margin±0.1] -> [same industry_l2] -> []
      mechanism: Gross margin and R&D intensity together describe the business model (commodity processing versus branded or IP-driven) and how far expensed intangible investment pushes EBITDA below economic earnings. A hard box on both across all sectors gives peers whose EBITDA has the same accounting meaning without relying on SIC codes, which often lump very different business models together. Within the box, growth (weighted most), ROIC and capex intensity rank peers on the Gordon-style drivers of the multiple.
      prediction: Beats the industry median in at least 3 of 4 years; if SIC carries information beyond business-model traits, it will fall short of the L2-screened R&D-band recipe.

  (3) sales_fcf_margin_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band capex_intensity±0.03 | rank sales_growth_1y 2, roic 1, gross_margin 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: EV/Sales is the present value of future free-cash-flow margins, and FCF margin is roughly EBITDA margin less capex intensity. A hard box on both EBITDA margin and capex intensity across all sectors therefore fixes the FCF margin itself rather than only its gross component. Peers are then ranked on growth (weighted most), ROIC (how long growth creates value) and gross margin (how durable the margin is).
      prediction: Median error below 0.390 and beats the industry median in all 4 exploration years.

  (4) sales_cost_structure_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.1 | rank sales_growth_1y 2, rnd_intensity 1, asset_turnover 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: Two firms with the same EBITDA margin can get there very differently: a high gross margin with heavy SG&A and R&D (spending that is discretionary and partly investment) or a thin gross margin with little overhead (a commodity cost structure). Investors capitalise the first kind of margin at a higher sales multiple because operating leverage and the investment buried in opex point to more future margin. A hard box on EBITDA margin and gross margin fixes both the profit level and how it is made, and growth, R&D intensity and asset turnover rank what is left.
      prediction: Beats the industry median in all 4 years with median error below 0.400.

  (5) sales_ebit_margin_growth_box
      recipe: EV/Sales | screen band ebit_margin±0.03, band sales_growth_1y±0.1 | rank roic 2, rnd_intensity 1, capex_intensity 1 | k=10, median, min_peers=5 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06] -> []
      mechanism: EBIT margin subtracts depreciation, a rough proxy for the maintenance capex needed to keep sales going, so it is closer than EBITDA margin to the sustainable after-tax operating margin that a DCF capitalises into EV/Sales. A hard box on EBIT margin and 1-year growth across all sectors matches the two first-order drivers of the sales multiple on this cleaner profit measure. Ranking on ROIC (weighted most), R&D intensity and capex intensity then matches how long growth creates value and how much profit is held back by expensed or capital investment.
      prediction: Beats the industry median in all 4 years; median error within 0.02 of the EBITDA-margin/growth box, with a lower mean error.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

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

PROPOSALS
  (0) g03-01 intangible-adjusted Gordon peers (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 2, roic 1, net_debt_to_ebitda 1 | k=12, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA has two separate sources of spread. One is the fundamental Gordon drivers: growth, reinvestment efficiency (ROIC) and risk (leverage). The other is the accounting distortion from expensing R&D, which pushes down the EBITDA of intangible-heavy firms and so raises their multiple. Matching on both sets at once within a 2-digit sector should line up the economic value drivers and the measurement bias in the denominator together, rather than only one of them.
      prediction: Beats the industry median (L3, fallback L2) in at least 3 of 4 exploration years, with median abs log error at or below 0.325.

  (1) g03-02 EBITDA-quality peers: D&A and R&D wedges (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l3 | rank rnd_intensity 2, ebit_margin 1, ebitda_margin 1, capex_intensity 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA leaves out two real economic costs that vary across firms: depreciation of past capital spending (the gap between EBITDA margin and EBIT margin, plus capex intensity) and R&D that is expensed rather than capitalised. Firms in the same 3-digit industry whose EBITDA carries the same D&A burden and the same R&D add-back should turn EBITDA into free cash flow at the same rate, and so trade at similar multiples. A trimmed mean keeps information from several peers while dropping extreme multiples.
      prediction: Beats the industry median in at least 3 of 4 exploration years, with a mean abs log error below 0.505.

  (2) g03-03 gross-margin business-model band (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2, band gross_margin±0.1 | rank rnd_intensity 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Gross margin shows the business model (commodity or processing versus branded or IP-driven). It also shows how much spending sits below gross profit in SG&A and R&D, which are expensed intangible investments that push EBITDA below economic earnings. A hard gross-margin band inside the 2-digit sector guarantees that every peer shares this cost structure. Ranking on R&D intensity, growth and ROIC then matches the remaining value drivers.
      prediction: Beats the industry median in at least 3 of 4 exploration years, with median abs log error at or below 0.330.

  (3) g03-04 margin band plus intangible intensity (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: EV/Sales is EV/EBITDA times EBITDA margin. A hard EBITDA-margin band within the 2-digit sector fixes the margin term. The EV/EBITDA term is then driven mostly by the R&D-expensing distortion and by growth and ROIC. Ranking on R&D intensity and gross margin (the intangible-heavy business model) together with growth and ROIC should therefore line up the second term, which the margin band alone leaves free.
      prediction: Beats the industry median in all 4 exploration years, with median abs log error at or below 0.400.

  (4) g03-05 free-cash-flow margin peers (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank capex_intensity 2, sales_growth_1y 2, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: In a DCF, EV/Sales equals the present value of future free-cash-flow margins. FCF margin is roughly EBITDA margin less capex intensity (after tax), growing at the firm's growth rate. A hard EBITDA-margin band, then ranking on capex intensity and sales growth, matches peers on FCF margin and its growth rate directly. ROIC captures how long that growth can create value.
      prediction: Beats the industry median in all 4 exploration years, with median abs log error at or below 0.405.

  (5) g03-06 margin-and-growth box across sectors (EV/Sales)
      recipe: EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank gross_margin 1, rnd_intensity 1, asset_turnover 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: Margin and growth are the two first-order drivers of the sales multiple. A tight two-way box on EBITDA margin and 1-year growth, applied across all sectors, gives peers with the same profitability and growth path from a much larger pool than any single SIC group. Within the box, gross margin, R&D intensity and asset turnover describe the business model and capital intensity directly, in place of an industry label.
      prediction: Beats the industry median in all 4 exploration years, with median abs log error at or below 0.410.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

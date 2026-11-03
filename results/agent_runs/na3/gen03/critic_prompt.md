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
  [g01-01] EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-02] EV/EBITDA | screen same industry_l3 | rank log_assets 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g01-03] EV/EBITDA | rank gross_margin 1, ebitda_margin 1, capex_intensity 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=3
  [g01-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
  [g01-05] EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
  [g01-06] EV/Sales | screen same industry_l3 | rank ebitda_margin 2, roic 1, log_sales 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-03] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g02-04] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.5 | k=10, median, min_peers=6 | fallback []
  [g02-05] EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, roic 1, log_sales 0.5 | k=15, median, min_peers=3
  [g02-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03] -> [same industry_l2]

PROPOSALS
  (0) L2 growth-profitability nearest neighbors (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: Within a broad industry, EV/EBITDA is set mainly by expected growth and by how much value each unit of EBITDA creates (return on capital), with size proxying for risk. Picking the nearest industry peers on 1-year growth, ROIC, EBITDA margin and size should match those drivers better than a plain industry median, and the harmonic mean limits the pull of extreme high-multiple peers.
      prediction: Median |ln error| below the L3 industry median's 0.333 in at least 3 of 4 exploration years, with a pooled median of 0.32 or less.

  (1) L3 size-and-growth peers with cascade (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share technology, cyclicality and capital needs, while similar size and growth capture differences in risk and in the expected path of cash flows. Keeping only the closest peers on size and growth inside the narrow industry, and widening to L2 and then the whole market when peers are scarce, should cut noise from mismatched firms of very different size.
      prediction: Pooled median |ln error| at or below 0.325, beating the L3 industry median in at least 3 of 4 years.

  (2) Cash-conversion peers (EV/EBITDA)
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, ebit_margin 1, sales_growth_1y 0.75, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=5 | fallback []
      mechanism: EBITDA overstates distributable cash for capital-heavy firms, so at equal growth investors pay less per dollar of EBITDA when capex and depreciation eat much of it. Matching on capex intensity and EBIT margin, which together capture D&A drag, along with growth and leverage inside the 2-digit industry, should line up peers that convert EBITDA into free cash flow in a similar way.
      prediction: Beats the L3 industry median's median error in at least 3 of 4 years, with a lower mean error than the Bhojraj-Lee regression (0.492).

  (3) Margin-matched industry peers (EV/Sales)
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so differences in margin within an industry explain most of the spread in sales multiples. Ranking 2-digit industry peers mostly on EBITDA margin, with gross margin and growth as secondary drivers, should take out the main source of error in the plain industry median.
      prediction: Pooled median |ln error| below 0.50 (versus 0.603 for the industry median), beating it in all 4 exploration years.

  (4) Margin-band screen with growth ranking (EV/Sales)
      recipe: EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 1.5, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
      mechanism: A hard band on EBITDA margin makes sure every peer earns a similar amount of profit per dollar of sales, which is the main link between EV/Sales and value. Inside that band, the same industry and similar growth and size line up the remaining drivers: expected growth and risk.
      prediction: Beats the EV/Sales industry median in at least 3 of 4 years, with a pooled median error below 0.52.

  (5) Cross-industry fundamental twins (EV/Sales)
      recipe: EV/Sales | rank ebitda_margin 3, sales_growth_1y 1, capex_intensity 0.75, asset_turnover 0.75, log_sales 0.5 | k=20, median, min_peers=3
      mechanism: Firms with the same margin, growth, capital intensity and asset turnover should earn similar value per dollar of sales whatever their SIC code, because those inputs set free cash flow per dollar of sales and how fast it grows. Dropping the industry screen allows closer fundamental matches for firms in thin or mixed industries.
      prediction: Pooled median |ln error| below the EV/Sales industry median (0.603) and below the Bhojraj-Lee regression (0.674), beating the industry median in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

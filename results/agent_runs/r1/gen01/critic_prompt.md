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
  (none)

PROPOSALS
  (0) ebitda_l3_growth_return_leverage
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a Gordon-style valuation, EV/EBITDA rises with expected growth and with how efficiently growth is funded (ROIC), and falls with financial risk. Industry peers share the same business risk and accounting conventions, so ranking within the industry on growth, ROIC and net leverage should isolate peers with the same fundamental multiple drivers, closer than the industry as a whole.
      prediction: Median |ln error| below the L3 industry-median baseline (0.333) in at least 3 of the 4 exploration years, with the pooled median at or below 0.32.

  (1) sales_l2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in profitability. Within a broad 2-digit industry, picking peers with the closest EBITDA and gross margins (plus growth) cancels out the margin term that a plain industry median ignores.
      prediction: Pooled median |ln error| at least 0.08 below the L3 industry-median EV/Sales baseline (0.603), i.e. at or below 0.52, and better in all 4 years.

  (2) sales_crossindustry_profitability_twins
      recipe: EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
      mechanism: Once margins, growth and capital intensity are matched, firms produce similar free cash flow per dollar of sales, whatever their SIC code. Searching the whole cross-section for profitability twins gives a larger and closer-matched peer set than industry codes, which often group businesses with very different economics.
      prediction: Beats the L3 industry-median EV/Sales baseline in at least 3 of 4 years, with a pooled median at or below 0.55.

  (3) ebitda_l2_size_band_reinvestment
      recipe: EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA overstates distributable cash flow for capital-heavy firms, because capex absorbs part of it. So at equal growth, firms with higher capex intensity should trade at lower EBITDA multiples. Size, in turn, proxies for risk and liquidity premia. Matching on reinvestment needs, growth and margin within a 2-digit industry and a size band should capture both effects.
      prediction: Median |ln error| at or below 0.33, beating the warranted-multiple regression (0.357) in all 4 years and the L3 industry median in at least 2 of 4.

  (4) ebitda_l4_cascade_growth_roic
      recipe: EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Narrow 4-digit SIC peers share product markets, customers and cyclicality, so they face the same discount rate and the same long-run growth outlook. Within that narrow group, a small ranking on growth and ROIC refines the match, and the cascade to L3 and L2 keeps coverage when narrow industries are thin.
      prediction: Beats the L3 industry median (0.333) in at least 3 of 4 years, and the gain is concentrated among firms that end up with L4 peers.

  (5) sales_l3_margin_band_growth_size
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
      mechanism: A hard band on EBITDA margin makes sure every peer converts sales into cash flow at a similar rate, which is the main driver of EV/Sales. Within that band and the 3-digit industry, ranking on growth and size captures the remaining differences in duration and risk. The fallbacks relax the industry screen before they relax the margin match.
      prediction: Pooled median |ln error| at or below 0.53, beating the L3 industry-median EV/Sales baseline in all 4 exploration years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

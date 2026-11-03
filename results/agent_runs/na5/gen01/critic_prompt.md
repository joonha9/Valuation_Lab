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
  (0) EBITDA_L2_growth_roic_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: Within a broad industry, an EV/EBITDA multiple capitalizes cash flow, so it should differ mainly by expected growth and by the return earned on reinvestment (higher ROIC means growth creates more value), with size proxying for risk. Picking the nearest peers on these value drivers inside a 2-digit SIC group keeps business risk comparable while matching the drivers of the multiple, and the harmonic mean limits the pull of peers with very high multiples.
      prediction: Median |ln error| below the L3/L2 industry median baseline (0.333) in at least 3 of 4 exploration years, with a pooled median of 0.32 or lower.

  (1) EBITDA_L3_leverage_capex_median
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.5, sales_growth_1y 1, log_assets 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry that also look alike on leverage, reinvestment needs and growth should share an EV/EBITDA multiple. Capex intensity separates EBITDA that turns into free cash flow from EBITDA that must be reinvested, and net debt/EBITDA captures financial risk and the cost of capital. A small peer set with a median aggregate stays robust to outliers.
      prediction: Pooled median |ln error| at or below 0.33, and lower than the Bhojraj-Lee warranted-multiple peers baseline (0.380) in all 4 exploration years.

  (2) EBITDA_crossindustry_fundamentals
      recipe: EV/EBITDA | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, capex_intensity 0.5, log_assets 0.5 | k=20, harmonic_mean, min_peers=3
      mechanism: If the multiple is set by fundamentals (growth, profitability, reinvestment, size) rather than by industry labels, then the nearest peers on those fundamentals across the whole cross-section should value a firm about as well as industry peers, and better for firms with few or mismatched industry peers. A large k with a harmonic mean averages away idiosyncratic noise.
      prediction: Pooled median |ln error| within 0.02 of the industry median baseline (no worse than 0.353), and better than the warranted-multiple regression (0.357) in at least 3 of 4 years.

  (3) Sales_L2_margin_growth_harmonic
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=5 | fallback []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so firms with different margins cannot share a sales multiple; matching on EBITDA margin (most weight), gross margin and growth inside a 2-digit industry gets rid of the main source of EV/Sales dispersion. The harmonic mean reduces the effect of a few richly valued peers.
      prediction: Pooled median |ln error| below 0.52, beating the industry median baseline (0.603) in all 4 exploration years.

  (4) Sales_marginband_crossindustry
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: A sales multiple is mostly a capitalized margin, so a hard band on EBITDA margin across all industries makes peers economically comparable even when SIC codes differ. Ranking the in-band firms on gross margin, growth and size then refines for pricing power, expected growth and risk; the median protects against outliers.
      prediction: Pooled median |ln error| below 0.55, beating the industry median baseline (0.603) in at least 3 of 4 exploration years.

  (5) Sales_L3_margin_trimmed
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 1.5, sales_growth_1y 0.5, asset_turnover 0.5 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Narrow-industry peers share product markets and cost structures, and within that set the EBITDA margin and growth explain most of the remaining differences in EV/Sales. A small, closely matched peer set with a trimmed mean keeps the precision of near neighbours while dropping extreme peers.
      prediction: Pooled median |ln error| below 0.55 and lower than the warranted-multiple regression baseline (0.674) in all 4 exploration years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

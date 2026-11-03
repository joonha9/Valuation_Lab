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
  (0) ebitda_l3_reinvestment_matched
      recipe: EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA is a capitalized cash-flow multiple, so firms in the same 3-digit industry share risk, but within an industry the multiple still varies with growth, the return earned on reinvestment (ROIC), and how much of EBITDA is consumed by capex. Matching peers on capex intensity, growth and ROIC inside the industry should pick firms whose EBITDA converts to free cash flow and grows at similar rates, so they should carry similar multiples.
      prediction: Median |ln(V_est/V)| below the L3/L2 industry median baseline (0.333) and beats it in at least 3 of 4 exploration years.

  (1) ebitda_l4_size_harmonic
      recipe: EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The narrowest industry definition gives peers with the most similar products, customers and cyclicality, and similar size proxies for similar business risk and liquidity. The harmonic mean of multiples equals averaging earnings yields, which is less dominated by a few peers with temporarily depressed EBITDA and very high multiples, a known source of upward bias with the arithmetic mean.
      prediction: Beats the L3/L2 industry median baseline on median error in at least 3 of 4 years, with lower mean error than 0.513.

  (2) ebitda_cross_industry_fundamentals
      recipe: EV/EBITDA | rank roic 1, sales_growth_1y 1, capex_intensity 1, rnd_intensity 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=20, trimmed_mean, min_peers=3
      mechanism: Valuation theory says EV/EBITDA depends on growth, profitability of reinvestment, reinvestment needs, intangible investment and leverage-related risk, not on the SIC code itself. Picking the nearest firms across all industries on these drivers is a nonparametric version of the warranted-multiple approach that avoids imposing a linear functional form, and a trimmed mean guards against outlier peers.
      prediction: Beats the Bhojraj-Lee warranted-multiple peers baseline (0.380) in at least 3 of 4 years, but does not beat the L3/L2 industry median overall.

  (3) sales_l2_margin_matched
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales is approximately EBITDA margin times EV/EBITDA, so margin differences explain most of the spread in sales multiples even inside an industry. Restricting to the 2-digit sector keeps risk and cyclicality broadly similar while giving enough candidates to find peers with nearly the same EBITDA and gross margin and similar growth.
      prediction: Median error below the L3/L2 industry median EV/Sales baseline (0.603) in all 4 exploration years.

  (4) sales_margin_band_cross_industry
      recipe: EV/Sales | screen band ebitda_margin±0.03 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band ebitda_margin±0.06]
      mechanism: Because a dollar of sales is worth roughly the cash margin it produces capitalized at a growth-adjusted rate, firms with nearly the same EBITDA margin should have similar EV/Sales regardless of industry. A hard margin band enforces this, and ranking within the band on growth, gross margin and capex intensity matches the remaining drivers (growth and how much of the margin is eaten by reinvestment).
      prediction: Beats the L3/L2 industry median EV/Sales baseline on median error in at least 3 of 4 years.

  (5) sales_l3_margin_band_harmonic
      recipe: EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, rnd_intensity 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]
      mechanism: Combining the same 3-digit industry (shared risk and business model) with a margin band (shared cash conversion of sales) targets the two main determinants of the sales multiple at once. Within that set, gross margin, growth and R&D intensity capture pricing power and intangible investment, and the harmonic mean limits the influence of high-multiple peers.
      prediction: Median error below 0.55 and lower than the L3/L2 industry median EV/Sales baseline in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

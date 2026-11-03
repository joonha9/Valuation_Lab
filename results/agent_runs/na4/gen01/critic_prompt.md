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
  (0) EBITDA_L2_growth_reinvestment_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_sales 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: An EV/EBITDA multiple capitalizes cash flow, so it should rise with expected growth and fall with the reinvestment needed to sustain it (capex absorbs EBITDA that never reaches investors). Peers from the same broad industry that match on growth, capex intensity and return on capital should share discount-rate and payout characteristics, and the harmonic mean limits the upward bias from high-multiple outliers.
      prediction: Median |ln error| below the L3 industry-median baseline (0.333) in at least 3 of 4 exploration years, and pooled median below 0.320.

  (1) EBITDA_L3_leverage_size_median
      recipe: EV/EBITDA | screen same industry_l3 | rank log_sales 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a narrow industry, residual EV/EBITDA dispersion is driven by size (liquidity and risk) and by leverage, since highly levered firms carry more distress risk and lower implied multiples on enterprise value. Ranking same-industry peers on size, net leverage and growth targets these remaining drivers while keeping the industry's common business risk.
      prediction: Pooled median |ln error| at or below 0.325, beating the L3 industry median in at least 3 of 4 years.

  (2) EBITDA_crossindustry_fundamentals_harmonic
      recipe: EV/EBITDA | rank sales_growth_1y 1, ebitda_margin 0.5, roic 1, rnd_intensity 1, capex_intensity 1, debt_to_assets 0.5, log_sales 0.5 | k=20, harmonic_mean, min_peers=3
      mechanism: If multiples are set by fundamentals (growth, profitability, risk, intangible investment), nearest neighbours on those fundamentals should value a firm well even across industries, as in warranted-multiple approaches. A large peer set aggregated with the harmonic mean diversifies away idiosyncratic mispricing.
      prediction: Pooled median |ln error| below the Bhojraj-Lee warranted-multiple baseline (0.357), though possibly not below the L3 industry median.

  (3) Sales_L2_margin_matched_median
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the price of a dollar of revenue is dominated by how much of it becomes profit. Matching same-sector peers mainly on EBITDA margin, with growth as a secondary driver, should remove the largest source of EV/Sales error.
      prediction: Pooled median |ln error| below 0.50, beating the L3 industry median (0.603) in all 4 exploration years.

  (4) Sales_margin_band_crossindustry_harmonic
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 1, rnd_intensity 0.5 | k=15, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
      mechanism: Firms earning similar EBITDA margins with similar growth and intangible investment should command similar revenue multiples regardless of sector label, because value per dollar of sales is a function of profit conversion and its growth. A hard margin band ensures no peer has a wildly different cost structure, while ranking on growth, gross margin and R&D refines the match.
      prediction: Pooled median |ln error| below 0.52 and beats the L3 industry median in at least 3 of 4 years.

  (5) Sales_L3_profitability_turnover_trimmed
      recipe: EV/Sales | screen same industry_l3 | rank ebit_margin 2, asset_turnover 1, sales_growth_1y 1, gross_margin 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a narrow industry, revenue multiples differ mainly because of operating margin and capital intensity: firms that convert sales into EBIT efficiently with little asset base create more value per dollar of revenue. Ranking same-industry peers on EBIT margin, asset turnover and growth, and using a trimmed mean, should capture these drivers while resisting outliers.
      prediction: Pooled median |ln error| below 0.53 and beats the L3 industry median in at least 3 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

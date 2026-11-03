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
  [g01-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-02] EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.5 | k=10, median, min_peers=5 | fallback []
  [g01-03] EV/Sales | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, asset_turnover 0.5 | k=15, median, min_peers=5
  [g01-04] EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank capex_intensity 1, sales_growth_1y 1, ebitda_margin 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
  [g01-05] EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
  [g01-06] EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.04]
  [g02-01] EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.75, log_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
  [g02-02] EV/EBITDA | screen same industry_l2, band log_sales±2 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
  [g02-03] EV/EBITDA | screen same industry_l3, band net_debt_to_ebitda±2 | rank ebitda_margin 1, sales_growth_1y 1, asset_turnover 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2, band net_debt_to_ebitda±2] -> [same industry_l2]
  [g02-04] EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_sales 1, capex_intensity 1, gross_margin 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.08]
  [g02-05] EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank roic 1, sales_growth_1y 1, asset_turnover 0.5 | k=10, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g02-06] EV/Sales | screen same industry_l4 | rank ebitda_margin 2, ebit_margin 1, sales_growth_1y 1 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
  [g03-01] EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band log_sales±1.5] -> [same industry_l3] -> [same industry_l2]
  [g03-02] EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
  [g03-03] EV/EBITDA | screen band sales_growth_1y±0.1, band net_debt_to_ebitda±1.5 | rank roic 1, ebit_margin 1, ebitda_margin 1, capex_intensity 0.5, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.2] -> []
  [g03-04] EV/Sales | screen band ebitda_margin±0.04, band capex_intensity±0.04 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08]
  [g03-05] EV/Sales | screen same industry_l2, band ebit_margin±0.03 | rank ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06]
  [g03-06] EV/Sales | screen band ebitda_margin±0.03, band log_sales±1.5 | rank sales_growth_1y 1, gross_margin 1, debt_to_assets 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]

PROPOSALS
  (0) sales_rnd_adjusted_margin_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band rnd_intensity±0.03 | rank sales_growth_1y 1, gross_margin 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: R&D is expensed, so two firms with the same reported EBITDA margin can have very different economic cash margins: the R&D-heavy firm is investing part of its margin in intangible capital that markets capitalize into value, which raises its EV/Sales. A hard band on R&D intensity next to the EBITDA-margin band puts peers at the same reported margin AND the same hidden investment rate, and ranking on growth, gross margin and size then matches duration, pricing power and the risk premium. Fallbacks drop the R&D constraint (for firms with no reported R&D) before widening the margin band.
      prediction: Beats the industry median EV/Sales in all 4 years with median error at or below 0.40, and does at least as well as g03-06 on R&D-intensive firms (rnd_intensity above 0.05).

  (1) sales_dupont_roa_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band asset_turnover±0.25 | rank sales_growth_1y 1, roic 1, debt_to_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06]
      mechanism: EV/Sales equals EV/Assets divided by asset turnover, and EBITDA margin times asset turnover is the pre-tax cash return on assets. Hard bands on both margin and turnover fix how much cash each dollar of sales produces and how much capital stands behind each dollar of sales, so peers share the same return on the asset base whatever their SIC code. Ranking on growth, ROIC and debt-to-assets then matches duration, value creation on new capital and financial risk.
      prediction: Beats the industry median EV/Sales in all 4 years with median error at or below 0.40; coverage at least 90%.

  (2) sales_operating_leverage_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.06 | rank sales_growth_1y 1, log_sales 1, capex_intensity 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03, band gross_margin±0.12] -> [band ebitda_margin±0.05]
      mechanism: Two firms with the same EBITDA margin but different gross margins have different cost structures: a high-gross-margin firm spends heavily on discretionary SG&A (marketing, customer acquisition) that is partly investment and gives strong operating leverage, so investors expect margin expansion and pay more per dollar of sales. Hard bands on both gross margin and EBITDA margin fix the current cash margin and the cost structure behind it, and ranking on growth, size and capex intensity matches duration, risk premium and reinvestment needs.
      prediction: Beats the industry median EV/Sales in all 4 years and has median error at or below 0.40, with lower mean error than g01-03 (0.672).

  (3) ebitda_rnd_expensing_regime
      recipe: EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: Because R&D is expensed, R&D-intensive firms report EBITDA that understates their pre-investment cash flow and carry growth options that the current EBITDA does not reflect, so they trade at systematically higher EV/EBITDA than low-R&D firms in the same broad industry. A hard band on R&D intensity inside the 2-digit industry keeps peers in the same expensing and growth-option regime, and ranking on growth, ROIC and net leverage matches the standard Gordon-model drivers; firms without R&D data fall back to plain industry peers.
      prediction: Median error at or below 0.330 and beats the industry median in at least 3 of 4 years.

  (4) ebitda_margin_cycle_position
      recipe: EV/EBITDA | screen same industry_l3, band ebitda_margin±0.05 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: EBITDA margins mean-revert, so a firm whose margin is depressed relative to industry norms trades at a high EV/EBITDA (the market prices in a recovery), while a firm at peak margins trades at a low one. A hard band on EBITDA margin inside the 3-digit industry puts peers at the same point in the margin cycle, so they share the same expected recovery or fade; ranking on growth, ROIC and net leverage then matches the remaining value drivers.
      prediction: Median error at or below 0.330, beats the industry median in at least 3 of 4 years, and lower mean error than the industry median baseline (0.513).

  (5) ebitda_pricing_power_moat
      recipe: EV/EBITDA | screen same industry_l2, band gross_margin±0.08 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2, band gross_margin±0.15] -> [same industry_l2]
      mechanism: Gross margin measures pricing power and product differentiation, which sets how long a firm can earn above its cost of capital (the competitive-advantage period). At equal near-term growth, a longer advantage period means a higher EV/EBITDA, and a broad 2-digit industry mixes branded and commodity producers. A gross-margin band inside the 2-digit industry keeps peers in the same competitive position, and ranking on growth, ROIC, net leverage and size matches the remaining drivers.
      prediction: Median error at or below 0.330 and beats the industry median in all 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

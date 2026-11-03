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
  [g04-01] EV/EBITDA | screen band sales_growth_1y±0.1, band roic±0.05 | rank rnd_intensity 1, capex_intensity 1, gross_margin 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.1] -> [same industry_l2] -> []
  [g04-02] EV/EBITDA | screen same industry_l2, band rnd_intensity±0.03 | rank sales_growth_1y 1, roic 1, capex_intensity 1 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
  [g04-03] EV/EBITDA | screen band gross_margin±0.08, band rnd_intensity±0.02 | rank sales_growth_1y 2, roic 1, capex_intensity 1 | k=10, median, min_peers=5 | fallback [same industry_l2, band gross_margin±0.1] -> [same industry_l2] -> []
  [g04-04] EV/Sales | screen band ebitda_margin±0.03, band capex_intensity±0.03 | rank sales_growth_1y 2, roic 1, gross_margin 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
  [g04-05] EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.1 | rank sales_growth_1y 2, rnd_intensity 1, asset_turnover 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
  [g04-06] EV/Sales | screen band ebit_margin±0.03, band sales_growth_1y±0.1 | rank roic 2, rnd_intensity 1, capex_intensity 1 | k=10, median, min_peers=5 | fallback [band ebit_margin±0.03] -> [band ebit_margin±0.06] -> []

PROPOSALS
  (0) ebitda_transitory_margin_l2
      recipe: EV/EBITDA | screen same industry_l2 | rank ebitda_margin 2, asset_turnover 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Investors capitalise normalised rather than current EBITDA, and profitability mean-reverts, so firms whose EBITDA margin is temporarily depressed trade at high EV/EBITDA and firms at peak margins trade at low ones (the Molodovsky effect applied to EBITDA). Within a 2-digit sector, matching on the EBITDA margin level, weighted most, aligns this cyclical position. Asset turnover separates structurally thin-margin, high-turnover models (distribution, retail) from depressed ones, and growth captures the remaining value driver.
      prediction: Median |ln error| below the industry baseline of 0.333 and beats the industry median in at least 3 of 4 exploration years.

  (1) ebitda_moat_duration_l2
      recipe: EV/EBITDA | screen same industry_l2 | rank roic 2, gross_margin 2, capex_intensity 1 | k=10, median, min_peers=5 | fallback []
      mechanism: In a value-driver model with fading excess returns, the EBITDA multiple depends less on this year's growth than on how long the firm can keep earning above its cost of capital (the competitive advantage period). High gross margin together with high ROIC is the accounting signature of pricing power and a durable moat, while capex intensity shows how much EBITDA must be reinvested to defend it. Within a 2-digit sector, peers matched on these persistence indicators should share the target's fade rate and so its EV/EBITDA.
      prediction: Beats the industry median in at least 3 of 4 years, with median |ln error| at or below 0.330.

  (2) ebitda_debt_capacity_l2
      recipe: EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 2, debt_to_assets 1, ebitda_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Lenders size debt to how stable and collateralised EBITDA is, so a firm's net debt to EBITDA and debt to assets reveal how much risk the credit market already sees in its EBITDA. Within a 2-digit sector, peers with the same debt capacity and EBITDA margin should carry a similar discount rate on EBITDA, and growth captures the cash-flow side. This aligns the risk term of a Gordon-style multiple, which growth and return features do not measure.
      prediction: Beats the industry median in at least 3 of 4 years; median |ln error| below 0.333.

  (3) sales_cashflow_box_discount_rank
      recipe: EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank log_assets 1, net_debt_to_ebitda 1, debt_to_assets 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: A DCF splits EV/Sales into a cash-flow part (margin and growth) and a discount-rate part. A tight cross-sector box on EBITDA margin and 1-year growth fixes the cash-flow part, so the remaining spread among the boxed peers should come mostly from risk. Ranking the survivors on size (log assets) and on leverage (net debt to EBITDA, debt to assets), the classic accounting proxies for the cost of capital, matches the discount rate rather than repeating the business-model features.
      prediction: Median |ln error| below 0.40 and beats the industry median in all 4 years.

  (4) sales_dupont_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band asset_turnover±0.3 | rank sales_growth_1y 2, roic 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: By the DuPont identity, return on assets equals EBITDA margin times asset turnover, and EV/Sales equals (EV / capital) times (capital / sales). The first term rises with the return on capital and the second is roughly the inverse of asset turnover. A hard cross-sector box on both EBITDA margin and asset turnover fixes both legs of the identity at once. Ranking on growth, weighted most, and ROIC then matches how far that return on capital is capitalised into value.
      prediction: Beats the industry median in all 4 years with median |ln error| below 0.40.

  (5) sales_latent_margin_box
      recipe: EV/Sales | screen band ebitda_margin±0.03, band gross_margin±0.08 | rank sales_growth_1y 2, rnd_intensity 1, capex_intensity 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: The gap between gross margin and EBITDA margin is SG&A plus R&D, which is largely discretionary, expensed growth spending. Two firms with the same reported EBITDA margin but different gross margins therefore have different latent steady-state margins, and the market prices the latent one. A cross-sector box on both EBITDA margin and gross margin fixes both the reported and the latent profitability. Ranking on growth, R&D intensity and capex intensity then matches how fast and with how much reinvestment that margin is earned.
      prediction: Median |ln error| at or below 0.39 and beats the industry median in all 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

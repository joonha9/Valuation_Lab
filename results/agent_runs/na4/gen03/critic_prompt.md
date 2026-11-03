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

PROPOSALS
  (0) L3 fundamental-twin EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, ebitda_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA is driven by expected growth, reinvestment needs and risk. Within a 3-digit industry, peers that also match on growth, return on capital and leverage share the same discount-rate and growth inputs, so their multiples are closer to the target's than the full industry's. A median of the nearest 10 resists outliers.
      prediction: Median |ln error| below the L3 industry median baseline (0.333) in at least 3 of 4 exploration years.

  (1) L2 growth-reinvestment EV/EBITDA
      recipe: EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, capex_intensity 1, roic 1, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback []
      mechanism: Value / EBITDA is roughly (1 - reinvestment rate) / (WACC - g), so firms with similar growth, capital intensity and ROIC should carry similar EBITDA multiples. The broader 2-digit pool gives enough candidates to find close fundamental matches, and the harmonic mean handles the right-skew of multiples.
      prediction: Median |ln error| below the warranted-multiple regression baseline (0.357) and within 0.02 of the L3 industry median overall.

  (2) Cross-industry size-quality EV/EBITDA
      recipe: EV/EBITDA | rank log_sales 1, ebitda_margin 1, roic 1, net_debt_to_ebitda 1, sales_growth_1y 1 | k=20, trimmed_mean, min_peers=3
      mechanism: Large, profitable, low-leverage firms trade at systematically different EBITDA multiples than small or distressed firms, whatever their industry. Matching on size, margin, ROIC and leverage across all firms captures that common risk premium. A trimmed mean over 20 peers lowers noise.
      prediction: Mean |ln error| below 0.513 (L3 industry mean), and median within 0.03 of the L3 industry median.

  (3) L3 margin-matched EV/Sales
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so differences in margin are the main reason sales multiples differ inside an industry. Industry peers ranked mainly on EBITDA margin, plus gross margin and growth, should take most of that variation out.
      prediction: Median |ln error| below 0.55, beating the L3 industry median baseline (0.603) in all 4 exploration years.

  (4) Cross-industry margin-band EV/Sales
      recipe: EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Firms that turn a sales dollar into the same EBITDA and grow at the same rate should be valued alike per sales dollar, regardless of SIC code, which often misclassifies diversified firms. A hard EBITDA-margin band forces economic comparability, and ranking on growth and ROIC refines it.
      prediction: Median |ln error| below 0.58 and mean below the regression baseline mean (0.837).

  (5) L2 profitability-capital EV/Sales
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, asset_turnover 1, capex_intensity 0.5, sales_growth_1y 1, debt_to_assets 0.5 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: Within a 2-digit sector, sales multiples rise with operating margin and fall with capital intensity and leverage, since asset-heavy, indebted firms keep less enterprise value per sales dollar. Ranking on margin, asset turnover, capex intensity and growth matches these drivers. The harmonic mean guards against high-multiple outliers.
      prediction: Beats the L3 industry median EV/Sales baseline in at least 3 of 4 years, with median |ln error| below 0.57.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

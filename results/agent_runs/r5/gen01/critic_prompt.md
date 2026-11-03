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
  (0) sales_margin_matched_within_l2
      recipe: EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in profitability. Picking peers in the same broad industry whose EBITDA margin and growth are closest to the target's holds the hidden EV/EBITDA term roughly fixed and matches the margin term directly.
      prediction: Median |ln error| below the EV/Sales industry-median baseline (0.603) in at least 3 of 4 exploration years, and below 0.55 when all years are pooled.

  (1) sales_cross_industry_fundamental_twins
      recipe: EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5
      mechanism: Within-industry sales multiples vary widely because margins vary, while firms in different industries with the same margin structure, growth and scale should be priced similarly per dollar of sales. Dropping the industry screen and matching on EBITDA margin, gross margin, growth and size gives a larger pool of firms whose economics really are alike.
      prediction: Beats the EV/Sales industry-median baseline (0.603) on the pooled median, and beats it in at least 3 of 4 exploration years.

  (2) sales_narrow_industry_margin_harmonic
      recipe: EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share technology and customers, and among them the ones with similar EBITDA and gross margins and similar asset turnover have a similar path from sales to cash flow. The harmonic mean weights low multiples more heavily and so damps the upward skew that a few richly valued peers add to sales multiples.
      prediction: Pooled median below 0.58 and a lower mean error than the EV/Sales industry-median baseline (0.945) in at least 3 of 4 exploration years.

  (3) ebitda_growth_quality_within_l3
      recipe: EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a constant-growth DCF, EV/EBITDA rises with expected growth and with return on invested capital, because high ROIC means less reinvestment is needed to grow. Within a 3-digit industry, peers that match the target on recent growth, ROIC and size should share its growth-and-reinvestment profile and so its multiple.
      prediction: Median |ln error| below the EV/EBITDA industry-median baseline (0.333) in at least 3 of 4 exploration years.

  (4) ebitda_capex_conversion_within_l2
      recipe: EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA overstates free cash flow by the amount of capital spending, so firms with heavy capex should trade at lower EV/EBITDA than asset-light firms with the same EBITDA. Matching peers in the broad industry on capex intensity, EBITDA margin and growth lines up how much EBITDA turns into cash, which drives the multiple.
      prediction: Pooled median below 0.33 (the industry-median baseline), with the largest gain over the baseline among firms in the top capex-intensity tercile.

  (5) ebitda_risk_size_harmonic
      recipe: EV/EBITDA | screen same industry_l2 | rank net_debt_to_ebitda 1, log_assets 1, roic 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: With growth held equal, EV/EBITDA falls as the cost of capital rises, and leverage and small size are the main accounting signs of higher risk and a higher discount rate. Peers in the same broad industry with similar net debt to EBITDA, asset size and ROIC should share the target's discount rate. The harmonic mean keeps a few richly priced peers from inflating the estimate.
      prediction: Beats both the warranted-multiple regression (0.357) and the warranted-multiple peers (0.380) on the pooled median, and beats the industry median (0.333) in at least 2 of 4 years.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}

You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 5). Accuracy is the median of |ln(V_est / V)|
across firm-years, where V is the firm's actual enterprise value on June 30 after its fiscal year.
Lower is better. Recipes are scored only on exploration years FY2016-2019; the
best ones will later be tested ONCE on later years you will never see, so prefer rules with a
clear economic reason over fragile tweaks. Cover both multiples across your proposals.

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

BASELINES (exploration years)
  EV/EBITDA: Industry median (L3, fallback L2) median 0.333, mean 0.513; Warranted multiple (Bhojraj-Lee regression) median 0.357, mean 0.492; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.380, mean 0.523
  EV/Sales: Industry median (L3, fallback L2) median 0.603, mean 0.945; Warranted multiple (Bhojraj-Lee regression) median 0.674, mean 0.837; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.691, mean 0.861

ARCHIVE: your earlier graded attempts, exploration scores only (21 graded)
  [g03-04] EV/EBITDA median 0.308 | mean 0.473 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.037
      EV/EBITDA | screen same industry_l2 | rank gross_margin 1, capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5
      mechanism: Inside an industry, firms with high gross margins tend to have durable moats and pricing power. Their EBITDA is more persistent and earns a higher multiple. Capex intensity and EBIT margin measure how much of EBITDA is used up by reinvestment and depreciation. Ranking 2-digit industry peers on gross margin, capex, EBIT margin and growth matches both how durable the earnings are and how much of them turns into cash.
  [g03-05] EV/EBITDA median 0.310 | mean 0.472 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.038
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, sales_growth_1y 1, net_debt_to_ebitda 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5
      mechanism: EV is unlevered in theory, but heavily indebted firms carry expected distress costs and less financial flexibility, which pushes down their EV/EBITDA. Within the 2-digit industry, matching on net debt to EBITDA together with capex intensity, EBIT margin and growth aligns the distress discount, cash conversion and growth outlook. A trimmed mean limits the influence of distressed or richly priced outliers.
  [g04-01] EV/EBITDA median 0.312 | mean 0.478 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.035
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, rnd_intensity 1, gross_margin 1, ebit_margin 1, sales_growth_1y 1, log_assets 0.5 | k=12, median, min_peers=5 | fallback []
      mechanism: R&D is expensed, so it lowers reported EBITDA even though it is an investment in future earnings, much like capex. R&D-heavy firms therefore show depressed EBITDA relative to their economic earnings and trade at higher EV/EBITDA. Within the 2-digit industry, matching on R&D intensity together with capex intensity, gross margin, EBIT margin and growth aligns total reinvestment (tangible plus intangible), pricing power and growth.
  [g02-04] EV/EBITDA median 0.317 | mean 0.483 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.031
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA leaves out depreciation and amortization, so it overstates the cash earnings of firms with heavy asset bases. The gap between EBITDA margin and EBIT margin measures this D&A burden, and capex intensity measures the reinvestment needed going forward. Within the 2-digit industry, matching both margins together with capex and growth picks peers that turn EBITDA into free cash flow at the same rate.
  [g01-02] EV/EBITDA median 0.322 | mean 0.488 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.026
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 1.5, sales_growth_1y 1, ebitda_margin 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores the depreciation and capital spending needed to sustain it, so capital-heavy firms convert less EBITDA into free cash flow and deserve lower EV/EBITDA. Within the 3-digit industry, matching on capex intensity and growth aligns the EBITDA-to-FCF conversion and growth outlook that drive the multiple.
  [g03-06] EV/EBITDA median 0.328 | mean 0.492 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.021
      EV/EBITDA | screen same industry_l2, band capex_intensity±0.04 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Capex intensity has been the strongest ranking signal for EV/EBITDA, because it sets how much EBITDA must be reinvested to sustain the business. Turning it into a hard band within the 2-digit industry means no peer has a very different reinvestment burden. Ranking on EBIT and EBITDA margins (the D&A gap) plus growth and size then sorts out the remaining differences in value drivers.
  [g02-05] EV/EBITDA median 0.335 | mean 0.506 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.007
      EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a constant-growth valuation, EV/EBITDA depends most on expected growth, just as EV/Sales depends most on margin. A hard band on 1-year sales growth within the 2-digit industry forces peers to have similar growth. Ranking on capex intensity and ROIC then lines up how much reinvestment that growth costs.
  [g01-01] EV/EBITDA median 0.335 | mean 0.504 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.009
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1.5, roic 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and with the return on new investment (high ROIC means less reinvestment per unit of growth), and larger firms trade at lower risk premia. Restricting to the 2-digit industry keeps shared business risk while ranking on growth, ROIC and size picks peers with the same fundamental value drivers inside a deeper pool than L3.
  [g01-03] EV/EBITDA median 0.343 | mean 0.534 | coverage 98.8% | beats industry 0/4 yrs | gain vs industry -0.022
      EV/EBITDA | screen same industry_l4 | rank log_assets 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The narrowest industry definition captures the most similar products, customers and cyclicality, and the harmonic mean is the theoretically consistent average of price ratios (it averages the yield EBITDA/EV) and damps high-multiple outliers. Ranking on size and asset turnover within the narrow industry further aligns scale-driven risk and business model.
  [g02-06] EV/EBITDA median 0.349 | mean 0.509 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.004
      EV/EBITDA | screen band ebitda_margin±0.05, band sales_growth_1y±0.1 | rank capex_intensity 1.5, roic 1, log_sales 1 | k=15, median, min_peers=5 | fallback [band sales_growth_1y±0.1] -> []
      mechanism: If EV/EBITDA is set by growth, reinvestment needs and risk rather than by industry labels, then firms with similar growth and EBITDA margins should share a multiple across industries. The margin band also stands in for competitive position. Ranking on capex intensity, ROIC and size then matches free-cash-flow conversion and the risk premium. This recipe tests whether the cross-industry fundamental matching that works for EV/Sales also works for EV/EBITDA.
  [g03-02] EV/Sales median 0.371 | mean 0.565 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.268
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=6, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: The narrowest industry that still has enough margin-matched peers gives the closest business risk and growth outlook. Starting from the 3-digit industry inside an EBITDA-margin band and widening step by step (2-digit plus band, then band alone, then a wider band) uses the most specific valid peer group for each firm. Ranking on EBITDA margin, gross margin and growth handles any profitability gap left inside the band.
  [g03-01] EV/Sales median 0.372 | mean 0.559 | coverage 94.3% | beats industry 4/4 yrs | gain vs industry +0.284
      EV/Sales | screen same industry_l2, band gross_margin±0.1, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band gross_margin±0.08, band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: EV/Sales equals EBITDA margin times an EBITDA multiple. The multiple itself depends on industry risk and on pricing power, which shows up in gross margin. Requiring the same 2-digit industry together with matching gross and EBITDA margins equalizes profitability, cost structure and business risk all at once. Ranking on growth, capex intensity and size then lines up duration and reinvestment needs. Fallbacks to the cross-industry double band and then a wide EBITDA band keep coverage high.
  [g02-01] EV/Sales median 0.391 | mean 0.586 | coverage 94.3% | beats industry 4/4 yrs | gain vs industry +0.258
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: EV/Sales is the EBITDA margin times an EBITDA multiple. The margin band equalizes the margin, and the shared 2-digit industry equalizes the multiple's industry-level risk, cyclicality and growth. Requiring both conditions together should remove the profitability error that plain industry medians make, and also the business-risk mismatch that a pure cross-industry margin match allows. When the industry-plus-band pool is too thin, the rule falls back to the cross-industry margin band, so coverage stays complete.
  [g04-05] EV/Sales median 0.391 | mean 0.579 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.252
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 1.5, sales_growth_1y 1.5, ebitda_margin 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: Once the margin is fixed, the EBITDA multiple embedded in EV/Sales depends on growth, but growth only adds value when ROIC exceeds the cost of capital. Growth at low ROIC can even destroy value. Inside the 2-digit industry plus an EBITDA-margin band, ranking with equal heavy weights on ROIC and 1-year growth picks peers whose growth creates value at the same rate.
  [g03-03] EV/Sales median 0.396 | mean 0.569 | coverage 93.0% | beats industry 4/4 yrs | gain vs industry +0.256
      EV/Sales | screen band ebitda_margin±0.05, band capex_intensity±0.03 | rank sales_growth_1y 1.5, gross_margin 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: What sales are worth depends on the free cash flow each dollar of sales produces, which is roughly EBITDA margin minus capex intensity. Two firms with the same EBITDA margin but very different capex needs convert sales to cash at very different rates. Hard bands on both EBITDA margin and capex intensity match FCF margin across industries. Ranking on growth, gross margin (pricing power) and size then handles duration and risk.
  [g04-04] EV/Sales median 0.398 | mean 0.588 | coverage 94.0% | beats industry 4/4 yrs | gain vs industry +0.253
      EV/Sales | screen same industry_l2, band ebit_margin±0.04 | rank ebit_margin 2, ebitda_margin 1, sales_growth_1y 1, gross_margin 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebit_margin±0.04] -> [band ebit_margin±0.08] -> [band ebitda_margin±0.1]
      mechanism: Sales are worth what they convert into sustainable cash flow. EBIT margin, which subtracts D&A as a proxy for maintenance capex, is closer to that than EBITDA margin, because it does not overstate the cash margin of asset-heavy firms. A hard EBIT-margin band inside the 2-digit industry matches after-reinvestment profitability and business risk together. Ranking on EBIT and EBITDA margin (which also captures the D&A gap), growth, gross margin and size then sorts out the remaining differences.
  [g02-03] EV/Sales median 0.399 | mean 0.581 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.256
      EV/Sales | screen band gross_margin±0.08, band ebitda_margin±0.05 | rank sales_growth_1y 1.5, capex_intensity 1, log_sales 0.5 | k=10, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: Two firms can have the same EBITDA margin while earning it through different cost structures. A high-gross-margin, high-opex firm, such as software, has more pricing power and operating leverage than a low-gross-margin, lean-opex firm, such as distribution. Banding on both gross margin and EBITDA margin matches pricing power and cost structure across industries. Ranking on growth, capital intensity and size then handles duration and risk, and a trimmed mean limits the effect of extreme peers.
  [g02-02] EV/Sales median 0.422 | mean 0.611 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.216
      EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank ebitda_margin 2, capex_intensity 1, roic 1, log_assets 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.1]
      mechanism: With the margin held fixed, what is left of the EV/Sales multiple depends mainly on expected growth and on how much reinvestment that growth needs. Hard bands on both EBITDA margin and 1-year growth fix the two largest drivers. Ranking on capital intensity and ROIC then lines up the free-cash-flow conversion of each sales dollar.
  [g01-05] EV/Sales median 0.429 | mean 0.634 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.312
      EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: If EV/Sales is mostly profitability times a growth- and risk-driven EBITDA multiple, then firms with near-identical EBITDA margins, growth and size should share EV/Sales even across industries. A hard band on EBITDA margin forces profitability equality, and ranking on growth, ROIC and size handles the remaining multiple drivers.
  [g01-04] EV/Sales median 0.474 | mean 0.771 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.174
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times the EBITDA margin, so most cross-sectional dispersion in EV/Sales comes from profitability differences. Within a 2-digit industry, ranking peers primarily on EBITDA margin and secondarily on gross margin and growth removes the dominant source of error that plain industry medians ignore.
  [g01-06] EV/Sales median 0.590 | mean 0.883 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.062
      EV/Sales | screen same industry_l3 | rank ebitda_margin 2.5, sales_growth_1y 1, log_sales 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Within the 3-digit industry, firms with the same EBITDA margin and growth have the same cash-flow-per-dollar-of-sales and similar duration, so their EV/Sales should coincide; the harmonic mean limits the upward pull of a few richly priced peers that commonly inflate EV/Sales averages.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g04-02] rejected: critic: Every rank feature (gross margin, capex intensity, net debt/EBITDA, ROIC, growth, size) has already been tried in g03-04, g03-05 and g02-05, so the part that is actually new is the harmonic-me
  [g04-03] rejected: critic: The recipe does not implement the mechanism: 'temporarily depressed' EBITDA is relative to a firm's own normal earnings, but ranking on current-year levels of EBITDA margin, net margin and ROE
  [g04-06] rejected: critic: This is essentially g03-01 with a 3-digit tier added in front of the same fallback chain (already explored in g03-02), k cut from 8 to 6, and an EBITDA-margin rank feature that adds little ins

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

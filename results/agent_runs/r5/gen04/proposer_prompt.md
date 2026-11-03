You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 4). Accuracy is the median of |ln(V_est / V)|
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

ARCHIVE: your earlier graded attempts, exploration scores only (16 graded)
  [g01-05] EV/EBITDA median 0.323 | mean 0.493 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.021
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1.5, ebitda_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA overstates free cash flow by the amount of capital spending, so firms with heavy capex should trade at lower EV/EBITDA than asset-light firms with the same EBITDA. Matching peers in the broad industry on capex intensity, EBITDA margin and growth lines up how much EBITDA turns into cash, which drives the multiple.
  [g03-01] EV/EBITDA median 0.326 | mean 0.496 | coverage 98.3% | beats industry 4/4 yrs | gain vs industry +0.014
      EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank capex_intensity 1, roic 1, ebitda_margin 0.5, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band sales_growth_1y±0.2] -> [same industry_l2]
      mechanism: In a constant-growth DCF, EV/EBITDA is proportional to (1 - reinvestment rate) / (WACC - g), so expected growth enters the denominator and is the most powerful single driver of the multiple. A hard screen holding 1-year sales growth within 10 points of the target's inside the same 2-digit industry fixes the growth term outright, and ranking the survivors on capex intensity and ROIC (how much of EBITDA must be reinvested to sustain that growth), EBITDA margin and size (a discount-rate proxy) lines up the remaining terms.
  [g02-02] EV/EBITDA median 0.326 | mean 0.502 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.012
      EV/EBITDA | screen same industry_l3, band log_sales±1.5 | rank ebit_margin 1, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: The gap between EBITDA margin and EBIT margin is depreciation as a share of sales, which measures how much capital the business uses up each year that EBITDA ignores. Peers in the same 3-digit industry and of similar size (a proxy for risk and discount rate) that match on both margins and on growth consume capital at a similar rate, so they should share the target's EV/EBITDA. The harmonic mean damps the few richly valued peers that skew multiples upward.
  [g03-03] EV/EBITDA median 0.332 | mean 0.510 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.004
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_assets 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA depends on three DCF terms: growth, the reinvestment needed to fund it, and the discount rate. Within a 3-digit industry, recent sales growth measures the first, capex intensity the second, and net debt to EBITDA plus asset size proxy the third, since heavily levered and small firms carry higher distress and financing risk and are priced at lower multiples of the same EBITDA. The harmonic mean damps the upward skew from a few richly valued peers.
  [g01-04] EV/EBITDA median 0.332 | mean 0.496 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.017
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a constant-growth DCF, EV/EBITDA rises with expected growth and with return on invested capital, because high ROIC means less reinvestment is needed to grow. Within a 3-digit industry, peers that match the target on recent growth, ROIC and size should share its growth-and-reinvestment profile and so its multiple.
  [g03-02] EV/EBITDA median 0.335 | mean 0.509 | coverage 98.2% | beats industry 1/4 yrs | gain vs industry +0.001
      EV/EBITDA | screen same industry_l2, band capex_intensity±0.03 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [same industry_l2, band capex_intensity±0.06] -> [same industry_l2]
      mechanism: EBITDA ignores capital spending, so the share of EBITDA that becomes free cash flow falls one-for-one with capex intensity; two firms with the same EBITDA but different capex needs deserve different EV/EBITDA. Screening peers in the same 2-digit industry to within 3 points of the target's capex-to-sales fixes this reinvestment burden as a hard constraint rather than a trade-off in a distance, and ranking on growth, ROIC and size then matches the growth, reinvestment efficiency and discount-rate terms of the DCF multiple.
  [g02-03] EV/EBITDA median 0.336 | mean 0.516 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry -0.002
      EV/EBITDA | screen same industry_l3 | rank rnd_intensity 1, asset_turnover 1, gross_margin 1, sales_growth_1y 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Because R&D is expensed, EBITDA understates the cash-generating capacity of R&D-heavy firms and they trade at higher EV/EBITDA, while asset turnover and gross margin capture whether a firm earns its profits through pricing power or volume on heavy assets. Within a 3-digit industry, peers that match on R&D intensity, asset turnover, gross margin and growth share the same business model and the same bias in reported EBITDA, so their multiple carries over. The trimmed mean removes extreme peers without discarding the middle of the distribution.
  [g02-01] EV/EBITDA median 0.344 | mean 0.508 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.005
      EV/EBITDA | rank capex_intensity 1.5, roic 1, sales_growth_1y 1, ebitda_margin 0.5 | k=20, median, min_peers=5
      mechanism: In a steady-state DCF, EV/EBITDA equals (1 - reinvestment share of EBITDA) / (WACC - g), and the reinvestment share depends on capital intensity and on the return earned on new capital, not on the industry label. Firms from any industry with similar capex intensity, ROIC, growth and EBITDA margin convert EBITDA into free cash flow at similar rates, and a large cross-industry pool of such firms gives a steadier median than a thin industry group.
  [g03-04] EV/Sales median 0.423 | mean 0.663 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.282
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales equals EBITDA margin times EV/EBITDA, so a tight EBITDA-margin band fixes the margin term, while the shared 2-digit industry adds common cyclicality, customers and risk that move the hidden EV/EBITDA term. Ranking the survivors on growth, capital intensity and size then matches the remaining drivers of EV/EBITDA, and falling back to a cross-industry margin band keeps coverage when the industry is thin; the harmonic mean damps upward skew in sales multiples.
  [g03-05] EV/Sales median 0.445 | mean 0.672 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.274
      EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.06, band sales_growth_1y±0.2] -> [band ebitda_margin±0.06] -> []
      mechanism: The two dominant drivers of a sales multiple are profitability (the EBITDA margin term) and growth (which sets the EV/EBITDA term through WACC - g), so hard-screening both, within 3 points of margin and 10 points of growth, guarantees every peer shares the target's two largest value drivers regardless of industry label. Ranking survivors on capex intensity and R&D intensity then matches how much of the margin is consumed by reinvestment or understated by expensed R&D, and size proxies for risk.
  [g03-06] EV/Sales median 0.447 | mean 0.682 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.265
      EV/Sales | screen band ebit_margin±0.04 | rank ebitda_margin 1, sales_growth_1y 1, debt_to_assets 0.5, log_assets 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebit_margin±0.08] -> []
      mechanism: EBIT margin charges depreciation and so is closer to the cash profit per dollar of sales that a buyer of the whole firm receives than EBITDA margin is; screening on EBIT margin within 4 points and ranking on EBITDA margin pins both the operating margin and the D&A share of sales, i.e. the capital the business consumes. Matching growth, leverage and asset size then aligns the growth and discount-rate terms, so cross-industry peers with the same after-depreciation economics should trade at similar sales multiples.
  [g02-05] EV/Sales median 0.448 | mean 0.698 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.248
      EV/Sales | screen band ebitda_margin±0.04 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 0.5, log_sales 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
      mechanism: Profitability is the dominant driver of sales multiples, so a hard screen holding EBITDA margin within a few points of the target's guarantees that every peer has the same margin term, instead of trading margin off against other features in a distance ranking. Within that margin band, firms from any industry that also match on growth, gross margin, capital intensity and size should be priced similarly per dollar of sales.
  [g01-03] EV/Sales median 0.489 | mean 0.797 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.148
      EV/Sales | screen same industry_l3 | rank ebitda_margin 2, gross_margin 1, asset_turnover 1 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share technology and customers, and among them the ones with similar EBITDA and gross margins and similar asset turnover have a similar path from sales to cash flow. The harmonic mean weights low multiples more heavily and so damps the upward skew that a few richly valued peers add to sales multiples.
  [g01-01] EV/Sales median 0.535 | mean 0.813 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.129
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most of the spread in sales multiples comes from differences in profitability. Picking peers in the same broad industry whose EBITDA margin and growth are closest to the target's holds the hidden EV/EBITDA term roughly fixed and matches the margin term directly.
  [g02-04] EV/Sales median 0.535 | mean 0.851 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.095
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, rnd_intensity 1, gross_margin 1 | k=8, harmonic_mean, min_peers=4 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, but for firms that expense large R&D budgets the reported EBITDA margin understates their economic margin, so two firms with the same EBITDA margin can deserve different sales multiples. Matching peers in the same 2-digit industry on EBITDA margin, R&D intensity and gross margin lines up the true pre-investment profitability per dollar of sales, and the harmonic mean damps upward skew in sales multiples.
  [g01-02] EV/Sales median 0.549 | mean 0.717 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.228
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=5
      mechanism: Within-industry sales multiples vary widely because margins vary, while firms in different industries with the same margin structure, growth and scale should be priced similarly per dollar of sales. Dropping the industry screen and matching on EBITDA margin, gross margin, growth and size gives a larger pool of firms whose economics really are alike.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g01-06] rejected: critic: The mechanism holds growth equal yet the recipe ranks on no growth feature, and ROIC is a reinvestment-efficiency variable rather than a risk signal, so the screens do not implement the stated
  [g02-06] rejected: critic: The stated mechanism is mis-specified: FCF margin is after-tax EBIT margin plus D&A/sales minus capex/sales, so subtracting full capex from an EBIT margin that already charges depreciation cou

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

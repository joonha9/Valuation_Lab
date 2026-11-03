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

ARCHIVE: your earlier graded attempts, exploration scores only (24 graded)
  [g04-02] EV/EBITDA median 0.306 | mean 0.458 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.056
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, ebit_margin 1, rnd_intensity 1, asset_turnover 1, net_debt_to_ebitda 1 | k=20, median, min_peers=5
      mechanism: The gap between EBITDA margin and EBIT margin is depreciation and amortization per dollar of sales, a measure of how much past capital spending EBITDA leaves out. Firms whose EBITDA is largely eaten by D&A turn less of it into lasting cash flow and should trade at lower EV/EBITDA, so matching EBIT margin next to EBITDA margin lines up capital consumption that capex in a single year can miss.
  [g03-01] EV/EBITDA median 0.309 | mean 0.461 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.053
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1, asset_turnover 1, net_debt_to_ebitda 1 | k=20, median, min_peers=5
      mechanism: The best EV/EBITDA rule ranked the whole cross-section on reinvestment, growth, returns and margin structure. Asset turnover adds the capital needed per dollar of sales (working capital and fixed assets, not only capex), and net debt to EBITDA captures financial risk and the tax shield, which move the discount rate applied to EBITDA. Matching on both should align the cash conversion and risk that EV/EBITDA prices.
  [g04-01] EV/EBITDA median 0.312 | mean 0.459 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.055
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1, asset_turnover 1, net_debt_to_ebitda 2 | k=20, median, min_peers=5
      mechanism: EV/EBITDA splits exactly into market cap/EBITDA plus net debt/EBITDA, so net leverage is a direct part of the multiple and also moves the tax shield and discount rate. Adding net debt to EBITDA helped the best rule; doubling its weight tightens the match on this part of the multiple while keeping the growth, reinvestment, return and margin drivers.
  [g04-03] EV/EBITDA median 0.313 | mean 0.465 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.049
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1, asset_turnover 2, net_debt_to_ebitda 1 | k=20, median, min_peers=5
      mechanism: Asset turnover measures all the capital (working capital and fixed assets) tied up per dollar of sales, so together with capex intensity it sets how much EBITDA must be reinvested to grow. Adding turnover improved the best rule, so giving it the same weight as capex should match the full reinvestment burden that EV/EBITDA prices.
  [g02-05] EV/EBITDA median 0.326 | mean 0.477 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.036
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1 | k=20, median, min_peers=5
      mechanism: The EV/Sales results showed that dropping the SIC screen and matching tightly on fundamentals beat industry peers. The same may hold for EV/EBITDA, whose DCF drivers are growth, reinvestment (capex intensity), return on capital and the gap between gross and EBITDA margin (spending on SG&A and R&D that builds intangibles). Ranking the full cross-section on these targets firms with the same value drivers across SIC boundaries.
  [g02-04] EV/EBITDA median 0.327 | mean 0.495 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.018
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 2, rnd_intensity 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Building on the best EV/EBITDA attempt: capex intensity sets how much of EBITDA turns into free cash flow, while R&D intensity marks firms that invest through operating expense, so their EBITDA understates steady-state earnings and they trade at higher multiples. Matching both, plus growth and ROIC, inside the 2-digit industry aligns the reinvestment and growth profile that the multiple prices.
  [g01-03] EV/EBITDA median 0.330 | mean 0.505 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.009
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 2, sales_growth_1y 1, roic 1, debt_to_assets 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores capital spending, so two firms with equal EBITDA but different capex intensity convert very different shares of it into free cash flow; capital-heavy firms should trade at lower EV/EBITDA. Matching peers within the 2-digit industry on capex intensity, growth and leverage aligns the cash-conversion and risk profile that the multiple prices.
  [g03-02] EV/EBITDA median 0.334 | mean 0.481 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.032
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1, log_sales 1 | k=25, median, min_peers=5
      mechanism: Size proxies for risk, diversification and access to capital: larger firms have lower discount rates and more stable EBITDA, so they trade at higher EV/EBITDA for the same growth and reinvestment. Adding log sales to the best cross-sectional driver set, with a slightly larger k for stability, should remove the size-driven part of the remaining error.
  [g01-02] EV/EBITDA median 0.335 | mean 0.511 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.002
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, ebitda_margin 1, log_sales 1 | k=10, harmonic_mean, min_peers=5 | fallback []
      mechanism: In a DCF, EV/EBITDA rises with expected growth and with return on invested capital (less reinvestment needed per unit of growth), and falls with risk. Within a broad industry, picking the nearest peers on growth, ROIC, margin and size targets firms with the same value drivers rather than just the same SIC label.
  [g01-01] EV/EBITDA median 0.341 | mean 0.532 | coverage 100.0% | beats industry 0/4 yrs | gain vs industry -0.018
      EV/EBITDA | screen same industry_l3 | k=all, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share demand cycles, risk and reinvestment needs, so their EV/EBITDA multiples cluster. The harmonic mean averages the inverse multiple (an earnings yield), which is less sensitive to a few peers with very high multiples from temporarily low EBITDA, and is known to reduce upward bias relative to the arithmetic mean.
  [g03-03] EV/EBITDA median 0.344 | mean 0.504 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.010
      EV/EBITDA | rank capex_intensity 2, sales_growth_1y 1, roic 1, gross_margin 1, ebitda_margin 1, rnd_intensity 1 | k=20, harmonic_mean, min_peers=5
      mechanism: With the same driver-matched cross-sectional peers as the best EV/EBITDA rule, the harmonic mean averages earnings yields, so peers whose multiples are inflated by temporarily depressed EBITDA carry little weight while all 20 peers still contribute information. This tests whether pooling the matched peers beats taking their median.
  [g02-06] EV/EBITDA median 0.374 | mean 0.593 | coverage 100.0% | beats industry 0/4 yrs | gain vs industry -0.080
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 2, debt_to_assets 1, sales_growth_1y 1, log_sales 0.5 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share cyclicality and risk, but within it capex intensity and leverage still vary widely. Capex sets free-cash conversion, and leverage moves the equity risk that feeds into EV. Ranking L3 peers on capex intensity, debt to assets and growth, then taking a trimmed mean, keeps the closest risk and reinvestment peers while dropping peers whose multiples are swollen by temporarily low EBITDA.
  [g04-06] EV/Sales median 0.403 | mean 0.641 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.305
      EV/Sales | rank ebitda_margin 4, ebit_margin 1, asset_turnover 1.5, gross_margin 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5
      mechanism: Two firms with equal EBITDA margins can have very different EBIT margins if one must spend heavily on depreciating assets, so value per dollar of sales depends on the margin that survives capital consumption. Adding EBIT margin to the margin and turnover match separates asset-light firms from capital-heavy ones with the same EBITDA margin.
  [g04-05] EV/Sales median 0.404 | mean 0.659 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.288
      EV/Sales | rank ebitda_margin 4, asset_turnover 1.5, gross_margin 1, sales_growth_1y 1, roic 1, capex_intensity 1, net_debt_to_ebitda 1 | k=10, median, min_peers=5
      mechanism: EV/Sales is EBITDA margin times EV/EBITDA, so after matching margin the remaining dispersion is the EV/EBITDA multiple itself, which the best EV/EBITDA rule explains with capex intensity and net leverage on top of growth, returns and turnover. Adding those two EV/EBITDA drivers to the margin-weighted EV/Sales match should align both factors of the sales multiple.
  [g03-05] EV/Sales median 0.405 | mean 0.643 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.303
      EV/Sales | rank ebitda_margin 4, asset_turnover 1.5, gross_margin 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, and asset turnover sets how much capital each dollar of sales ties up, which drives value per dollar of sales once margin is fixed. Raising the weights on EBITDA margin and asset turnover and keeping only the 10 nearest peers tightens the match on the two levers that explain most EV/Sales dispersion, as the best rule (the only one using turnover) suggests.
  [g04-04] EV/Sales median 0.406 | mean 0.651 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.295
      EV/Sales | rank ebitda_margin 4, asset_turnover 1.5, gross_margin 1, sales_growth_1y 1, roic 1, net_debt_to_ebitda 1 | k=10, median, min_peers=5
      mechanism: EV/Sales equals market cap/sales plus net debt/sales, and net debt to EBITDA times EBITDA margin gives the net debt part directly, so once margin is matched, matching net leverage pins down part of the multiple and the financial risk behind it. Adding it to the best margin and turnover rule should cut the error left over after profitability.
  [g01-05] EV/Sales median 0.409 | mean 0.654 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.292
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1, asset_turnover 1 | k=15, median, min_peers=5
      mechanism: If value per dollar of sales is driven by margin, growth and capital efficiency, firms with the same fundamentals should carry similar EV/Sales regardless of SIC code; SIC codes are coarse and often misclassify diversified firms. Dropping the industry screen enlarges the pool so the nearest neighbours match much more tightly on the actual value drivers.
  [g01-06] EV/Sales median 0.412 | mean 0.625 | coverage 94.0% | beats industry 4/4 yrs | gain vs industry +0.201
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | k=all, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [same industry_l2, band ebitda_margin±0.1] -> [band ebitda_margin±0.03]
      mechanism: A sales multiple is only comparable among firms with similar profitability; within the same industry, restricting peers to those whose EBITDA margin is within 5 points of the target's removes the main source of dispersion in EV/Sales. The harmonic mean then damps the influence of high-multiple peers in the band.
  [g03-06] EV/Sales median 0.413 | mean 0.617 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.329
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1, asset_turnover 1, log_sales 1 | k=15, median, min_peers=5
      mechanism: Holding margin, growth, capital efficiency and turnover fixed, larger firms carry lower risk and more durable margins, so they are worth more per dollar of sales. Adding log sales to the best EV/Sales driver set aligns this risk dimension without reintroducing coarse SIC screens.
  [g02-03] EV/Sales median 0.420 | mean 0.738 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.209
      EV/Sales | screen band ebitda_margin±0.03 | rank sales_growth_1y 1, roic 1, capex_intensity 1, gross_margin 1 | k=15, median, min_peers=8 | fallback [band ebitda_margin±0.06] -> []
      mechanism: A hard band of plus or minus 3 points of EBITDA margin removes the dominant driver of EV/Sales dispersion before any ranking. Within that band, the remaining differences in value come from growth, capital efficiency and reinvestment needs, so ranking on these picks the peers whose margin also lasts and grows at the target's pace.
  [g03-04] EV/Sales median 0.432 | mean 0.725 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.220
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1, asset_turnover 1 | k=15, harmonic_mean, min_peers=5
      mechanism: The best EV/Sales rule matched the whole cross-section on margin, growth, returns and asset turnover. Because EV/Sales is right-skewed even among close matches, the harmonic mean (which averages sales yields) damps a few richly valued peers, which helped the banded L3 rule's mean error. This isolates the aggregator effect on the best peer set.
  [g01-04] EV/Sales median 0.477 | mean 0.779 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.166
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the main driver of a sales multiple is profitability. Within the same 2-digit industry, peers with similar EBITDA and gross margins and similar growth should share the target's EV/Sales much more closely than the industry as a whole.
  [g02-01] EV/Sales median 0.493 | mean 0.746 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.200
      EV/Sales | rank ebitda_margin 3, capex_intensity 1, sales_growth_1y 1, roic 1, gross_margin 1 | k=20, median, min_peers=5
      mechanism: EV/Sales is EV/EBITDA times EBITDA margin, and EV/EBITDA itself depends on how much of EBITDA must be reinvested (capex) and on growth. Ranking the whole cross-section on EBITDA margin, capex intensity, growth and ROIC finds firms whose cash conversion per dollar of sales matches the target's, and works better than SIC codes, which are coarse. A larger k of 20 with the median steadies the estimate against a few odd peers.
  [g02-02] EV/Sales median 0.539 | mean 0.771 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.175
      EV/Sales | rank ebitda_margin 3, gross_margin 1.5, rnd_intensity 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=5
      mechanism: R&D is expensed, so research-heavy firms show depressed EBITDA margins but high gross margins and high value per dollar of sales; matching on margin alone pairs them with genuinely low-profit firms. Adding R&D intensity and gross margin next to EBITDA margin separates firms that invest through the income statement from firms that are simply unprofitable, so peers share the target's true economic margin.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

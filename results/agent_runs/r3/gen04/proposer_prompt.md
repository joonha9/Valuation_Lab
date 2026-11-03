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
  [g02-01] EV/EBITDA median 0.316 | mean 0.474 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.040
      EV/EBITDA | screen same industry_l2 | rank ebitda_margin 1, ebit_margin 1, roic 1, sales_growth_1y 1, net_debt_to_ebitda 0.5 | k=12, trimmed_mean, min_peers=6 | fallback []
      mechanism: EBITDA ignores depreciation, so two firms with the same EBITDA margin but different EBIT margins differ in how much of EBITDA is consumed by asset replacement and how much is taxable; matching both ebitda_margin and ebit_margin implicitly matches D&A intensity. Doing this inside the 2-digit sector (shared macro risk and cost of capital) while also matching ROIC, growth and leverage combines the industry anchor with the driver-based nearest-neighbour idea, and a trimmed mean limits outlier peers.
  [g03-02] EV/EBITDA median 0.327 | mean 0.478 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.036
      EV/EBITDA | screen band net_debt_to_ebitda±1 | rank roic 1, sales_growth_1y 1, ebit_margin 1, log_assets 1, rnd_intensity 0.5 | k=15, median, min_peers=8 | fallback [band net_debt_to_ebitda±2] -> []
      mechanism: Lenders extend debt as a multiple of EBITDA in proportion to how stable and durable they judge that EBITDA to be, so a firm's net debt/EBITDA is an accounting-based revealed signal of the risk of its cash flows, which is the denominator of the EV/EBITDA multiple. Banding on net debt/EBITDA groups firms with similar perceived cash-flow risk and capital structure across industries, and ranking on ROIC, growth, EBIT margin, size and R&D matches the remaining value drivers.
  [g01-01] EV/EBITDA median 0.327 | mean 0.495 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.018
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA is a capitalized cash-flow multiple, so firms in the same 3-digit industry share risk, but within an industry the multiple still varies with growth, the return earned on reinvestment (ROIC), and how much of EBITDA is consumed by capex. Matching peers on capex intensity, growth and ROIC inside the industry should pick firms whose EBITDA converts to free cash flow and grows at similar rates, so they should carry similar multiples.
  [g03-01] EV/EBITDA median 0.330 | mean 0.501 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.012
      EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank ebitda_margin 1, ebit_margin 1, roic 1, capex_intensity 1 | k=10, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a growing-perpetuity view EV/EBITDA is roughly (1 - reinvestment rate)/(WACC - g), so peers need both the same discount rate and the same growth regime. A 2-digit sector screen anchors cost of capital and cyclicality, a hard growth band puts peers in the same growth regime, and ranking on EBITDA and EBIT margins, ROIC and capex intensity matches how much of EBITDA must be reinvested to deliver that growth.
  [g01-03] EV/EBITDA median 0.335 | mean 0.469 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.045
      EV/EBITDA | rank roic 1, sales_growth_1y 1, capex_intensity 1, rnd_intensity 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=20, trimmed_mean, min_peers=3
      mechanism: Valuation theory says EV/EBITDA depends on growth, profitability of reinvestment, reinvestment needs, intangible investment and leverage-related risk, not on the SIC code itself. Picking the nearest firms across all industries on these drivers is a nonparametric version of the warranted-multiple approach that avoids imposing a linear functional form, and a trimmed mean guards against outlier peers.
  [g02-02] EV/EBITDA median 0.336 | mean 0.493 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.021
      EV/EBITDA | screen band sales_growth_1y±0.08 | rank roic 1, capex_intensity 1, rnd_intensity 1, log_assets 0.5, ebitda_margin 0.5 | k=15, median, min_peers=8 | fallback [band sales_growth_1y±0.16] -> []
      mechanism: In a growing-perpetuity view the EV/EBITDA multiple is most sensitive to expected growth, so a hard band on recent sales growth forces peers into the same growth regime regardless of SIC code. Within that band, ROIC, capex intensity and R&D intensity determine how much of EBITDA must be reinvested to deliver the growth, and size proxies for risk, so the nearest firms on these should share the multiple.
  [g03-03] EV/EBITDA median 0.339 | mean 0.525 | coverage 100.0% | beats industry 1/4 yrs | gain vs industry -0.012
      EV/EBITDA | screen same industry_l3 | rank gross_margin 1, asset_turnover 1, ebit_margin 1, sales_growth_1y 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, firms differ in where they sit on the value chain: branded or proprietary producers have high gross margins and low asset turnover, while commodity processors and distributors have thin margins and fast turnover, and these positions carry different durability of EBITDA and hence different multiples. Matching gross margin, asset turnover and EBIT margin inside the industry, plus growth, picks peers with the same business model rather than just the same product code.
  [g01-02] EV/EBITDA median 0.343 | mean 0.534 | coverage 98.8% | beats industry 0/4 yrs | gain vs industry -0.022
      EV/EBITDA | screen same industry_l4 | rank log_sales 1, sales_growth_1y 0.5 | k=6, harmonic_mean, min_peers=4 | fallback [same industry_l3] -> [same industry_l2]
      mechanism: The narrowest industry definition gives peers with the most similar products, customers and cyclicality, and similar size proxies for similar business risk and liquidity. The harmonic mean of multiples equals averaging earnings yields, which is less dominated by a few peers with temporarily depressed EBITDA and very high multiples, a known source of upward bias with the arithmetic mean.
  [g01-05] EV/Sales median 0.378 | mean 0.541 | coverage 90.8% | beats industry 4/4 yrs | gain vs industry +0.255
      EV/Sales | screen band ebitda_margin±0.03 | rank sales_growth_1y 1, gross_margin 1, capex_intensity 1, log_sales 0.5 | k=15, median, min_peers=8 | fallback [band ebitda_margin±0.06]
      mechanism: Because a dollar of sales is worth roughly the cash margin it produces capitalized at a growth-adjusted rate, firms with nearly the same EBITDA margin should have similar EV/Sales regardless of industry. A hard margin band enforces this, and ranking within the band on growth, gross margin and capex intensity matches the remaining drivers (growth and how much of the margin is eaten by reinvestment).
  [g01-06] EV/Sales median 0.384 | mean 0.581 | coverage 92.0% | beats industry 4/4 yrs | gain vs industry +0.232
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, rnd_intensity 0.5 | k=6, harmonic_mean, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03]
      mechanism: Combining the same 3-digit industry (shared risk and business model) with a margin band (shared cash conversion of sales) targets the two main determinants of the sales multiple at once. Within that set, gross margin, growth and R&D intensity capture pricing power and intangible investment, and the harmonic mean limits the influence of high-multiple peers.
  [g02-04] EV/Sales median 0.423 | mean 0.687 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.260
      EV/Sales | screen band ebitda_margin±0.04 | rank rnd_intensity 1.5, sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.08] -> []
      mechanism: Expensed R&D depresses reported EBITDA margin even though it is an investment, so R&D-heavy firms carry higher EV/Sales than their EBITDA margin suggests. Banding on EBITDA margin and then ranking on R&D intensity matches the economic (pre-R&D) margin, while growth, ROIC and capex intensity match the remaining capitalization and reinvestment drivers of the sales multiple.
  [g02-06] EV/Sales median 0.425 | mean 0.657 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.288
      EV/Sales | screen band gross_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 0.5, asset_turnover 0.5 | k=10, median, min_peers=6 | fallback [band gross_margin±0.1] -> []
      mechanism: Gross margin reflects pricing power and business model (software vs. distribution), which sets the long-run attainable operating margin; firms in the same gross-margin band but with lower current EBITDA margin are often scaling and are valued on future margins. Banding on gross margin and ranking on EBITDA margin, growth and size matches both the business-model ceiling and the current position toward it.
  [g03-04] EV/Sales median 0.430 | mean 0.631 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.315
      EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.1 | rank capex_intensity 1, rnd_intensity 1, roic 1, log_sales 0.5 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales is approximately the cash margin of a dollar of sales times a growth-dependent capitalization factor, so the two first-order drivers are margin and growth. A joint hard band on EBITDA margin and sales growth matches both factors directly across industries, and ranking on capex intensity, R&D intensity, ROIC and size matches reinvestment needs and risk, with fallbacks that relax growth first because margin matters most for the sales multiple.
  [g03-05] EV/Sales median 0.447 | mean 0.682 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.265
      EV/Sales | screen band ebit_margin±0.03 | rank ebitda_margin 1, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=12, trimmed_mean, min_peers=6 | fallback [band ebit_margin±0.06] -> []
      mechanism: Depreciation and amortization approximate the reinvestment needed to sustain the asset base, so EBIT margin is closer than EBITDA margin to the sustainable free-cash margin per dollar of sales that the sales multiple capitalizes. Banding on EBIT margin and then ranking on EBITDA margin (which jointly pins down D&A intensity), gross margin, growth and R&D intensity matches cash conversion, pricing power and expensed intangible investment.
  [g01-04] EV/Sales median 0.474 | mean 0.771 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.174
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales is approximately EBITDA margin times EV/EBITDA, so margin differences explain most of the spread in sales multiples even inside an industry. Restricting to the 2-digit sector keeps risk and cyclicality broadly similar while giving enough candidates to find peers with nearly the same EBITDA and gross margin and similar growth.
  [g02-05] EV/Sales median 0.539 | mean 0.755 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.192
      EV/Sales | rank ebitda_margin 4, ebit_margin 2, sales_growth_1y 1, capex_intensity 1, roic 1 | k=10, median, min_peers=3
      mechanism: EV/Sales is approximately EBITDA margin times EV/EBITDA, so the dominant matching variable is margin, but a hard band loses firms; a heavily weighted soft distance on EBITDA and EBIT margin keeps full coverage while still forcing close margin matches. Secondary weights on growth, capex intensity and ROIC match the EV/EBITDA component (growth and reinvestment efficiency), across all industries.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g02-03] rejected: critic: The mechanism is about margins that are temporarily depressed relative to a firm's own normal level, but the recipe only matches current-level margins and ROE, which cannot tell a transitory d
  [g03-06] rejected: critic: This is essentially g01-06 with its own first fallback (same industry_l2 plus an EBITDA-margin band) promoted to the primary screen; the 'sector anchors the discount rate inside a margin band'

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

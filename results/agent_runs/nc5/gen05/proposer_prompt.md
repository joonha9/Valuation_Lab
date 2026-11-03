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
  [g04-02] EV/EBITDA median 0.305 | mean 0.473 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.040
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, sales_growth_1y 0.7, ebitda_margin 0.6, gross_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.4 | k=12, median, min_peers=8 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share production technology, demand cycles and therefore discount rates and terminal growth; when enough exist, ranking them on reinvestment, growth, moat (gross and EBITDA margin), leverage and size should remove the residual differences more precisely than 2-digit peers. Falling back to 2-digit peers keeps coverage in thin industries.
  [g04-03] EV/EBITDA median 0.306 | mean 0.472 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.042
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 0.7, gross_margin 0.7, ebitda_margin 0.6, net_debt_to_ebitda 0.5, log_sales 0.4, asset_turnover 0.3 | k=12, median, min_peers=5 | fallback []
      mechanism: Beyond capex, the capital tied up per dollar of sales (asset turnover, including working capital) determines how much EBITDA growth costs in reinvestment, so capital-light firms deserve higher EV/EBITDA. Giving gross margin more weight as the pricing-power proxy and adding asset turnover to the best 2-digit-industry driver set should better align cash conversion and persistence.
  [g03-02] EV/EBITDA median 0.307 | mean 0.470 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.040
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 0.7, ebitda_margin 0.6, gross_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.4 | k=12, median, min_peers=5
      mechanism: Gross margin proxies for pricing power and the durability of a competitive advantage, which lengthens the period of excess returns and raises EV/EBITDA, while capex intensity measures the reinvestment that EBITDA does not deduct. Matching 2-digit industry peers on reinvestment, growth, moat (gross and EBITDA margin), leverage and size should align both the cash-flow conversion and the persistence components of the multiple.
  [g04-01] EV/EBITDA median 0.309 | mean 0.475 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.039
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, sales_growth_1y 0.7, ebitda_margin 0.6, gross_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.4, rnd_intensity 0.3 | k=15, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA is set by how much EBITDA converts to free cash flow (capex intensity), by growth, by the durability of excess returns (gross and EBITDA margin) and by risk (leverage, size). R&D is expensed, so high-R&D firms carry EBITDA that understates long-run cash flow; adding it to the best 2-digit-industry driver set and keeping 15 peers lowers the sampling noise of the peer median.
  [g03-01] EV/EBITDA median 0.312 | mean 0.477 | coverage 98.2% | beats industry 4/4 yrs | gain vs industry +0.033
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, ebitda_margin 0.8, sales_growth_1y 0.7, net_debt_to_ebitda 0.5, log_sales 0.4, rnd_intensity 0.3 | k=15, median, min_peers=5
      mechanism: EV/EBITDA is driven by how much EBITDA converts to free cash flow (capex intensity), by growth, and by risk (leverage, size), with EBITDA margin capturing durability of earnings. Using the same 2-digit industry driver set as the best prior recipe but keeping 15 nearest peers reduces the sampling noise of a small-sample median, while R&D intensity flags expensed intangible investment that depresses current EBITDA relative to long-run cash flow.
  [g03-03] EV/EBITDA median 0.314 | mean 0.478 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.036
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, ebitda_margin 0.8, sales_growth_1y 0.7, net_debt_to_ebitda 0.5, log_sales 0.4 | k=10, median, min_peers=8 | fallback [same industry_l2] -> []
      mechanism: Narrow 3-digit industry peers share production technology and demand cycles, so if enough exist they should give tighter discount-rate and growth alignment; ranking them on capex intensity, margin, growth, leverage and size removes the remaining cash-conversion and risk differences. The median (not trimmed mean) is robust to the outlier multiples that hurt the earlier L3 attempt, and the L2 fallback preserves coverage in thin industries.
  [g02-04] EV/EBITDA median 0.319 | mean 0.481 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.033
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, ebitda_margin 0.8, sales_growth_1y 0.7, net_debt_to_ebitda 0.5, log_sales 0.4 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/EBITDA depends on how much EBITDA converts to free cash flow (capex intensity), on growth, and on risk (leverage, size). Adding EBITDA margin captures competitive position and durability of earnings, so 2-digit industry peers matched on all of these should share both the cash-conversion and the risk components of the multiple.
  [g01-03] EV/EBITDA median 0.325 | mean 0.489 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank ebitda_margin 1, roic 0.8, sales_growth_1y 0.6 | k=8, median, min_peers=4 | fallback [same industry_l2] -> [band log_sales±1]
      mechanism: Size proxies for risk, diversification and liquidity premia, so similar-size peers in the same broad industry share discount rates. Within that size band, matching on EBITDA margin and ROIC aligns profitability durability and competitive position, which drive the persistence of EBITDA.
  [g01-02] EV/EBITDA median 0.325 | mean 0.491 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 0.7, log_assets 0.4 | k=10, median, min_peers=5 | fallback []
      mechanism: EBITDA ignores capital intensity, so firms that must reinvest more of EBITDA in capex deserve lower EV/EBITDA; leverage proxies for risk and financial distress. Matching within a 2-digit industry on capex intensity, net debt/EBITDA and growth captures the conversion of EBITDA to free cash flow and its risk.
  [g02-06] EV/EBITDA median 0.330 | mean 0.506 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.008
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 1, net_debt_to_ebitda 0.7, sales_growth_1y 0.7, ebitda_margin 0.4 | k=8, trimmed_mean, min_peers=6 | fallback [same industry_l2] -> []
      mechanism: Firms in the same 3-digit industry share production technology and demand drivers, so their EV/EBITDA differences mostly reflect capital needs, leverage risk and growth. Ranking narrow-industry peers on capex intensity, net debt/EBITDA and growth, with a trimmed mean to limit outlier multiples, should improve on the plain L3 industry median while falling back to L2 when peers are scarce.
  [g01-01] EV/EBITDA median 0.333 | mean 0.512 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.002
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, log_sales 0.5 | k=8, harmonic_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Under a constant-growth DCF, EV/EBITDA rises with expected growth and with return on capital (lower reinvestment needed per unit of growth). Within a 3-digit industry, peers closest on recent growth and ROIC should share discount rates and value-driver economics, and the harmonic mean limits the upward bias of averaging ratios with a price numerator.
  [g02-05] EV/EBITDA median 0.333 | mean 0.497 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.017
      EV/EBITDA | screen same industry_l2, band log_sales±1.5 | rank roic 1, capex_intensity 0.8, sales_growth_1y 0.6, rnd_intensity 0.4 | k=10, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: In a growing-perpetuity model, EV/EBITDA rises with growth and with return on invested capital because high-ROIC firms need less reinvestment per unit of growth; capex intensity measures that reinvestment directly. Restricting to similar-size firms in the same broad industry aligns discount rates, and R&D intensity flags intangible investment not captured by capex.
  [g03-06] EV/Sales median 0.384 | mean 0.575 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.263
      EV/Sales | screen band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 0.6, asset_turnover 0.4 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.06] -> [band ebitda_margin±0.12]
      mechanism: Since EV/Sales scales nearly linearly with operating margin, a very tight margin band (plus or minus 3 points) makes peers nearly identical on the dominant driver, leaving growth and reinvestment intensity to explain the residual sales multiple. Widening the band only when peers are scarce keeps the margin match as close as the cross-section allows for each firm.
  [g04-06] EV/Sales median 0.394 | mean 0.631 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.315
      EV/Sales | screen band ebitda_margin±0.02 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 0.6, asset_turnover 0.4, net_debt_to_ebitda 0.4 | k=12, median, min_peers=6 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> [band ebitda_margin±0.15] -> []
      mechanism: With a 2-point EBITDA-margin band the sales multiple of peers differs mainly through the EV/EBITDA component, which depends on growth, reinvestment (capex intensity, asset turnover) and the discount rate (net leverage). Matching on these within the tightest band the cross-section allows, widening only when peers are scarce, should align both the margin and the multiple applied to it.
  [g04-05] EV/Sales median 0.397 | mean 0.617 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.330
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 0.6, gross_margin 0.4, log_sales 0.3 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> [band ebitda_margin±0.12] -> []
      mechanism: Margin explains most of EV/Sales, while a shared 2-digit industry adds common cyclicality, risk and terminal-growth expectations. Requiring same-industry peers within a tight 3-point margin band, and falling back to a pure cross-industry tight band and then wider bands when the industry is thin, combines both sources of similarity without sacrificing margin closeness.
  [g01-05] EV/Sales median 0.401 | mean 0.664 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.281
      EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.7, asset_turnover 0.5 | k=12, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Because EV/Sales scales almost linearly with operating margin, firms with similar EBITDA margins and growth should trade at similar sales multiples even across industries. A tight margin band plus ranking on margin, growth and asset turnover selects economically similar cash-flow generators from the full cross-section, giving larger and closer peer sets than industry codes.
  [g04-04] EV/Sales median 0.402 | mean 0.633 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.313
      EV/Sales | screen band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 0.6, asset_turnover 0.4 | k=10, median, min_peers=6 | fallback [band ebitda_margin±0.06] -> [band ebitda_margin±0.12] -> []
      mechanism: EV/Sales scales nearly linearly with operating margin, so a plus-or-minus 3 point EBITDA-margin band makes peers nearly identical on the dominant driver, leaving growth, reinvestment and capital intensity to explain the residual. Progressively widening the band and ending with an unscreened ranked fallback keeps the closest-margin match available for every firm instead of dropping firms with extreme margins.
  [g02-02] EV/Sales median 0.405 | mean 0.629 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.317
      EV/Sales | screen same industry_l2, band ebitda_margin±0.08 | rank ebitda_margin 2, sales_growth_1y 1, asset_turnover 0.5 | k=8, median, min_peers=5 | fallback [band ebitda_margin±0.05] -> []
      mechanism: Margin explains most of EV/Sales, but industry membership adds shared risk, cyclicality and terminal-growth expectations. Requiring peers to share a 2-digit SIC code and lie within a moderate EBITDA-margin band combines both sources of similarity, falling back to a pure cross-industry margin band when the industry is thin.
  [g03-05] EV/Sales median 0.413 | mean 0.618 | coverage 93.6% | beats industry 4/4 yrs | gain vs industry +0.219
      EV/Sales | screen same industry_l2, band ebitda_margin±0.06 | rank ebitda_margin 2, sales_growth_1y 1, capex_intensity 0.5, log_sales 0.4 | k=10, harmonic_mean, min_peers=5 | fallback [band ebitda_margin±0.05] -> [band ebitda_margin±0.1]
      mechanism: Industry membership adds shared cyclicality, risk and terminal-growth expectations on top of margin, which earlier gave the best mean error, while the harmonic mean gave the best median error. Combining a 2-digit industry screen and a margin band with ranking on margin, growth, capex intensity and size, and falling back to a pure cross-industry margin band in thin industries, should capture both sources of similarity.
  [g02-03] EV/Sales median 0.414 | mean 0.618 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.328
      EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=20, median, min_peers=6 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Among firms with similar EBITDA margins, the sales multiple still depends on the discount rate applied to those cash flows. Net leverage and firm size proxy for financial risk and for liquidity and diversification premia, so matching on them within a margin band should align discount rates as well as profitability.
  [g03-04] EV/Sales median 0.431 | mean 0.718 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.228
      EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.6, capex_intensity 0.6, net_debt_to_ebitda 0.4 | k=15, harmonic_mean, min_peers=6 | fallback [band ebitda_margin±0.1] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so a tight cross-industry margin band removes most dispersion; what remains is the EV/EBITDA component, driven by growth, reinvestment needs (capex intensity) and risk (net leverage). Adding capex intensity and leverage to the margin-growth ranking aligns the cash conversion and discount rate of those margins, and the harmonic mean limits upward bias from averaging price ratios.
  [g02-01] EV/Sales median 0.450 | mean 0.722 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.224
      EV/Sales | screen band ebitda_margin±0.04 | rank ebitda_margin 2, sales_growth_1y 1, gross_margin 0.7, rnd_intensity 0.6 | k=15, harmonic_mean, min_peers=6 | fallback [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so firms with near-identical margins share most of the sales-multiple variation regardless of industry. Within that margin band, growth and R&D intensity capture the remaining value driver: R&D is expensed, so high-R&D firms carry depressed current margins relative to their long-run cash-flow potential and trade at higher sales multiples than their reported margin suggests.
  [g01-04] EV/Sales median 0.474 | mean 0.774 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.171
      EV/Sales | screen same industry_l2 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 0.8 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so the dominant cross-sectional driver of EV/Sales is profitability. Ranking 2-digit industry peers primarily on EBITDA margin, then gross margin and growth, should remove most of the margin-driven dispersion that plagues industry-median EV/Sales.
  [g01-06] EV/Sales median 0.507 | mean 0.826 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.117
      EV/Sales | screen same industry_l3 | rank ebitda_margin 2, asset_turnover 0.8, roic 0.6, sales_growth_1y 0.6 | k=6, trimmed_mean, min_peers=4 | fallback [same industry_l2] -> [band ebitda_margin±0.07]
      mechanism: Within a narrow 3-digit industry, business models are similar, but margin and capital intensity still vary; EV/Sales rises with margin and falls with the capital (low asset turnover) needed to support sales. Matching on EBITDA margin, asset turnover and ROIC with a trimmed mean captures both levers while limiting outlier peers.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

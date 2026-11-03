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
  [g03-01] EV/EBITDA median 0.307 | mean 0.453 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.061
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, ebitda_margin 0.5, log_sales 0.5 | k=30, trimmed_mean, min_peers=3
      mechanism: Growth, return on capital, reinvestment, intangibles, leverage, margin durability and size jointly set the rate at which the market capitalizes EBITDA. Matching on all eight drivers picks fundamentally similar firms, and a wide k=30 neighborhood aggregated with a trimmed mean averages out peer-specific mispricing while discarding multiples inflated by temporarily depressed EBITDA.
  [g04-01] EV/EBITDA median 0.310 | mean 0.449 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.065
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, ebitda_margin 0.5, log_sales 0.5, ebit_margin 0.5 | k=30, trimmed_mean, min_peers=3
      mechanism: Two firms with the same EBITDA but different depreciation burdens do not generate the same free cash flow: a large gap between EBITDA and EBIT margin signals heavy asset replacement needs, which lowers the rate at which EBITDA is capitalized. Adding EBIT margin to the eight proven growth, return, reinvestment, intangible, leverage, margin and size drivers matches peers on how much of EBITDA survives as sustainable operating profit.
  [g04-02] EV/EBITDA median 0.313 | mean 0.454 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.059
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, ebitda_margin 0.5, log_sales 0.5, asset_turnover 0.5, debt_to_assets 0.5 | k=30, trimmed_mean, min_peers=3
      mechanism: Asset turnover measures how much capital a firm needs per dollar of sales and debt-to-assets measures balance-sheet risk; both affect free-cash-flow conversion and the cost of capital beyond what capex intensity and net debt/EBITDA capture. Matching on them alongside the eight proven drivers, with a wide trimmed-mean neighborhood, should pick peers with similar capital needs and risk.
  [g02-02] EV/EBITDA median 0.315 | mean 0.461 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.052
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5 | k=30, trimmed_mean, min_peers=3
      mechanism: The same growth, return, reinvestment and leverage drivers set EV/EBITDA, but each peer's multiple contains firm-specific pricing noise. A larger neighborhood (k=30) with a trimmed mean averages out idiosyncratic mispricing while discarding the extreme multiples that come from temporarily depressed EBITDA.
  [g02-01] EV/EBITDA median 0.315 | mean 0.460 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.054
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, ebitda_margin 0.5, log_sales 0.5 | k=20, median, min_peers=3
      mechanism: Building on the best global EV/EBITDA rule, adding EBITDA margin and size captures two further drivers of capitalization rates: high-margin firms tend to have more durable pricing power, and larger firms carry lower risk and liquidity discounts. Peers matched on growth, ROIC, reinvestment, intangibles, leverage, margin and size should share both cash-flow profile and discount rate.
  [g01-05] EV/EBITDA median 0.318 | mean 0.467 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.047
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5 | k=20, median, min_peers=3
      mechanism: Firms with similar growth, ROIC, reinvestment needs, intangible intensity and leverage have similar cash-flow profiles and risk, so they should capitalize EBITDA at similar rates whatever their SIC code. Using more peers (k=20) cuts noise from any single mispriced comparable.
  [g03-03] EV/EBITDA median 0.318 | mean 0.470 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.044
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, debt_to_assets 0.5, log_assets 0.5 | k=25, median, min_peers=3
      mechanism: Discount rates depend on financial risk and size: highly levered firms carry more equity risk and distress cost, and larger asset bases are associated with lower risk and liquidity discounts. Adding debt-to-assets and asset size to the growth, return, reinvestment and intangible drivers selects peers with both similar cash-flow profiles and similar cost of capital.
  [g04-03] EV/EBITDA median 0.319 | mean 0.478 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.035
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5, ebitda_margin 0.5, log_sales 0.5 | k=30, trimmed_mean, min_peers=15 | fallback []
      mechanism: Industry membership captures shared cyclicality and systematic risk that accounting ratios miss, but earlier industry rules used too few peers and too few drivers. Restricting to the same 2-digit industry and then taking the 30 nearest on the eight proven drivers with a trimmed mean tests whether common risk exposure adds information once noise is averaged out; thin industries fall back to the whole market.
  [g02-03] EV/EBITDA median 0.323 | mean 0.482 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.031
      EV/EBITDA | screen band sales_growth_1y±0.1 | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5 | k=20, median, min_peers=5 | fallback [band sales_growth_1y±0.25] -> []
      mechanism: Expected growth is the single largest driver of EV/EBITDA in a constant-growth model, and z-score distance can trade a large growth gap against small gaps elsewhere. A hard band on 1-year sales growth guarantees every peer is in the same growth regime, and ranking within it on ROIC, reinvestment, intangibles and leverage then matches cash conversion and risk.
  [g01-04] EV/EBITDA median 0.329 | mean 0.511 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry +0.003
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 0.5 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Close industry peers share technology, cyclicality and risk, and within that group growth and return on capital separate high- from low-multiple firms. The harmonic mean averages earnings yields rather than multiples, so a few very high-multiple peers do not pull the estimate up.
  [g01-01] EV/EBITDA median 0.330 | mean 0.499 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.014
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 1, roic 1, capex_intensity 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: In a constant-growth model EV/EBITDA rises with expected growth and with the share of EBITDA that turns into free cash flow (high ROIC, low reinvestment). Peers in the same 2-digit industry that match on growth, ROIC and capex intensity should share discount-rate exposure and cash conversion, so they should trade at similar EBITDA multiples.
  [g03-02] EV/EBITDA median 0.339 | mean 0.502 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.012
      EV/EBITDA | rank sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, net_debt_to_ebitda 0.5 | k=30, harmonic_mean, min_peers=3
      mechanism: Averaging EBITDA yields (the harmonic mean of multiples) rather than multiples treats peer valuations the way a capitalization rate would, so a few peers with very high multiples from near-zero EBITDA cannot pull the estimate up. Peers matched on growth, ROIC, reinvestment, intangibles and leverage across the whole market share cash conversion and risk.
  [g01-06] EV/Sales median 0.391 | mean 0.672 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.272
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: A hard band on EBITDA margin makes sure every peer has nearly the same profit per dollar of sales, so the target's sales multiple is not inferred from firms with a different margin. Ranking those peers on gross margin, growth and size then picks firms with a similar cost structure and growth outlook.
  [g04-05] EV/Sales median 0.391 | mean 0.663 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.281
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, ebit_margin 1, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> [same industry_l2]
      mechanism: At the same EBITDA margin, a firm with heavier depreciation must reinvest more to sustain sales and converts less of each dollar into free cash flow, so it deserves a lower sales multiple. Ranking banded same-industry peers on EBIT margin as well as EBITDA margin, gross margin, growth and size matches both profitability and the capital burden behind it.
  [g02-05] EV/Sales median 0.391 | mean 0.663 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.281
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> [same industry_l2]
      mechanism: Same-industry peers share technology and cyclicality, and a tight EBITDA-margin band equalizes profit per dollar of sales; ranking again on EBITDA margin inside the band selects the closest-margin peers, with gross margin, growth and size refining cost structure and risk. Fallbacks progressively relax industry before margin, since margin is the dominant driver of the sales multiple.
  [g04-04] EV/Sales median 0.391 | mean 0.663 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.281
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, rnd_intensity 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> [same industry_l2]
      mechanism: R&D is expensed, so research-intensive firms report depressed EBITDA margins relative to their economic profitability and the market pays more per dollar of sales than their reported margin implies. Adding R&D intensity to the proven industry plus EBITDA-margin-band recipe matches peers whose reported margins understate economic margins by a similar amount.
  [g03-06] EV/Sales median 0.394 | mean 0.664 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.280
      EV/Sales | screen same industry_l3, band ebitda_margin±0.04 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.03] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> [same industry_l2]
      mechanism: Closer 3-digit industry peers share products, input costs and customers more tightly than 2-digit groups, and within them an EBITDA-margin band equalizes profit per dollar of sales. Where the 3-digit group is thin, the rule relaxes to 2-digit industry with a tighter band and then to margin alone, keeping margin, the dominant sales-multiple driver, fixed throughout.
  [g03-04] EV/Sales median 0.398 | mean 0.681 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.264
      EV/Sales | screen same industry_l2, band ebitda_margin±0.02 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, roic 0.5, log_sales 0.5 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.02] -> [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.05] -> [same industry_l2]
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so pinning margin within two points removes most variation in sales multiples, while same 2-digit industry peers share cyclicality and technology. Ranking on margin, gross margin, growth, ROIC and size refines the remaining EBITDA-multiple drivers; fallbacks relax industry before margin because margin is the dominant driver.
  [g03-05] EV/Sales median 0.402 | mean 0.675 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.271
      EV/Sales | screen band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, capex_intensity 1, rnd_intensity 0.5, gross_margin 0.5, debt_to_assets 0.5 | k=30, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.06] -> []
      mechanism: Inside a tight EBITDA-margin band the sales multiple reduces to the EBITDA multiple, so the drivers that win for EV/EBITDA (growth, ROIC, reinvestment, intangibles, leverage) should also rank sales-multiple peers. A large neighborhood with a trimmed mean cuts idiosyncratic pricing noise while discarding extreme multiples.
  [g04-06] EV/Sales median 0.402 | mean 0.671 | coverage 99.9% | beats industry 4/4 yrs | gain vs industry +0.274
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04 | rank ebitda_margin 2, gross_margin 1, sales_growth_1y 1, capex_intensity 0.5, log_sales 0.5 | k=15, trimmed_mean, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> [same industry_l2]
      mechanism: Inside the same 2-digit industry and a four-point EBITDA-margin band, remaining sales-multiple differences come from growth, cost structure, reinvestment and size, plus idiosyncratic mispricing. Using 15 nearest peers with a trimmed mean, the aggregation that won for EV/EBITDA, averages out peer-specific noise while discarding extreme multiples, and capex intensity adds the reinvestment driver.
  [g02-06] EV/Sales median 0.409 | mean 0.662 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.284
      EV/Sales | screen band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, capex_intensity 0.5, gross_margin 0.5 | k=20, median, min_peers=5 | fallback [band ebitda_margin±0.1] -> []
      mechanism: Within an EBITDA-margin band, EV/Sales differences reduce to EV/EBITDA differences, which are driven by growth, return on capital and reinvestment needs. Ranking banded peers on margin, growth, ROIC and capex intensity across the whole market, with k=20 to reduce noise, mirrors the best-performing EV/EBITDA rule applied to the sales multiple.
  [g02-04] EV/Sales median 0.415 | mean 0.693 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.254
      EV/Sales | screen band ebitda_margin±0.03 | rank gross_margin 1, sales_growth_1y 1, rnd_intensity 0.5, capex_intensity 0.5, roic 0.5 | k=15, median, min_peers=5 | fallback [band ebitda_margin±0.06] -> []
      mechanism: Because EV/Sales equals EV/EBITDA times EBITDA margin, a tight margin band removes most of the cross-sectional variation in sales multiples, and SIC labels add little once profit per dollar of sales is fixed. Within the band, matching gross margin, growth, R&D and capex intensity picks firms with similar cost structure, growth and reinvestment, which drive the remaining EBITDA-multiple differences.
  [g01-02] EV/Sales median 0.474 | mean 0.771 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.174
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1 | k=8, median, min_peers=5 | fallback []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most cross-sectional variation in sales multiples comes from profitability. Within a 2-digit industry, peers with nearly the same EBITDA and gross margins (and similar growth) should carry similar sales multiples.
  [g01-03] EV/Sales median 0.540 | mean 0.761 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.185
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, rnd_intensity 1 | k=15, median, min_peers=3
      mechanism: Sales multiples are driven by margin, growth and intangible intensity more than by SIC labels, which are coarse and often stale. Matching on EBITDA margin, gross margin, growth and R&D intensity across the whole market should find economically similar firms even where the industry is thin.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}

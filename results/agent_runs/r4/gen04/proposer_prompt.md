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

ARCHIVE: your earlier graded attempts, exploration scores only (17 graded)
  [g02-05] EV/EBITDA median 0.315 | mean 0.489 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.024
      EV/EBITDA | screen same industry_l2 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=10, median, min_peers=5 | fallback []
      mechanism: Under US GAAP, R&D is expensed, so EBITDA understates the economic earnings of intangible-heavy firms and inflates their EV/EBITDA compared with tangible-asset peers in the same sector. Matching on R&D intensity and gross margin within a 2-digit sector aligns this accounting distortion, and growth and ROIC capture the remaining value drivers.
  [g03-03] EV/EBITDA median 0.320 | mean 0.493 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.020
      EV/EBITDA | screen same industry_l2, band gross_margin±0.1 | rank rnd_intensity 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: Gross margin shows the business model (commodity or processing versus branded or IP-driven). It also shows how much spending sits below gross profit in SG&A and R&D, which are expensed intangible investments that push EBITDA below economic earnings. A hard gross-margin band inside the 2-digit sector guarantees that every peer shares this cost structure. Ranking on R&D intensity, growth and ROIC then matches the remaining value drivers.
  [g01-04] EV/EBITDA median 0.322 | mean 0.490 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.023
      EV/EBITDA | screen same industry_l2 | rank sales_growth_1y 2, roic 2, net_debt_to_ebitda 1, log_sales 1 | k=10, median, min_peers=5 | fallback []
      mechanism: A Gordon-style decomposition implies EV/EBITDA rises with growth and with return on invested capital (less reinvestment needed per unit of growth) and falls with risk. Within a 2-digit sector, peers closest in sales growth, ROIC and leverage should therefore share the target's EBITDA multiple more closely than the full industry median.
  [g02-04] EV/EBITDA median 0.330 | mean 0.503 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.011
      EV/EBITDA | screen same industry_l3, band sales_growth_1y±0.1 | rank roic 1, capex_intensity 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band sales_growth_1y±0.1] -> [same industry_l2] -> []
      mechanism: Growth is the first-order driver of EV/EBITDA in a Gordon-style model, and soft ranking can still let in peers with very different growth. A hard band on 1-year sales growth inside the 3-digit industry ensures every peer is on a similar growth path. Ranking on ROIC and capex intensity then matches how much of that growth turns into free cash flow.
  [g01-05] EV/EBITDA median 0.332 | mean 0.506 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.007
      EV/EBITDA | screen same industry_l3 | rank capex_intensity 2, ebitda_margin 1, sales_growth_1y 1 | k=8, harmonic_mean, min_peers=4 | fallback [same industry_l2] -> []
      mechanism: EBITDA ignores capital expenditure, so firms that must reinvest heavily to sustain EBITDA convert less of it into free cash flow and trade at lower EV/EBITDA. Matching on capex intensity and EBITDA margin within a 3-digit industry aligns the cash conversion of EBITDA, and the harmonic mean is the unbiased average for price-scaled ratios.
  [g01-06] EV/EBITDA median 0.339 | mean 0.515 | coverage 100.0% | beats industry 1/4 yrs | gain vs industry -0.001
      EV/EBITDA | screen same industry_l4 | rank log_sales 1, log_assets 1, sales_growth_1y 1 | k=6, median, min_peers=4 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: The narrowest industry definition captures shared products, customers and regulatory risk, and among those close competitors firm size proxies for diversification, market power and lower risk, which raises the multiple. Cascading from 4-digit to 2-digit SIC keeps peers as close as the data allow while size ranking removes the scale mismatch inside small industries.
  [g02-03] EV/EBITDA median 0.349 | mean 0.496 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry +0.018
      EV/EBITDA | rank sales_growth_1y 2, roic 2, capex_intensity 1, net_debt_to_ebitda 1 | k=20, median, min_peers=3
      mechanism: In a steady-state DCF, EV/EBITDA depends on growth, on how much EBITDA must be reinvested (capex intensity, and ROIC as reinvestment efficiency), and on risk (leverage). Firms with the same growth, return, reinvestment and leverage should have similar EBITDA multiples whatever their SIC label. Dropping the industry screen gives a larger pool, so the nearest matches on these drivers can be closer.
  [g03-02] EV/EBITDA median 0.357 | mean 0.562 | coverage 100.0% | beats industry 0/4 yrs | gain vs industry -0.049
      EV/EBITDA | screen same industry_l3 | rank rnd_intensity 2, ebit_margin 1, ebitda_margin 1, capex_intensity 1 | k=8, trimmed_mean, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EBITDA leaves out two real economic costs that vary across firms: depreciation of past capital spending (the gap between EBITDA margin and EBIT margin, plus capex intensity) and R&D that is expensed rather than capitalised. Firms in the same 3-digit industry whose EBITDA carries the same D&A burden and the same R&D add-back should turn EBITDA into free cash flow at the same rate, and so trade at similar multiples. A trimmed mean keeps information from several peers while dropping extreme multiples.
  [g03-06] EV/Sales median 0.373 | mean 0.628 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.318
      EV/Sales | screen band ebitda_margin±0.03, band sales_growth_1y±0.1 | rank gross_margin 1, rnd_intensity 1, asset_turnover 1 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.03] -> [band ebitda_margin±0.06] -> []
      mechanism: Margin and growth are the two first-order drivers of the sales multiple. A tight two-way box on EBITDA margin and 1-year growth, applied across all sectors, gives peers with the same profitability and growth path from a much larger pool than any single SIC group. Within the box, gross margin, R&D intensity and asset turnover describe the business model and capital intensity directly, in place of an industry label.
  [g03-04] EV/Sales median 0.393 | mean 0.662 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.284
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank rnd_intensity 2, gross_margin 1, sales_growth_1y 1, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: EV/Sales is EV/EBITDA times EBITDA margin. A hard EBITDA-margin band within the 2-digit sector fixes the margin term. The EV/EBITDA term is then driven mostly by the R&D-expensing distortion and by growth and ROIC. Ranking on R&D intensity and gross margin (the intangible-heavy business model) together with growth and ROIC should therefore line up the second term, which the margin band alone leaves free.
  [g02-02] EV/Sales median 0.394 | mean 0.658 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.288
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank roic 2, asset_turnover 2, sales_growth_1y 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: EV/Sales can be written as (EV / invested capital) x (invested capital / sales). The first term rises with ROIC relative to the cost of capital, and the second is roughly the inverse of asset turnover. Within a 2-digit sector and an EBITDA-margin band, peers matched on ROIC and asset turnover should line up both terms of this identity, with growth as the remaining value driver.
  [g01-03] EV/Sales median 0.407 | mean 0.607 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.339
      EV/Sales | screen same industry_l3, band ebitda_margin±0.06 | rank sales_growth_1y 1, log_sales 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.06] -> [band ebitda_margin±0.04] -> []
      mechanism: A hard band on EBITDA margin forces peers to share the profitability that converts sales into value, while the 3-digit industry screen holds business model and risk roughly constant. Remaining peers are ordered by growth and size, the next most important drivers of the multiple after margin.
  [g02-06] EV/Sales median 0.408 | mean 0.598 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.348
      EV/Sales | screen same industry_l2, band ebitda_margin±0.04, band sales_growth_1y±0.15 | rank log_sales 1, capex_intensity 1 | k=6, median, min_peers=3 | fallback [same industry_l2, band ebitda_margin±0.04] -> [band ebitda_margin±0.04, band sales_growth_1y±0.15] -> []
      mechanism: The two first-order drivers of the sales multiple are profitability (margin) and growth, so both are set as hard bands inside the 2-digit sector rather than traded off in a distance metric. Among the survivors, size and capex intensity proxy for risk and reinvestment needs. The cascade loosens the growth band first, because margin explains more of EV/Sales.
  [g03-05] EV/Sales median 0.418 | mean 0.707 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.239
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank capex_intensity 2, sales_growth_1y 2, roic 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> []
      mechanism: In a DCF, EV/Sales equals the present value of future free-cash-flow margins. FCF margin is roughly EBITDA margin less capex intensity (after tax), growing at the firm's growth rate. A hard EBITDA-margin band, then ranking on capex intensity and sales growth, matches peers on FCF margin and its growth rate directly. ROIC captures how long that growth can create value.
  [g02-01] EV/Sales median 0.418 | mean 0.678 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.268
      EV/Sales | screen band ebitda_margin±0.04 | rank gross_margin 2, sales_growth_1y 1, rnd_intensity 1 | k=12, median, min_peers=5 | fallback [band ebitda_margin±0.08] -> []
      mechanism: EV/Sales is roughly EV/EBITDA times EBITDA margin, so a tight margin band removes the main source of dispersion without needing an SIC label. Among firms with the same margin, gross margin and R&D intensity show the business model (asset-light or intangible-heavy versus commodity), which affects how durable and how fast-growing the margin is. These traits describe the economics more directly than the SIC code does.
  [g01-02] EV/Sales median 0.419 | mean 0.659 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.287
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, asset_turnover 1 | k=15, median, min_peers=3
      mechanism: With no industry screen, peers are chosen purely on the economic drivers of the sales multiple: profitability (EBITDA and gross margin), growth, and capital intensity (asset turnover, which proxies reinvestment needs). Firms with the same margin, growth and asset-intensity profile should command similar EV/Sales regardless of SIC label, and a larger pool lets the nearest matches be closer.
  [g01-01] EV/Sales median 0.552 | mean 0.806 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.139
      EV/Sales | screen same industry_l2 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback []
      mechanism: EV/Sales is approximately EV/EBITDA times EBITDA margin, so most of the cross-sectional spread in sales multiples comes from differences in profitability. Within a 2-digit sector (similar cost structure and risk), peers with the closest EBITDA margin and growth should have the closest sales multiple.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g03-01] rejected: critic: This is essentially g02-05 (same L2 screen, same rnd/gross-margin/growth/ROIC ranking) with net_debt_to_ebitda pasted in from g01-04 plus a growth-weight and k tweak, so the 'combine both' ide

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object
A near-copy of an archived recipe (e.g. only k or a weight changed slightly) will be rejected by
an independent referee, who sees your mechanism but no scores.

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}
